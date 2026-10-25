import time
import sqlite3
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from .database import DatabaseManager
from .ast_guardrails import ASTGuardrails, GuardrailAudit
from .config import settings

@dataclass
class ExecutionResult:
    success: bool
    columns: List[str] = field(default_factory=list)
    rows: List[List[Any]] = field(default_factory=list)
    row_count: int = 0
    execution_time_ms: float = 0.0
    error_message: Optional[str] = None
    guardrail_audit: Optional[GuardrailAudit] = None
    sql_executed: Optional[str] = None

class SandboxExecutor:
    """Executes validated SQL queries against the read-only SQLite sandbox."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None, guardrails: Optional[ASTGuardrails] = None):
        self.db = db_manager or DatabaseManager()
        self.guardrails = guardrails or ASTGuardrails()

    def execute_guarded(self, raw_sql: str) -> ExecutionResult:
        """
        Validates the raw SQL through AST guardrails and executes it only if 100% safe.
        """
        audit = self.guardrails.validate_and_sanitize(raw_sql)
        if not audit.is_safe:
            return ExecutionResult(
                success=False,
                error_message=f"Guardrail Blocked: {'; '.join(audit.violations)}",
                guardrail_audit=audit,
                sql_executed=raw_sql
            )

        start_time = time.perf_counter()
        target_sql = audit.sanitized_sql or raw_sql

        try:
            with self.db.get_read_only_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(target_sql)
                
                # Fetch column descriptions
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                raw_rows = cursor.fetchall()
                
                # Serialize row values
                rows = []
                for row in raw_rows:
                    row_data = []
                    for val in row:
                        if isinstance(val, (int, float, str, type(None))):
                            row_data.append(val)
                        elif isinstance(val, bytes):
                            row_data.append(f"<blob {len(val)} bytes>")
                        else:
                            row_data.append(str(val))
                    rows.append(row_data)

                exec_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

                return ExecutionResult(
                    success=True,
                    columns=columns,
                    rows=rows,
                    row_count=len(rows),
                    execution_time_ms=exec_time_ms,
                    guardrail_audit=audit,
                    sql_executed=target_sql
                )

        except sqlite3.OperationalError as op_err:
            exec_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return ExecutionResult(
                success=False,
                execution_time_ms=exec_time_ms,
                error_message=f"SQLite Execution Error: {str(op_err)}",
                guardrail_audit=audit,
                sql_executed=target_sql
            )
        except Exception as err:
            exec_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return ExecutionResult(
                success=False,
                execution_time_ms=exec_time_ms,
                error_message=f"Unexpected Execution Error: {str(err)}",
                guardrail_audit=audit,
                sql_executed=target_sql
            )
