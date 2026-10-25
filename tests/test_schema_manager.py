import pytest
from TextToSQL.core.database import DatabaseManager, seed_database
from TextToSQL.core.schema_manager import SchemaManager

@pytest.fixture(scope="module")
def setup_schema():
    db = DatabaseManager()
    seed_database(db)
    return SchemaManager(db)

class TestSchemaManager:

    def test_introspects_all_tables(self, setup_schema):
        schema = setup_schema.get_full_schema()
        assert "tables" in schema
        expected_tables = {"customers", "suppliers", "products", "orders", "order_items", "support_tickets", "product_reviews"}
        actual_tables = set(schema["tables"].keys())
        assert expected_tables.issubset(actual_tables)

    def test_extracts_foreign_keys(self, setup_schema):
        schema = setup_schema.get_full_schema()
        fks = schema["foreign_keys"]
        assert len(fks) > 0
        from_tables = {fk["from_table"] for fk in fks}
        assert "orders" in from_tables
        assert "order_items" in from_tables

    def test_generates_annotated_ddl(self, setup_schema):
        ddl = setup_schema.format_ddl_context(["customers", "orders"])
        assert "CREATE TABLE customers" in ddl
        assert "CREATE TABLE orders" in ddl
        assert "FOREIGN KEY" in ddl

    def test_pruning_selects_relevant_tables(self, setup_schema):
        pruned = setup_schema.prune_schema("What are the best selling products by units ordered?")
        assert "products" in pruned
        assert "order_items" in pruned
