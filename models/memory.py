"""
记忆数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MemoryType(str, Enum):
    """记忆类型"""
    USER_PREFERENCE = "user_preference"  # 用户偏好
    CONVERSATION = "conversation"  # 对话历史
    FACT = "fact"  # 事实知识
    INSTRUCTION = "instruction"  # 指令
    CONTEXT = "context"  # 上下文


class MemoryBase(BaseModel):
    """记忆基础信息"""
    memory_type: MemoryType = Field(..., description="记忆类型")
    content: str = Field(..., description="记忆内容")
    metadata: Optional[dict] = Field(default_factory=dict, description="元数据")
    importance: float = Field(default=0.5, description="重要性 (0-1)")


class MemoryCreate(MemoryBase):
    """创建记忆"""
    pass


class MemoryResponse(MemoryBase):
    """记忆响应"""
    id: str
    created_at: datetime
    updated_at: datetime
    similarity: Optional[float] = None


class MemoryUpdate(BaseModel):
    """更新记忆"""
    content: Optional[str] = None
    metadata: Optional[dict] = None
    importance: Optional[float] = None


class MemorySearch(BaseModel):
    """搜索记忆"""
    query: str = Field(..., description="搜索查询")
    memory_type: Optional[MemoryType] = Field(None, description="过滤类型")
    limit: int = Field(default=5, description="返回数量")
    min_similarity: float = Field(default=0.5, description="最小相似度")


class MemoryBatch(BaseModel):
    """批量记忆"""
    memories: List[MemoryCreate]