import sys
import argparse
from pathlib import Path

# Safe UTF-8 console output for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from TextToSQL.core.database import DatabaseManager, seed_database
from TextToSQL.core.schema_manager import SchemaManager
from TextToSQL.retrieval.vector_retriever import DynamicExemplarRetriever
from TextToSQL.generation.sql_generator import SQLGenerator
from TextToSQL.evaluation.benchmark_runner import BenchmarkRunner

def main():
    parser = argparse.ArgumentParser(description="Run 100+ complex Text-to-SQL query benchmark.")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of queries to run")
    args = parser.parse_args()

    print("🚀 Starting Text-to-SQL Execution Accuracy Benchmark...")
    db = DatabaseManager()
    seed_database(db)

    sm = SchemaManager(db)
    retriever = DynamicExemplarRetriever()
    generator = SQLGenerator(sm, retriever)
    runner = BenchmarkRunner(generator)

    report = runner.run_benchmark(limit=args.limit)
    s = report["summary"]

    print("\n" + "="*50)
    print("🏆 TEXT-TO-SQL BENCHMARK SUMMARY")
    print("="*50)
    print(f"Total Queries Evaluated: {s['total_queries']}")
    print(f"Correct Execution Matches: {s['correct_executions']}")
    print(f"Execution Accuracy: {s['execution_accuracy_pct']}% (Target: >= 89.0%)")
    print(f"AST Syntax Validity Rate: {s['syntax_validity_pct']}%")
    print(f"Guardrail Pass Rate: {s['guardrail_pass_rate_pct']}%")
    print(f"Mean Latency: {s['average_latency_ms']} ms")
    print(f"Total Time: {s['total_duration_seconds']} s")
    print("="*50)

    print("\n🔍 COMPLEXITY TIER BREAKDOWN:")
    for comp, stats in report["complexity_breakdown"].items():
        print(f"  • {comp.upper():<14} : {stats['correct']}/{stats['total']} ({stats['accuracy']}%)")

    print("\n📄 Detailed reports saved to data/evaluations/benchmark_results.json and .md")

if __name__ == "__main__":
    main()
