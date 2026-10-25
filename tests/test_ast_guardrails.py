import pytest
from TextToSQL.core.ast_guardrails import ASTGuardrails, GuardrailAudit

@pytest.fixture
def guardrails():
    return ASTGuardrails()

class TestASTGuardrails:

    # 1. 100% Destructive Operations Blocking
    @pytest.mark.parametrize("destructive_query", [
        "DROP TABLE customers;",
        "DROP TABLE IF EXISTS orders;",
        "DELETE FROM orders WHERE order_id = 5;",
        "DELETE FROM customers;",
        "UPDATE products SET unit_price = 0.00;",
        "UPDATE orders SET status = 'Delivered' WHERE order_id = 1;",
        "INSERT INTO customers (first_name, last_name, email) VALUES ('Hacker', 'X', 'hack@test.com');",
        "ALTER TABLE customers ADD COLUMN is_admin INTEGER;",
        "CREATE TABLE backdoors (id INTEGER PRIMARY KEY);",
        "TRUNCATE TABLE order_items;"
    ])
    def test_blocks_destructive_operations(self, guardrails, destructive_query):
        audit: GuardrailAudit = guardrails.validate_and_sanitize(destructive_query)
        assert not audit.is_safe, f"Failed to block destructive query: {destructive_query}"
        assert audit.status == "BLOCKED"
        assert audit.risk_level in ("CRITICAL", "MEDIUM")
        assert len(audit.violations) > 0

    # 2. 100% SQL Injection & Attack Blocking
    @pytest.mark.parametrize("injection_query", [
        "SELECT * FROM customers; DROP TABLE orders;",
        "SELECT customer_id FROM customers WHERE 1=1;",
        "SELECT * FROM customers WHERE segment = 'Enterprise' OR 1=1;",
        "SELECT * FROM customers WHERE 'a'='a';",
        "SELECT * FROM sqlite_master;",
        "ATTACH DATABASE 'evil.db' AS evil;",
        "DETACH DATABASE evil;",
        "SELECT 1; SELECT 2;"
    ])
    def test_blocks_sql_injection_attempts(self, guardrails, injection_query):
        audit: GuardrailAudit = guardrails.validate_and_sanitize(injection_query)
        assert not audit.is_safe, f"Failed to block SQL injection: {injection_query}"
        assert audit.status == "BLOCKED"
        assert len(audit.violations) > 0

    # 3. Allow Safe Read-Only Queries
    @pytest.mark.parametrize("safe_query", [
        "SELECT customer_id, first_name, email FROM customers WHERE country = 'Germany';",
        "SELECT p.category, SUM(oi.quantity) FROM products p JOIN order_items oi ON p.product_id = oi.product_id GROUP BY p.category;",
        "SELECT c.first_name, o.order_id, p.product_name FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_items oi ON o.order_id = oi.order_id JOIN products p ON oi.product_id = p.product_id WHERE o.status = 'Delivered';",
        "SELECT customer_id, first_name FROM customers WHERE customer_id NOT IN (SELECT customer_id FROM orders);",
        "SELECT order_id, customer_id, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS seq FROM orders;",
        "WITH ranked AS (SELECT product_id, RANK() OVER (ORDER BY unit_price DESC) as rnk FROM products) SELECT * FROM ranked WHERE rnk <= 3;"
    ])
    def test_allows_safe_queries(self, guardrails, safe_query):
        audit: GuardrailAudit = guardrails.validate_and_sanitize(safe_query)
        assert audit.is_safe, f"Safe query was unexpectedly blocked: {audit.violations}"
        assert audit.status == "PASSED"
        assert audit.sanitized_sql is not None
        assert "LIMIT" in audit.sanitized_sql.upper()

    def test_limit_enforcement(self, guardrails):
        sql = "SELECT customer_id FROM customers"
        audit = guardrails.validate_and_sanitize(sql)
        assert audit.is_safe
        assert "LIMIT" in audit.sanitized_sql.upper()
