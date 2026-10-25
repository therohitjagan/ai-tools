import math
from typing import List, Any, Dict, Optional, Tuple
from dataclasses import dataclass
from ..core.sandbox_executor import SandboxExecutor, ExecutionResult
from ..core.ast_guardrails import ASTGuardrails, GuardrailAudit

@dataclass
class EvaluationResult:
    query_id: str
    question: str
    complexity: str
    syntax_valid: bool
    guardrail_passed: bool
    execution_match: bool
    predicted_sql: str
    gold_sql: str
    predicted_row_count: int
    gold_row_count: int
    latency_ms: float
    error_message: Optional[str] = None
    diff_reason: Optional[str] = None

class AccuracyEvaluator:
    """
    Rigorously evaluates Text-to-SQL predictions against gold queries.
    Measures syntax validity, AST guardrail compliance, and execution set equivalence.
    """

    def __init__(self, executor: Optional[SandboxExecutor] = None, guardrails: Optional[ASTGuardrails] = None):
        self.executor = executor or SandboxExecutor()
        self.guardrails = guardrails or ASTGuardrails()

    def evaluate_query(
        self,
        query_id: str,
        question: str,
        complexity: str,
        predicted_sql: str,
        gold_sql: str
    ) -> EvaluationResult:
        """
        Executes both predicted and gold queries and verifies result set equivalence.
        """
        # 1. AST Guardrail Validation
        audit = self.guardrails.validate_and_sanitize(predicted_sql)
        if not audit.is_safe:
            return EvaluationResult(
                query_id=query_id,
                question=question,
                complexity=complexity,
                syntax_valid="Syntax Error" not in "".join(audit.violations),
                guardrail_passed=False,
                execution_match=False,
                predicted_sql=predicted_sql,
                gold_sql=gold_sql,
                predicted_row_count=0,
                gold_row_count=0,
                latency_ms=0.0,
                error_message=f"Guardrail blocked: {'; '.join(audit.violations)}",
                diff_reason="Guardrail violation prevented execution."
            )

        # 2. Execute Gold Standard Query
        gold_result: ExecutionResult = self.executor.execute_guarded(gold_sql)
        if not gold_result.success:
            return EvaluationResult(
                query_id=query_id,
                question=question,
                complexity=complexity,
                syntax_valid=True,
                guardrail_passed=True,
                execution_match=False,
                predicted_sql=predicted_sql,
                gold_sql=gold_sql,
                predicted_row_count=0,
                gold_row_count=0,
                latency_ms=0.0,
                error_message=f"Gold standard query error: {gold_result.error_message}",
                diff_reason="Gold standard query execution failed."
            )

        # 3. Execute Predicted Query
        pred_result: ExecutionResult = self.executor.execute_guarded(predicted_sql)
        if not pred_result.success:
            return EvaluationResult(
                query_id=query_id,
                question=question,
                complexity=complexity,
                syntax_valid=True,
                guardrail_passed=True,
                execution_match=False,
                predicted_sql=predicted_sql,
                gold_sql=gold_sql,
                predicted_row_count=0,
                gold_row_count=gold_result.row_count,
                latency_ms=pred_result.execution_time_ms,
                error_message=pred_result.error_message,
                diff_reason=f"Predicted query runtime error: {pred_result.error_message}"
            )

        # 4. Compare Result Sets
        is_ordered = "order by" in gold_sql.lower()
        match, reason = self.compare_result_sets(pred_result.rows, gold_result.rows, is_ordered)

        return EvaluationResult(
            query_id=query_id,
            question=question,
            complexity=complexity,
            syntax_valid=True,
            guardrail_passed=True,
            execution_match=match,
            predicted_sql=predicted_sql,
            gold_sql=gold_sql,
            predicted_row_count=pred_result.row_count,
            gold_row_count=gold_result.row_count,
            latency_ms=pred_result.execution_time_ms,
            error_message=None if match else reason,
            diff_reason=None if match else reason
        )

    def compare_result_sets(
        self,
        pred_rows: List[List[Any]],
        gold_rows: List[List[Any]],
        require_order: bool = False,
        float_tolerance: float = 1e-2
    ) -> Tuple[bool, Optional[str]]:
        """
        Deep comparison of two table result sets with float tolerance and multiset matching.
        """
        if len(pred_rows) != len(gold_rows):
            return False, f"Row count mismatch: predicted {len(pred_rows)} rows vs gold {len(gold_rows)} rows."

        if not pred_rows and not gold_rows:
            return True, None

        if len(pred_rows[0]) != len(gold_rows[0]):
            return False, f"Column count mismatch: predicted {len(pred_rows[0])} columns vs gold {len(gold_rows[0])} columns."

        def values_match(val1: Any, val2: Any) -> bool:
            if val1 is None and val2 is None:
                return True
            if val1 is None or val2 is None:
                return False
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                return abs(float(val1) - float(val2)) <= float_tolerance
            # String comparison
            s1 = str(val1).strip().lower()
            s2 = str(val2).strip().lower()
            if s1 == s2:
                return True
            try:
                f1 = float(s1)
                f2 = float(s2)
                return abs(f1 - f2) <= float_tolerance
            except ValueError:
                return False

        def rows_match(r1: List[Any], r2: List[Any]) -> bool:
            if len(r1) != len(r2):
                return False
            return all(values_match(a, b) for a, b in zip(r1, r2))

        # Ordered comparison
        if require_order:
            for idx, (p_row, g_row) in enumerate(zip(pred_rows, gold_rows)):
                if not rows_match(p_row, g_row):
                    return False, f"Row ordering/value mismatch at row {idx + 1}: predicted {p_row} != gold {g_row}."
            return True, None

        # Multiset comparison (order-invariant)
        unmatched_gold = list(gold_rows)
        for p_row in pred_rows:
            matched_idx = -1
            for g_idx, g_row in enumerate(unmatched_gold):
                if rows_match(p_row, g_row):
                    matched_idx = g_idx
                    break
            if matched_idx != -1:
                unmatched_gold.pop(matched_idx)
            else:
                return False, f"Unmatched predicted row: {p_row} not found in gold results."

        return True, None
