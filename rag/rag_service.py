from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model
from rag.retriever import HybridRetriever
from utils.cache import cache_service
from utils.logger_handler import logger
from utils.prompt_loader import load_rag_prompts


class RagSummarizeService(object):
    def __init__(self):
        self.retriever = HybridRetriever()
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._init_chain()

    def _init_chain(self):
        chain = self.prompt_template | self.model | StrOutputParser()
        return chain

    def retriever_docs(self, query: str) -> list[Document]:
        cache_key_args = (query,)
        cached = cache_service.get("rag_docs", *cache_key_args)

        # 先找缓存, 找得到直接返回
        # 防止Redis存了个[], 这样的if cached == [] 也是False, 即使命中也会跳过
        if cached is not None:
            logger.info(f"[rag] 使用缓存的检索结果, query={query[:20]}...")
            return [
                # 读取时再还原
                Document(page_content=doc["page_content"], metadata=doc.get("metadata", {}))
                for doc in cached
            ]

        # 检索到的匹配文档
        docs = self.retriever.retrieve(query)

        # 存入cache
        cache_value = [
            # Document 对象不能直接 JSON 序列化，所以要转成字典
            {"page_content": doc.page_content, "metadata": doc.metadata}
            for doc in docs
        ]
        cache_service.set("rag_docs", *cache_key_args, value=cache_value)

        return docs

    # 用上个函数检索到的匹配文档, 组合成提示词送入模型
    def rag_summarize(self, query: str) -> str:
        context_docs = self.retriever_docs(query)
        context = ""
        counter = 0
        for doc in context_docs:
            counter += 1
            context += f"[参考资料{counter}]: 参考资料:{doc.page_content} \n"

        return self.chain.invoke(
            {
                "input": query,
                "context": context,
            }
        )



if __name__ == '__main__':
    rag = RagSummarizeService()
    print(rag.rag_summarize("小户型适合哪些扫地机器人"))