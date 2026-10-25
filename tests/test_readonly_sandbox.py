import pytest
import sqlite3
from TextToSQL.core.database import DatabaseManager, seed_database
from TextToSQL.core.sandbox_executor import SandboxExecutor, ExecutionResult

@pytest.fixture(scope="module")
def setup_db():
    db = DatabaseManager()
    seed_database(db)
    return db

class TestReadOnlySandbox:

    def test_database_is_populated(self, setup_db):
        with setup_db.get_read_only_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers")
            assert cursor.fetchone()[0] > 0

    def test_sandbox_executes_safe_query(self, setup_db):
        executor = SandboxExecutor(setup_db)
        res: ExecutionResult = executor.execute_guarded("SELECT customer_id, first_name, country FROM customers LIMIT 5;")
        assert res.success is True
        assert res.row_count == 5
        assert len(res.columns) == 3
        assert res.execution_time_ms > 0

    def test_sandbox_blocks_destructive_at_guardrail(self, setup_db):
        executor = SandboxExecutor(setup_db)
        res: ExecutionResult = executor.execute_guarded("DROP TABLE customers;")
        assert res.success is False
        assert "Guardrail Blocked" in res.error_message

    def test_c_level_readonly_enforcement(self, setup_db):
        # Even if someone bypassed python guardrail, the C-level SQLite URI mode=ro blocks writes
        with setup_db.get_read_only_connection() as conn:
            with pytest.raises(sqlite3.OperationalError):
                conn.execute("INSERT INTO customers (first_name, last_name, email, segment, country, signup_date, churn_status) VALUES ('A','B','c@d.com','SMB','USA','2025-01-01','Active')")
