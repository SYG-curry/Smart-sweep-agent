from typing import List
from langchain_core.documents import Document
from rag.reranker import SimpleReranker
from rag.vector_store import VectorStoreService
from utils.config_handler import chroma_conf


# rerank检索实现, 建议跳点函数阅读, 两次检索
class HybridRetriever:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.reranker = SimpleReranker()

    def retrieve(self, query: str) -> List[Document]:
        candidate_docs = self.retriever.invoke(query)

        top_k = chroma_conf.get("rerank_top_k", chroma_conf["k"])

        reranked_docs = self.reranker.rerank(
            query=query,
            documents=candidate_docs,
            top_k=top_k,
        )

        return reranked_docs













