"""
RAG检索服务
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from core.vectorstore import vector_store
from core.embeddings import embedding_service
from models.knowledge import (
    DocumentType, DocumentCreate, DocumentResponse,
    QueryRequest, QueryResponse, SourceInfo
)
from utils.config import config


class RAGService:
    """RAG检索服务"""
    
    COLLECTION_NAME = "knowledge"
    
    def __init__(self):
        self.collection_name = config.CHROMA_COLLECTION_NAME + "_knowledge"
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.RAG_CHUNK_SIZE,
            chunk_overlap=config.RAG_CHUNK_OVERLAP,
            length_function=len,
        )
        self.llm = ChatOpenAI(
            model=config.LLM_MODEL,
            openai_api_key=config.OPENAI_API_KEY,
            temperature=0
        )
    
    def add_document(self, doc: DocumentCreate) -> DocumentResponse:
        """添加文档"""
        # 生成文档ID
        doc_id = str(uuid.uuid4())
        
        # 分块
        chunks = self.text_splitter.split_text(doc.content)
        
        # 生成向量
        embeddings = embedding_service.embed_texts(chunks)
        
        # 准备数据
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "document_id": doc_id,
                "document_title": doc.title,
                "doc_type": doc.doc_type.value,
                "source": doc.source or "",
                "chunk_index": i,
                "created_at": datetime.now().isoformat(),
                **(doc.metadata or {})
            }
            for i in range(len(chunks))
        ]
        
        # 保存到向量数据库
        vector_store.add(
            collection_name=self.collection_name,
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        return DocumentResponse(
            id=doc_id,
            title=doc.title,
            content=doc.content,
            doc_type=doc.doc_type,
            source=doc.source,
            metadata=doc.metadata,
            chunk_count=len(chunks),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def query(self, request: QueryRequest) -> QueryResponse:
        """查询"""
        # 生成查询向量
        query_embedding = embedding_service.embed_text(request.query)
        
        # 构建过滤条件
        where = None
        if request.filter_doc_ids:
            where = {"document_id": {"$in": request.filter_doc_ids}}
        
        # 检索相关文档
        results = vector_store.query(
            collection_name=self.collection_name,
            query_text=request.query,
            query_embedding=query_embedding,
            n_results=request.top_k,
            where=where
        )
        
        # 提取来源信息
        sources = []
        context_parts = []
        
        if results and results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0
                similarity = 1 - distance
                
                sources.append({
                    "document_id": metadata.get("document_id", ""),
                    "document_title": metadata.get("document_title", ""),
                    "chunk_content": results["documents"][0][i][:200] + "...",
                    "similarity": round(similarity, 3)
                })
                
                context_parts.append(results["documents"][0][i])
        
        # 生成回答
        context = "\n\n---\n\n".join(context_parts)
        answer = self._generate_answer(request.query, context)
        
        # 计算置信度
        confidence = sum(s["similarity"] for s in sources) / len(sources) if sources else 0
        
        return QueryResponse(
            query=request.query,
            answer=answer,
            sources=sources,
            confidence=round(confidence, 3)
        )
    
    def _generate_answer(self, query: str, context: str) -> str:
        """生成回答"""
        prompt = ChatPromptTemplate.from_template("""
你是一个AI助手。请基于以下参考资料回答用户的问题。

参考资料：
{context}

用户问题：{query}

要求：
1. 只基于参考资料回答，不要编造信息
2. 如果参考资料中没有相关信息，请明确说明
3. 回答要简洁明了
4. 在回答末尾注明引用的来源

回答：
""")
        
        try:
            response = self.llm.invoke(
                prompt.format(context=context, query=query)
            )
            return response.content
        except Exception as e:
            return f"生成回答时出错: {str(e)}"
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """获取所有文档"""
        results = vector_store.get_all(self.collection_name)
        
        documents = {}
        if results and results["metadatas"]:
            for metadata in results["metadatas"]:
                doc_id = metadata.get("document_id")
                if doc_id and doc_id not in documents:
                    documents[doc_id] = {
                        "id": doc_id,
                        "title": metadata.get("document_title", ""),
                        "doc_type": metadata.get("doc_type", ""),
                        "source": metadata.get("source", ""),
                        "created_at": metadata.get("created_at", ""),
                        "chunk_count": 1
                    }
                elif doc_id:
                    documents[doc_id]["chunk_count"] += 1
        
        return list(documents.values())
    
    def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        try:
            results = vector_store.get_all(self.collection_name)
            
            chunk_ids = []
            if results and results["metadatas"]:
                for i, metadata in enumerate(results["metadatas"]):
                    if metadata.get("document_id") == doc_id:
                        chunk_ids.append(results["ids"][i])
            
            if chunk_ids:
                vector_store.delete(
                    collection_name=self.collection_name,
                    ids=chunk_ids
                )
            return True
        except Exception:
            return False
    
    def count(self) -> int:
        """获取文档块数量"""
        return vector_store.count(self.collection_name)


# 创建全局实例
rag_service = RAGService()