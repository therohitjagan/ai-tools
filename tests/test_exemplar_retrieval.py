import pytest
from TextToSQL.retrieval.exemplar_store import get_all_exemplars
from TextToSQL.retrieval.vector_retriever import DynamicExemplarRetriever

class TestExemplarRetrieval:

    def test_exemplars_store_not_empty(self):
        exemplars = get_all_exemplars()
        assert len(exemplars) >= 20
        complexities = {ex.complexity for ex in exemplars}
        assert "simple" in complexities
        assert "join" in complexities
        assert "aggregation" in complexities
        assert "subquery" in complexities
        assert "window" in complexities

    def test_dynamic_vector_retrieval(self):
        retriever = DynamicExemplarRetriever()
        results = retriever.retrieve("cumulative running revenue over order dates", top_k=3)
        assert len(results) == 3
        top_ex, score = results[0]
        assert score > 0.0
        assert "window" in [ex.complexity for ex, _ in results] or "aggregation" in [ex.complexity for ex, _ in results]

    def test_join_retrieval(self):
        retriever = DynamicExemplarRetriever()
        results = retriever.retrieve("customer name and their orders delivered", top_k=3)
        assert len(results) == 3
        assert any(ex.complexity == "join" for ex, _ in results)
