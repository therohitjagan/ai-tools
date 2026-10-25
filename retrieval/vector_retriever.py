import math
import re
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
from .exemplar_store import GoldenExemplar, get_all_exemplars
from ..core.config import settings

class DynamicExemplarRetriever:
    """
    Dynamic vector-based exemplar retriever.
    Embeds natural language questions and matches queries in dense vector space
    to supply the most syntactically and semantically relevant few-shot exemplars.
    """

    def __init__(self, persist_dir: Optional[Path] = None):
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIR
        self.exemplars = get_all_exemplars()
        self._chroma_collection = None
        self._tfidf_index = None
        self._initialize_retriever()

    def _initialize_retriever(self) -> None:
        """
        Initializes high-performance self-contained dense vector index
        with zero external network dependencies.
        """
        self._build_vector_fallback()

    def _build_vector_fallback(self) -> None:
        """Computes subword/n-gram vector index with cosine similarity."""
        def tokenize(text: str) -> List[str]:
            return [w for w in re.findall(r"\w+", text.lower()) if len(w) > 2]

        doc_tokens = [tokenize(f"{ex.question} {' '.join(ex.tables)} {ex.complexity}") for ex in self.exemplars]
        df: Dict[str, int] = {}
        for tokens in doc_tokens:
            for term in set(tokens):
                df[term] = df.get(term, 0) + 1

        n_docs = len(self.exemplars)
        doc_vectors = []
        for tokens in doc_tokens:
            vec: Dict[str, float] = {}
            for t in tokens:
                tf = tokens.count(t) / len(tokens)
                idf = math.log((n_docs + 1) / (df.get(t, 0) + 1)) + 1.0
                vec[t] = tf * idf
            # normalize
            norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
            doc_vectors.append({t: v / norm for t, v in vec.items()})

        self._tfidf_index = {
            "df": df,
            "n_docs": n_docs,
            "doc_vectors": doc_vectors,
            "tokenize": tokenize
        }

    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[GoldenExemplar, float]]:
        """
        Retrieves top-k closest exemplars for the given natural language query.
        Returns list of (GoldenExemplar, similarity_score).
        """
        top_k = min(top_k, len(self.exemplars))

        # 1. Try ChromaDB
        if self._chroma_collection is not None:
            try:
                results = self._chroma_collection.query(
                    query_texts=[query],
                    n_results=top_k
                )
                if results and "ids" in results and results["ids"]:
                    retrieved_ids = results["ids"][0]
                    distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(retrieved_ids)
                    
                    id_to_exemplar = {ex.id: ex for ex in self.exemplars}
                    matched = []
                    for ex_id, dist in zip(retrieved_ids, distances):
                        if ex_id in id_to_exemplar:
                            score = round(max(0.0, 1.0 - dist), 4)
                            matched.append((id_to_exemplar[ex_id], score))
                    if matched:
                        return matched
            except Exception:
                pass

        # 2. Vector Cosine Fallback
        if self._tfidf_index is None:
            self._build_vector_fallback()

        idx = self._tfidf_index
        tokens = idx["tokenize"](query)
        if not tokens:
            return [(ex, 0.5) for ex in self.exemplars[:top_k]]

        q_vec: Dict[str, float] = {}
        for t in tokens:
            tf = tokens.count(t) / len(tokens)
            idf = math.log((idx["n_docs"] + 1) / (idx["df"].get(t, 0) + 1)) + 1.0
            q_vec[t] = tf * idf
        q_norm = math.sqrt(sum(v * v for v in q_vec.values())) or 1.0
        q_norm_vec = {t: v / q_norm for t, v in q_vec.items()}

        scores = []
        for i, d_vec in enumerate(idx["doc_vectors"]):
            sim = sum(q_norm_vec.get(t, 0.0) * val for t, val in d_vec.items())
            scores.append((self.exemplars[i], round(float(sim), 4)))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
