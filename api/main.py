"""
FastAPI后端主入口
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from core.memory import memory_manager
from core.rag import rag_service
from core.detector import hallucination_detector
from models.memory import (
    MemoryCreate, MemoryResponse, MemoryUpdate, MemorySearch
)
from models.knowledge import (
    DocumentCreate, DocumentResponse, QueryRequest, QueryResponse
)

# 创建FastAPI应用
app = FastAPI(
    title="Agent Memory Manager",
    description="Agent记忆+知识库管理工具",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Agent Memory Manager API",
        "version": "1.0.0",
        "endpoints": {
            "/memory": "记忆管理",
            "/knowledge": "知识库管理",
            "/query": "RAG查询",
            "/detect": "幻觉检测"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "agent-memory-manager"}


# ============ 记忆管理 ============

@app.post("/memory", response_model=MemoryResponse)
async def create_memory(memory: MemoryCreate):
    """创建记忆"""
    try:
        return memory_manager.save(memory)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory", response_model=List[MemoryResponse])
async def get_all_memories():
    """获取所有记忆"""
    try:
        return memory_manager.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/search", response_model=List[MemoryResponse])
async def search_memories(search: MemorySearch):
    """搜索记忆"""
    try:
        return memory_manager.search(search)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/{memory_id}", response_model=MemoryResponse)
async def get_memory(memory_id: str):
    """获取单个记忆"""
    try:
        memory = memory_manager.get_by_id(memory_id)
        if not memory:
            raise HTTPException(status_code=404, detail="记忆不存在")
        return memory
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/memory/{memory_id}", response_model=MemoryResponse)
async def update_memory(memory_id: str, update: MemoryUpdate):
    """更新记忆"""
    try:
        memory = memory_manager.update(memory_id, update)
        if not memory:
            raise HTTPException(status_code=404, detail="记忆不存在")
        return memory
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/memory/{memory_id}")
async def delete_memory(memory_id: str):
    """删除记忆"""
    try:
        success = memory_manager.delete(memory_id)
        if not success:
            raise HTTPException(status_code=404, detail="记忆不存在")
        return {"message": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/stats/count")
async def get_memory_count():
    """获取记忆数量"""
    try:
        return {"count": memory_manager.count()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ 知识库管理 ============

@app.post("/knowledge", response_model=DocumentResponse)
async def add_document(doc: DocumentCreate):
    """添加文档"""
    try:
        return rag_service.add_document(doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge")
async def get_all_documents():
    """获取所有文档"""
    try:
        return rag_service.get_all_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/knowledge/{doc_id}")
async def delete_document(doc_id: str):
    """删除文档"""
    try:
        success = rag_service.delete_document(doc_id)
        if not success:
            raise HTTPException(status_code=404, detail="文档不存在")
        return {"message": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge/stats/count")
async def get_knowledge_count():
    """获取知识库块数量"""
    try:
        return {"count": rag_service.count()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ RAG查询 ============

@app.post("/query", response_model=QueryResponse)
async def query_knowledge(request: QueryRequest):
    """RAG查询"""
    try:
        return rag_service.query(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ 幻觉检测 ============

@app.post("/detect")
async def detect_hallucination(answer: str, context: str):
    """检测幻觉"""
    try:
        return hallucination_detector.detect(answer, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)