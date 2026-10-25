import pytest
from TextToSQL.core.database import DatabaseManager, seed_database
from TextToSQL.evaluation.benchmark_dataset import get_benchmark_dataset
from TextToSQL.evaluation.accuracy_evaluator import AccuracyEvaluator
from TextToSQL.evaluation.benchmark_runner import BenchmarkRunner
from TextToSQL.generation.sql_generator import SQLGenerator

@pytest.fixture(scope="module")
def setup_eval():
    db = DatabaseManager()
    seed_database(db)
    gen = SQLGenerator()
    runner = BenchmarkRunner(gen)
    return runner

class TestEvaluationAccuracy:

    def test_benchmark_dataset_contains_100_plus_queries(self):
        dataset = get_benchmark_dataset()
        assert len(dataset) >= 100, f"Expected 100+ benchmark queries, found {len(dataset)}"
        
        # Check presence of complex queries
        complexities = {q.complexity for q in dataset}
        assert "simple" in complexities
        assert "join" in complexities
        assert "aggregation" in complexities
        assert "subquery" in complexities
        assert "window" in complexities

    def test_accuracy_evaluator_float_tolerance(self):
        evaluator = AccuracyEvaluator()
        row_pred = [["Electronics", 12500.456]]
        row_gold = [["Electronics", 12500.459]]
        match, _ = evaluator.compare_result_sets(row_pred, row_gold, float_tolerance=0.01)
        assert match is True

    def test_accuracy_evaluator_multiset_matching(self):
        evaluator = AccuracyEvaluator()
        rows_pred = [["A", 10], ["B", 20]]
        rows_gold = [["B", 20], ["A", 10]]
        match, _ = evaluator.compare_result_sets(rows_pred, rows_gold, require_order=False)
        assert match is True

    def test_full_benchmark_achieves_89_percent_accuracy(self, setup_eval):
        report = setup_eval.run_benchmark()
        summary = report["summary"]

        assert summary["total_queries"] >= 100
        assert summary["execution_accuracy_pct"] >= 89.0, f"Execution accuracy {summary['execution_accuracy_pct']}% fell below 89.0% threshold"
        assert summary["syntax_validity_pct"] == 100.0
        assert summary["guardrail_pass_rate_pct"] == 100.0
