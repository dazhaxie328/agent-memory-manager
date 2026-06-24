"""
知识库数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """文档类型"""
    TEXT = "text"
    PDF = "pdf"
    MARKDOWN = "markdown"
    URL = "url"


class DocumentBase(BaseModel):
    """文档基础信息"""
    title: str = Field(..., description="文档标题")
    content: str = Field(..., description="文档内容")
    doc_type: DocumentType = Field(default=DocumentType.TEXT, description="文档类型")
    source: Optional[str] = Field(None, description="来源")
    metadata: Optional[dict] = Field(default_factory=dict, description="元数据")


class DocumentCreate(DocumentBase):
    """创建文档"""
    pass


class DocumentResponse(DocumentBase):
    """文档响应"""
    id: str
    chunk_count: int
    created_at: datetime
    updated_at: datetime


class DocumentChunk(BaseModel):
    """文档分块"""
    id: str
    document_id: str
    content: str
    chunk_index: int
    metadata: Optional[dict] = None


class QueryRequest(BaseModel):
    """查询请求"""
    query: str = Field(..., description="查询内容")
    top_k: int = Field(default=5, description="返回数量")
    filter_doc_ids: Optional[List[str]] = Field(None, description="过滤文档ID")


class QueryResponse(BaseModel):
    """查询响应"""
    query: str
    answer: str
    sources: List[dict]
    confidence: float


class SourceInfo(BaseModel):
    """来源信息"""
    document_id: str
    document_title: str
    chunk_content: str
    similarity: float
    page: Optional[int] = None