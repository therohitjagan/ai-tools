from typing import List, Tuple
from ..core.schema_manager import SchemaManager
from ..retrieval.exemplar_store import GoldenExemplar

SYSTEM_PROMPT_TEMPLATE = """You are an expert SQL Data Architect specializing in translating natural language questions into accurate, high-performance, read-only SQLite queries.

### DATABASE RULES:
1. DIALECT: SQLite 3.x.
2. READ-ONLY CONSTRAINT: Only generate SELECT statements (including CTEs using WITH ... AS (...)). Never write INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or PRAGMA statements.
3. JOINS: Join tables using explicit foreign key references. Alias table names cleanly (e.g. `c` for customers, `o` for orders, `oi` for order_items, `p` for products).
4. DATES: SQLite stores dates as ISO-8601 strings ('YYYY-MM-DD'). Use `strftime('%Y-%m', date_col)` for monthly grouping and `date('now', '-N days')` for intervals.
5. CONCATENATION: Use the pipe operator `||` for string concatenation (e.g. `first_name || ' ' || last_name`).
6. ROUNDING: Always wrap monetary and percentage averages in `ROUND(..., 2)`.
7. LIMIT: Apply a reasonable `LIMIT` (default 100) if no specific limit is requested.

### SCHEMA CONTEXT:
{schema_ddl}

### DYNAMICALLY RETRIEVED FEW-SHOT EXEMPLARS:
{few_shot_exemplars}

### INSTRUCTIONS:
Given the user's natural language question, generate ONLY the executable SQL query inside a markdown ```sql code block. No explanation before or after.
"""

class PromptBuilder:
    """Assembles schema-aware system instructions and dynamically retrieved exemplars."""

    def __init__(self, schema_manager: SchemaManager):
        self.schema_manager = schema_manager

    def build_system_prompt(self, user_question: str, retrieved_exemplars: List[Tuple[GoldenExemplar, float]]) -> str:
        """
        Dynamically prunes schema and formats retrieved exemplars into few-shot context.
        """
        # Prune schema to most relevant tables
        relevant_tables = self.schema_manager.prune_schema(user_question, max_tables=5)
        schema_ddl = self.schema_manager.format_ddl_context(relevant_tables)

        # Format exemplars
        exemplar_blocks = []
        for i, (ex, sim_score) in enumerate(retrieved_exemplars, 1):
            block = (
                f"-- Exemplar #{i} (Complexity: {ex.complexity.upper()}, Similarity: {sim_score:.2f})\n"
                f"-- Question: {ex.question}\n"
                f"{ex.sql}"
            )
            exemplar_blocks.append(block)

        exemplars_text = "\n\n".join(exemplar_blocks) if exemplar_blocks else "-- No exemplars retrieved."

        return SYSTEM_PROMPT_TEMPLATE.format(
            schema_ddl=schema_ddl,
            few_shot_exemplars=exemplars_text
        )

    def build_user_prompt(self, user_question: str) -> str:
        """Constructs user prompt."""
        return f"Natural Language Question: {user_question}\nGenerate SQL:"
