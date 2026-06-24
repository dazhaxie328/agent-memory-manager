"""
向量数据库封装
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from utils.config import config


class VectorStore:
    """向量数据库封装"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=config.CHROMA_PERSIST_DIR,
            Settings=Settings(anonymized_telemetry=False)
        )
        self.collections = {}
    
    def get_collection(self, name: str):
        """获取或创建集合"""
        if name not in self.collections:
            self.collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
        return self.collections[name]
    
    def add(
        self,
        collection_name: str,
        ids: List[str],
        documents: List[str],
        embeddings: Optional[List[List[float]]] = None,
        metadatas: Optional[List[dict]] = None
    ):
        """添加文档"""
        collection = self.get_collection(collection_name)
        kwargs = {
            "ids": ids,
            "documents": documents,
        }
        if embeddings:
            kwargs["embeddings"] = embeddings
        if metadatas:
            kwargs["metadatas"] = metadatas
        collection.add(**kwargs)
    
    def query(
        self,
        collection_name: str,
        query_text: str,
        query_embedding: Optional[List[float]] = None,
        n_results: int = 5,
        where: Optional[dict] = None
    ) -> Dict[str, Any]:
        """查询"""
        collection = self.get_collection(collection_name)
        kwargs = {
            "query_texts": [query_text] if not query_embedding else None,
            "query_embeddings": [query_embedding] if query_embedding else None,
            "n_results": n_results,
        }
        if where:
            kwargs["where"] = where
        return collection.query(**kwargs)
    
    def update(
        self,
        collection_name: str,
        ids: List[str],
        documents: Optional[List[str]] = None,
        embeddings: Optional[List[List[float]]] = None,
        metadatas: Optional[List[dict]] = None
    ):
        """更新"""
        collection = self.get_collection(collection_name)
        kwargs = {"ids": ids}
        if documents:
            kwargs["documents"] = documents
        if embeddings:
            kwargs["embeddings"] = embeddings
        if metadatas:
            kwargs["metadatas"] = metadatas
        collection.update(**kwargs)
    
    def delete(self, collection_name: str, ids: List[str]):
        """删除"""
        collection = self.get_collection(collection_name)
        collection.delete(ids=ids)
    
    def get_all(self, collection_name: str) -> Dict[str, Any]:
        """获取所有"""
        collection = self.get_collection(collection_name)
        return collection.get()
    
    def count(self, collection_name: str) -> int:
        """获取数量"""
        collection = self.get_collection(collection_name)
        return collection.count()


# 创建全局实例
vector_store = VectorStore()