"""
记忆管理服务
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from core.vectorstore import vector_store
from core.embeddings import embedding_service
from models.memory import (
    MemoryType, MemoryCreate, MemoryResponse,
    MemoryUpdate, MemorySearch
)
from utils.config import config


class MemoryManager:
    """记忆管理服务"""
    
    COLLECTION_NAME = "memories"
    
    def __init__(self):
        self.collection_name = config.CHROMA_COLLECTION_NAME + "_memories"
    
    def save(self, memory: MemoryCreate) -> MemoryResponse:
        """保存记忆"""
        # 生成ID
        memory_id = str(uuid.uuid4())
        
        # 生成向量
        embedding = embedding_service.embed_text(memory.content)
        
        # 准备元数据
        metadata = {
            "memory_type": memory.memory_type.value,
            "importance": memory.importance,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            **(memory.metadata or {})
        }
        
        # 保存到向量数据库
        vector_store.add(
            collection_name=self.collection_name,
            ids=[memory_id],
            documents=[memory.content],
            embeddings=[embedding],
            metadatas=[metadata]
        )
        
        return MemoryResponse(
            id=memory_id,
            memory_type=memory.memory_type,
            content=memory.content,
            metadata=memory.metadata,
            importance=memory.importance,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def search(self, search: MemorySearch) -> List[MemoryResponse]:
        """搜索记忆"""
        # 生成查询向量
        query_embedding = embedding_service.embed_text(search.query)
        
        # 构建过滤条件
        where = None
        if search.memory_type:
            where = {"memory_type": search.memory_type.value}
        
        # 查询
        results = vector_store.query(
            collection_name=self.collection_name,
            query_text=search.query,
            query_embedding=query_embedding,
            n_results=search.limit,
            where=where
        )
        
        # 解析结果
        memories = []
        if results and results["ids"] and results["ids"][0]:
            for i, memory_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0
                similarity = 1 - distance  # cosine distance转similarity
                
                if similarity >= search.min_similarity:
                    memories.append(MemoryResponse(
                        id=memory_id,
                        memory_type=MemoryType(metadata.get("memory_type", "fact")),
                        content=results["documents"][0][i],
                        metadata={k: v for k, v in metadata.items() 
                                 if k not in ["memory_type", "importance", "created_at", "updated_at"]},
                        importance=metadata.get("importance", 0.5),
                        created_at=datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat())),
                        updated_at=datetime.fromisoformat(metadata.get("updated_at", datetime.now().isoformat())),
                        similarity=similarity
                    ))
        
        return memories
    
    def get_by_id(self, memory_id: str) -> Optional[MemoryResponse]:
        """根据ID获取记忆"""
        results = vector_store.get_all(self.collection_name)
        
        if memory_id in results["ids"]:
            idx = results["ids"].index(memory_id)
            metadata = results["metadatas"][idx] if results["metadatas"] else {}
            
            return MemoryResponse(
                id=memory_id,
                memory_type=MemoryType(metadata.get("memory_type", "fact")),
                content=results["documents"][idx],
                metadata={k: v for k, v in metadata.items() 
                         if k not in ["memory_type", "importance", "created_at", "updated_at"]},
                importance=metadata.get("importance", 0.5),
                created_at=datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(metadata.get("updated_at", datetime.now().isoformat()))
            )
        
        return None
    
    def update(self, memory_id: str, update: MemoryUpdate) -> Optional[MemoryResponse]:
        """更新记忆"""
        # 获取现有记忆
        existing = self.get_by_id(memory_id)
        if not existing:
            return None
        
        # 准备更新数据
        new_content = update.content or existing.content
        new_metadata = {
            "memory_type": existing.memory_type.value,
            "importance": update.importance or existing.importance,
            "created_at": existing.created_at.isoformat(),
            "updated_at": datetime.now().isoformat(),
            **(update.metadata or existing.metadata or {})
        }
        
        # 如果内容变化，重新生成向量
        if update.content:
            new_embedding = embedding_service.embed_text(new_content)
            vector_store.update(
                collection_name=self.collection_name,
                ids=[memory_id],
                documents=[new_content],
                embeddings=[new_embedding],
                metadatas=[new_metadata]
            )
        else:
            vector_store.update(
                collection_name=self.collection_name,
                ids=[memory_id],
                metadatas=[new_metadata]
            )
        
        return self.get_by_id(memory_id)
    
    def delete(self, memory_id: str) -> bool:
        """删除记忆"""
        try:
            vector_store.delete(
                collection_name=self.collection_name,
                ids=[memory_id]
            )
            return True
        except Exception:
            return False
    
    def get_all(self) -> List[MemoryResponse]:
        """获取所有记忆"""
        results = vector_store.get_all(self.collection_name)
        
        memories = []
        if results and results["ids"]:
            for i, memory_id in enumerate(results["ids"]):
                metadata = results["metadatas"][i] if results["metadatas"] else {}
                
                memories.append(MemoryResponse(
                    id=memory_id,
                    memory_type=MemoryType(metadata.get("memory_type", "fact")),
                    content=results["documents"][i],
                    metadata={k: v for k, v in metadata.items() 
                             if k not in ["memory_type", "importance", "created_at", "updated_at"]},
                    importance=metadata.get("importance", 0.5),
                    created_at=datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat())),
                    updated_at=datetime.fromisoformat(metadata.get("updated_at", datetime.now().isoformat()))
                ))
        
        return memories
    
    def count(self) -> int:
        """获取记忆数量"""
        return vector_store.count(self.collection_name)
    
    def save_conversation(self, user_message: str, ai_response: str, metadata: dict = None):
        """保存对话记忆"""
        content = f"用户: {user_message}\nAI: {ai_response}"
        return self.save(MemoryCreate(
            memory_type=MemoryType.CONVERSATION,
            content=content,
            metadata=metadata or {},
            importance=0.3
        ))
    
    def save_user_preference(self, preference: str, metadata: dict = None):
        """保存用户偏好"""
        return self.save(MemoryCreate(
            memory_type=MemoryType.USER_PREFERENCE,
            content=preference,
            metadata=metadata or {},
            importance=0.8
        ))
    
    def save_fact(self, fact: str, metadata: dict = None):
        """保存事实知识"""
        return self.save(MemoryCreate(
            memory_type=MemoryType.FACT,
            content=fact,
            metadata=metadata or {},
            importance=0.6
        ))


# 创建全局实例
memory_manager = MemoryManager()