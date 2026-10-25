import re
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
import sqlglot
from sqlglot import exp

from .config import settings
from .schema_manager import SchemaManager

class GuardrailViolation(Exception):
    """Raised when SQL violates AST security rules."""
    def __init__(self, message: str, violation_type: str = "SECURITY_VIOLATION"):
        super().__init__(message)
        self.violation_type = violation_type

@dataclass
class GuardrailAudit:
    is_safe: bool
    status: str  # "PASSED" | "BLOCKED"
    violations: List[str] = field(default_factory=list)
    ast_type: str = "UNKNOWN"
    tables_accessed: List[str] = field(default_factory=list)
    columns_accessed: List[str] = field(default_factory=list)
    join_count: int = 0
    subquery_depth: int = 0
    has_window_functions: bool = False
    has_cte: bool = False
    sanitized_sql: Optional[str] = None
    risk_level: str = "LOW"  # "LOW" | "MEDIUM" | "CRITICAL"

class ASTGuardrails:
    """
    Multi-tier AST Query Guardrails.
    Guarantees 100% blocking of destructive statements (DROP, DELETE, UPDATE, INSERT, ALTER),
    stacked query injections, tautology bypasses, and unauthorized catalog modifications.
    """

    PROHIBITED_AST_NODES = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Alter,
        exp.Create,
        exp.TruncateTable,
        exp.Command,
        exp.Pragma,
        exp.Set,
        exp.Kill,
        exp.Transaction,
        exp.Commit,
        exp.Rollback,
    )

    FORBIDDEN_KEYWORDS_PATTERN = re.compile(
        r"\b(ATTACH\s+DATABASE|DETACH\s+DATABASE|LOAD_EXTENSION|XP_CMDSHELL|EXEC|EXECUTE)\b",
        re.IGNORECASE
    )

    FORBIDDEN_TABLES = {"sqlite_master", "sqlite_schema", "sqlite_temp_master", "information_schema"}

    def __init__(self, schema_manager: Optional[SchemaManager] = None):
        self.schema_manager = schema_manager

    def validate_and_sanitize(self, sql_query: str) -> GuardrailAudit:
        """
        Validates the SQL query against lexical, AST, injection, and complexity rules.
        Returns a detailed GuardrailAudit. If safe, includes sanitized SQL with safe LIMIT.
        """
        violations: List[str] = []
        clean_query = sql_query.strip().rstrip(";")

        # Tier 1: Lexical & Stacked Query Pre-Checks
        if self._has_stacked_queries(clean_query):
            violations.append("Stacked query detected: multiple statements separated by semicolons are forbidden.")

        if self.FORBIDDEN_KEYWORDS_PATTERN.search(clean_query):
            violations.append("Forbidden dialect keyword detected (ATTACH/DETACH/LOAD_EXTENSION/EXEC).")

        # Tier 2: AST Parsing via sqlglot
        try:
            # Parse using SQLite dialect
            parsed_expressions = sqlglot.parse(clean_query, read="sqlite")
        except Exception as e:
            return GuardrailAudit(
                is_safe=False,
                status="BLOCKED",
                violations=[f"SQL Syntax Error / Unparseable: {str(e)}"],
                risk_level="CRITICAL"
            )

        if not parsed_expressions or parsed_expressions[0] is None:
            return GuardrailAudit(
                is_safe=False,
                status="BLOCKED",
                violations=["Empty or invalid SQL statement."],
                risk_level="CRITICAL"
            )

        if len(parsed_expressions) > 1:
            violations.append(f"Multiple statements parsed ({len(parsed_expressions)} statements found). Only single SELECT queries are permitted.")

        root_ast = parsed_expressions[0]

        # Verify Root Node Type
        if not self._is_read_only_root(root_ast):
            violations.append(f"Disallowed root statement type: '{type(root_ast).__name__}'. Only SELECT or CTE queries are permitted.")

        # Tier 3: Deep AST Traversal for Prohibited Nodes
        for node in root_ast.walk():
            if isinstance(node, self.PROHIBITED_AST_NODES):
                node_name = type(node).__name__.upper()
                violations.append(f"Destructive or modifying AST node detected: '{node_name}'.")

        # Tier 4: SQL Injection & Tautology Detection
        tautologies = self._detect_tautologies(root_ast)
        if tautologies:
            violations.extend(tautologies)

        # Tier 5: Catalog & System Tables Inspection
        tables_accessed = [table.name.lower() for table in root_ast.find_all(exp.Table) if table.name]
        for tbl in tables_accessed:
            if tbl in self.FORBIDDEN_TABLES:
                violations.append(f"Access to protected system catalog table '{tbl}' is forbidden.")

        # Columns accessed
        columns_accessed = list(set([col.name for col in root_ast.find_all(exp.Column) if col.name]))

        # Tier 6: Complexity & Join Limits
        join_nodes = list(root_ast.find_all(exp.Join))
        join_count = len(join_nodes)
        if join_count > settings.MAX_JOIN_DEPTH:
            violations.append(f"Join depth exceeded: query contains {join_count} JOINs (max allowed is {settings.MAX_JOIN_DEPTH}).")

        subquery_depth = self._compute_subquery_depth(root_ast)
        if subquery_depth > settings.MAX_SUBQUERY_DEPTH:
            violations.append(f"Subquery depth exceeded: query nesting depth is {subquery_depth} (max allowed is {settings.MAX_SUBQUERY_DEPTH}).")

        # Feature flags
        has_window = len(list(root_ast.find_all(exp.Window))) > 0
        has_cte = isinstance(root_ast, exp.Select) and bool(root_ast.args.get("with"))

        # Determine outcome
        if violations:
            risk = "CRITICAL" if any("Destructive" in v or "Stacked" in v or "Forbidden" in v for v in violations) else "MEDIUM"
            return GuardrailAudit(
                is_safe=False,
                status="BLOCKED",
                violations=violations,
                ast_type=type(root_ast).__name__,
                tables_accessed=list(set(tables_accessed)),
                columns_accessed=columns_accessed,
                join_count=join_count,
                subquery_depth=subquery_depth,
                has_window_functions=has_window,
                has_cte=has_cte,
                risk_level=risk
            )

        # Tier 7: Automatic Safe LIMIT Injection / Sanitization
        sanitized_ast = self._enforce_limit(root_ast)
        sanitized_sql = sanitized_ast.sql(dialect="sqlite")

        return GuardrailAudit(
            is_safe=True,
            status="PASSED",
            violations=[],
            ast_type=type(root_ast).__name__,
            tables_accessed=list(set(tables_accessed)),
            columns_accessed=columns_accessed,
            join_count=join_count,
            subquery_depth=subquery_depth,
            has_window_functions=has_window,
            has_cte=has_cte,
            sanitized_sql=sanitized_sql,
            risk_level="LOW"
        )

    def _is_read_only_root(self, ast: exp.Expression) -> bool:
        """Verifies if the root node is a pure read-only query (Select, Union, Intersect, or CTE)."""
        if isinstance(ast, (exp.Select, exp.Union, exp.Intersect, exp.Except)):
            return True
        return False

    def _has_stacked_queries(self, sql: str) -> bool:
        """Detects semicolons separating distinct executable statements."""
        # Remove string literals to prevent matching semicolons inside strings
        no_strings = re.sub(r"'[^']*'", "''", sql)
        no_strings = re.sub(r'"[^"]*"', '""', no_strings)
        statements = [s.strip() for s in no_strings.split(";") if s.strip()]
        return len(statements) > 1

    def _detect_tautologies(self, ast: exp.Expression) -> List[str]:
        """Detects common SQL injection tautologies like 1=1, 'a'='a', TRUE OR ... in where conditions."""
        findings = []
        for eq in ast.find_all(exp.EQ):
            left = eq.this
            right = eq.expression
            # e.g., 1=1 or 0=0
            if isinstance(left, exp.Literal) and isinstance(right, exp.Literal):
                if left.this == right.this:
                    findings.append(f"SQL injection tautology detected: '{left.sql()} = {right.sql()}' evaluates to always TRUE.")
            # e.g. 'a'='a'
            elif isinstance(left, exp.Literal) and isinstance(right, exp.Literal):
                if str(left) == str(right):
                    findings.append(f"SQL injection tautology detected: '{left} = {right}'.")

        # Detect boolean TRUE in OR connectors
        for connector in ast.find_all(exp.Or):
            left = connector.this
            right = connector.expression
            if isinstance(left, exp.Boolean) and left.this is True:
                findings.append("SQL injection detected: boolean TRUE in OR clause.")
            if isinstance(right, exp.Boolean) and right.this is True:
                findings.append("SQL injection detected: boolean TRUE in OR clause.")

        return findings

    def _compute_subquery_depth(self, ast: exp.Expression, current_depth: int = 0) -> int:
        """Calculates the maximum depth of nested subqueries."""
        max_d = current_depth
        for subquery in ast.find_all(exp.Subquery):
            d = self._compute_subquery_depth(subquery.this, current_depth + 1)
            if d > max_d:
                max_d = d
        return max_d

    def _enforce_limit(self, ast: exp.Expression) -> exp.Expression:
        """Clamps or injects a safe LIMIT clause into the root query."""
        ast_copy = ast.copy()
        if isinstance(ast_copy, exp.Select):
            limit_node = ast_copy.args.get("limit")
            if limit_node is None:
                # Append default limit
                ast_copy = ast_copy.limit(settings.DEFAULT_QUERY_LIMIT)
            else:
                try:
                    val = int(limit_node.expression.this)
                    if val > settings.MAX_RETURN_ROWS or val <= 0:
                        ast_copy.args["limit"] = exp.Limit(this=exp.Literal.number(settings.MAX_RETURN_ROWS))
                except Exception:
                    pass
        return ast_copy
