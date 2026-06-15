from typing import List
from langchain_core.documents import Document



class SimpleReranker:
    def __init__(self):
        pass

    def rerank(
            self,
            query: str,
            documents: List[Document],
            top_k: int = 3,
    ) -> List[Document]:
        if not documents:
            return []

        scored_docs = []

        for doc in documents:
            score = self._score(query, doc.page_content)
            scored_docs.append((score, doc))

        scored_docs.sort(key=lambda item: item[0], reverse=True)

        return [doc for score, doc in scored_docs[:top_k]]

    def _score(self, query: str, content: str) -> int:
        score = 0

        for char in query:
            if char.strip() and char in content:
                score += 1

        return score








