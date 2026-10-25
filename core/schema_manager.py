import sqlite3
from typing import Dict, List, Any, Set, Tuple
from pathlib import Path
from .database import DatabaseManager

class SchemaManager:
    """Introspects SQLite relational schema, builds foreign key graphs, and prunes context."""

    def __init__(self, db_manager: DatabaseManager | None = None):
        self.db = db_manager or DatabaseManager()
        self._schema_cache: Dict[str, Any] | None = None
        self._fk_graph: Dict[str, Set[str]] = {}

    def get_full_schema(self, refresh: bool = False) -> Dict[str, Any]:
        """Returns introspected metadata for all tables, columns, keys, and sample values."""
        if self._schema_cache and not refresh:
            return self._schema_cache

        schema = {"tables": {}, "foreign_keys": [], "relationships": {}}

        with self.db.get_read_only_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Fetch user tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row["name"] for row in cursor.fetchall()]

            for table in tables:
                # Columns & types
                cursor.execute(f"PRAGMA table_info({table})")
                cols = []
                pks = []
                for col in cursor.fetchall():
                    c_info = {
                        "name": col["name"],
                        "type": col["type"],
                        "notnull": bool(col["notnull"]),
                        "pk": bool(col["pk"])
                    }
                    if col["pk"]:
                        pks.append(col["name"])
                    cols.append(c_info)

                # Foreign keys
                cursor.execute(f"PRAGMA foreign_key_list({table})")
                fks = []
                for fk in cursor.fetchall():
                    fk_info = {
                        "from_table": table,
                        "from_col": fk["from"],
                        "to_table": fk["table"],
                        "to_col": fk["to"]
                    }
                    fks.append(fk_info)
                    schema["foreign_keys"].append(fk_info)

                    # Build graph
                    self._fk_graph.setdefault(table, set()).add(fk["table"])
                    self._fk_graph.setdefault(fk["table"], set()).add(table)

                # Sample categorical values for text columns
                distinct_values = {}
                for c in cols:
                    if "TEXT" in c["type"].upper() or "VARCHAR" in c["type"].upper():
                        try:
                            cursor.execute(f"SELECT DISTINCT {c['name']} FROM {table} WHERE {c['name']} IS NOT NULL LIMIT 8")
                            distinct_values[c["name"]] = [r[0] for r in cursor.fetchall()]
                        except Exception:
                            pass

                # Row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]

                schema["tables"][table] = {
                    "columns": cols,
                    "primary_keys": pks,
                    "foreign_keys": fks,
                    "distinct_values": distinct_values,
                    "row_count": row_count
                }

        self._schema_cache = schema
        return schema

    def format_ddl_context(self, selected_tables: List[str] | None = None) -> str:
        """Generates DDL string annotated with foreign keys and distinct categorical values."""
        schema = self.get_full_schema()
        target_tables = selected_tables or list(schema["tables"].keys())
        
        ddl_parts = []
        for t_name in target_tables:
            if t_name not in schema["tables"]:
                continue
            t_data = schema["tables"][t_name]
            lines = [f"CREATE TABLE {t_name} ("]
            
            col_defs = []
            for col in t_data["columns"]:
                pk_str = " PRIMARY KEY" if col["pk"] else ""
                notnull_str = " NOT NULL" if col["notnull"] and not col["pk"] else ""
                col_defs.append(f"    {col['name']} {col['type']}{pk_str}{notnull_str}")

            for fk in t_data["foreign_keys"]:
                col_defs.append(f"    FOREIGN KEY ({fk['from_col']}) REFERENCES {fk['to_table']}({fk['to_col']})")

            lines.append(",\n".join(col_defs))
            lines.append(");")

            # Annotate distinct categorical values if helpful
            enums = []
            for col_name, vals in t_data["distinct_values"].items():
                if 1 <= len(vals) <= 6:
                    val_repr = ", ".join(f"'{v}'" for v in vals)
                    enums.append(f"-- Example values for {t_name}.{col_name}: [{val_repr}]")
            
            if enums:
                lines.append("\n".join(enums))

            ddl_parts.append("\n".join(lines))

        return "\n\n".join(ddl_parts)

    def prune_schema(self, query_text: str, max_tables: int = 5) -> List[str]:
        """
        Dynamically selects the most relevant tables for the natural language query,
        ensuring foreign key connectivity between referenced entities.
        """
        schema = self.get_full_schema()
        all_tables = list(schema["tables"].keys())
        q_lower = query_text.lower()

        scores: Dict[str, float] = {t: 0.0 for t in all_tables}

        # Table keywords mapping
        table_keywords = {
            "customers": ["customer", "client", "user", "buyer", "signup", "churn", "email", "segment", "country"],
            "suppliers": ["supplier", "vendor", "manufacturer", "reliability", "rating"],
            "products": ["product", "item", "category", "price", "cost", "stock", "inventory", "laptops", "tablets", "audio", "furniture"],
            "orders": ["order", "purchase", "sale", "revenue", "spend", "bought", "shipping", "payment", "fulfillment", "delivered", "status"],
            "order_items": ["quantity", "items", "discount", "volume", "units", "ordered"],
            "support_tickets": ["ticket", "support", "issue", "complaint", "resolution", "satisfaction", "priority", "escalated"],
            "product_reviews": ["review", "rating", "feedback", "stars", "helpful", "sentiment"]
        }

        for t, kws in table_keywords.items():
            for kw in kws:
                if kw in q_lower:
                    scores[t] += 2.0
            if t in q_lower:
                scores[t] += 4.0
            
            # Check column names
            for col in schema["tables"].get(t, {}).get("columns", []):
                if col["name"].lower() in q_lower:
                    scores[t] += 1.5

        # Always include at least 1 table with score > 0, fallback to default core tables
        selected = [t for t, s in sorted(scores.items(), key=lambda x: x[1], reverse=True) if s > 0][:max_tables]
        if not selected:
            selected = ["customers", "orders", "products"]

        # Ensure bridging tables for JOIN integrity:
        # e.g., if customers and products are selected, orders and order_items bridge them
        if "customers" in selected and "products" in selected:
            if "orders" not in selected:
                selected.append("orders")
            if "order_items" not in selected:
                selected.append("order_items")

        if "orders" in selected and "products" in selected and "order_items" not in selected:
            selected.append("order_items")

        return list(dict.fromkeys(selected))
