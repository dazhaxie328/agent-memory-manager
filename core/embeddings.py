"""
Embedding封装
"""

from typing import List
from langchain_openai import OpenAIEmbeddings
from utils.config import config


class EmbeddingService:
    """Embedding服务"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            openai_api_key=config.OPENAI_API_KEY
        )
    
    def embed_text(self, text: str) -> List[float]:
        """将文本转换为向量"""
        return self.embeddings.embed_query(text)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量将文本转换为向量"""
        return self.embeddings.embed_documents(texts)


# 创建全局实例
embedding_service = EmbeddingService()