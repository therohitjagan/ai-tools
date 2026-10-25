import sys
from pathlib import Path

# Safe UTF-8 console output for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from TextToSQL.core.database import DatabaseManager, seed_database
from TextToSQL.core.schema_manager import SchemaManager
from TextToSQL.core.ast_guardrails import ASTGuardrails
from TextToSQL.core.sandbox_executor import SandboxExecutor
from TextToSQL.retrieval.vector_retriever import DynamicExemplarRetriever
from TextToSQL.generation.sql_generator import SQLGenerator

def main():
    print("="*65)
    print("🛡️  Text-to-SQL Assistant with Guardrails - Interactive CLI")
    print("="*65)
    print("Type a natural language question (or type 'exit' to quit).")
    print("Try attack payloads like 'DROP TABLE customers;' to test guardrails.")
    print("="*65)

    db = DatabaseManager()
    seed_database(db)
    sm = SchemaManager(db)
    gr = ASTGuardrails(sm)
    executor = SandboxExecutor(db, gr)
    retriever = DynamicExemplarRetriever()
    generator = SQLGenerator(sm, retriever)

    while True:
        try:
            user_input = input("\n💬 User Query > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Goodbye!")
                break

            # If user explicitly enters raw SQL to test guardrails
            if any(user_input.upper().startswith(kw) for kw in ("SELECT", "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "ATTACH")):
                print("\n🔍 Running AST Security Audit on Raw SQL...")
                audit = gr.validate_and_sanitize(user_input)
                if audit.is_safe:
                    print(f"✅ PASSED: Safe read-only statement ({audit.ast_type})")
                    res = executor.execute_guarded(user_input)
                    print(f"Executed in {res.execution_time_ms} ms, {res.row_count} rows returned.")
                    if res.rows:
                        print("Columns:", res.columns)
                        for r in res.rows[:5]:
                            print("  ", r)
                else:
                    print(f"🛑 BLOCKED: Threat detected! (Risk: {audit.risk_level})")
                    for v in audit.violations:
                        print(f"   - {v}")
                continue

            # Natural language generation flow
            print("⚙️  Retrieving vector exemplars & synthesizing query...")
            gen_res = generator.generate_sql(user_input, top_k_exemplars=3)
            sql = gen_res["sql"]
            print(f"\n📝 Generated SQL:\n{sql}\n")

            print("🛡️  Executing in Read-Only Sandbox...")
            exec_res = executor.execute_guarded(sql)
            if exec_res.success:
                print(f"✅ Execution Success: {exec_res.row_count} rows in {exec_res.execution_time_ms} ms")
                if exec_res.rows:
                    print("Columns:", exec_res.columns)
                    for r in exec_res.rows[:5]:
                        print("  ", r)
                    if exec_res.row_count > 5:
                        print(f"   ... and {exec_res.row_count - 5} more rows.")
            else:
                print(f"❌ Execution Blocked/Failed: {exec_res.error_message}")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

if __name__ == "__main__":
    main()
