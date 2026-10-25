from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from ..core.config import settings
from ..core.database import DatabaseManager, seed_database
from ..core.schema_manager import SchemaManager
from ..core.ast_guardrails import ASTGuardrails, GuardrailAudit
from ..core.sandbox_executor import SandboxExecutor, ExecutionResult
from ..retrieval.vector_retriever import DynamicExemplarRetriever
from ..generation.sql_generator import SQLGenerator
from ..evaluation.benchmark_runner import BenchmarkRunner

# Initialize services
db_manager = DatabaseManager()
seed_database(db_manager)
schema_manager = SchemaManager(db_manager)
guardrails = ASTGuardrails(schema_manager)
executor = SandboxExecutor(db_manager, guardrails)
retriever = DynamicExemplarRetriever()
generator = SQLGenerator(schema_manager, retriever)
benchmark_runner = BenchmarkRunner(generator)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade natural language Text-to-SQL API with schema-aware few-shot prompting, dynamic vector exemplar retrieval, and AST guardrails."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request / Response Schemas
class QueryRequest(BaseModel):
    question: str = Field(..., example="Show top 5 products by revenue in Electronics")
    top_k_exemplars: int = Field(default=3, ge=1, le=10)

class GenerateSQLRequest(BaseModel):
    question: str = Field(..., example="List active customers in Germany")
    top_k_exemplars: int = Field(default=3, ge=1, le=10)

class ValidateSQLRequest(BaseModel):
    sql: str = Field(..., example="DROP TABLE customers;")

class ExecuteSQLRequest(BaseModel):
    sql: str = Field(..., example="SELECT customer_id, first_name, country FROM customers LIMIT 10;")

class BenchmarkRunRequest(BaseModel):
    limit: Optional[int] = Field(default=None, description="Optional subset limit for fast testing")

# Endpoints
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database_connected": db_manager.db_path.exists()
    }

@app.post("/api/query")
def end_to_end_query(req: QueryRequest):
    """
    End-to-End Pipeline:
    1. Retrieve dynamic exemplars via dense vector similarity.
    2. Build schema-aware few-shot prompt.
    3. Generate SQL query.
    4. Validate against AST guardrails (destructive & injection checks).
    5. Execute safely in read-only SQLite sandbox.
    """
    # 1 & 2 & 3. Generate SQL
    gen_result = generator.generate_sql(req.question, top_k_exemplars=req.top_k_exemplars)
    generated_sql = gen_result["sql"]

    # 4 & 5. Guardrail check & execution
    exec_result: ExecutionResult = executor.execute_guarded(generated_sql)

    return {
        "question": req.question,
        "generated_sql": generated_sql,
        "generation_mode": gen_result["generation_mode"],
        "retrieved_exemplars": gen_result["retrieved_exemplars"],
        "guardrail_audit": exec_result.guardrail_audit,
        "execution": {
            "success": exec_result.success,
            "columns": exec_result.columns,
            "rows": exec_result.rows,
            "row_count": exec_result.row_count,
            "execution_time_ms": exec_result.execution_time_ms,
            "error_message": exec_result.error_message,
            "sql_executed": exec_result.sql_executed
        }
    }

@app.post("/api/generate")
def generate_sql_only(req: GenerateSQLRequest):
    """Generates SQL with dynamic few-shot vector retrieval without executing."""
    result = generator.generate_sql(req.question, top_k_exemplars=req.top_k_exemplars)
    return result

@app.post("/api/guardrails/validate")
def validate_sql(req: ValidateSQLRequest):
    """
    AST Security Audit:
    Inspects SQL for destructive operations (DROP, DELETE, UPDATE, INSERT, ALTER),
    stacked queries, tautology injections, and complexity limits.
    """
    audit: GuardrailAudit = guardrails.validate_and_sanitize(req.sql)
    return audit

@app.post("/api/execute")
def execute_sql(req: ExecuteSQLRequest):
    """Safely executes SQL inside the read-only sandbox with statement timeout."""
    result: ExecutionResult = executor.execute_guarded(req.sql)
    return result

@app.get("/api/schema")
def get_schema():
    """Returns database schema, column definitions, foreign keys, and distinct categorical values."""
    return schema_manager.get_full_schema()

@app.get("/api/exemplars")
def get_exemplars(query: Optional[str] = None, top_k: int = 5):
    """Retrieves all golden exemplars or searches them dynamically via vector similarity."""
    if query:
        matches = retriever.retrieve(query, top_k=top_k)
        return [
            {
                "id": ex.id,
                "question": ex.question,
                "sql": ex.sql,
                "complexity": ex.complexity,
                "tables": ex.tables,
                "similarity": score
            }
            for ex, score in matches
        ]
    return [
        {
            "id": ex.id,
            "question": ex.question,
            "sql": ex.sql,
            "complexity": ex.complexity,
            "tables": ex.tables
        }
        for ex in retriever.exemplars
    ]

@app.post("/api/benchmark/run")
def run_benchmark_endpoint(req: BenchmarkRunRequest):
    """Triggers the 100+ complex query evaluation suite and returns accuracy metrics."""
    report = benchmark_runner.run_benchmark(limit=req.limit)
    return report
