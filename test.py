#!/usr/bin/env python3
"""
测试脚本 - 验证项目功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有模块导入"""
    print("测试模块导入...")
    
    try:
        from models.memory import MemoryType, MemoryCreate, MemoryResponse
        print("✓ models.memory 导入成功")
    except Exception as e:
        print(f"✗ models.memory 导入失败: {e}")
    
    try:
        from models.knowledge import DocumentType, DocumentCreate, QueryRequest
        print("✓ models.knowledge 导入成功")
    except Exception as e:
        print(f"✗ models.knowledge 导入失败: {e}")
    
    try:
        from utils.config import config
        print("✓ utils.config 导入成功")
    except Exception as e:
        print(f"✗ utils.config 导入失败: {e}")
    
    try:
        from core.vectorstore import vector_store
        print("✓ core.vectorstore 导入成功")
    except Exception as e:
        print(f"✗ core.vectorstore 导入失败: {e}")
    
    try:
        from core.embeddings import embedding_service
        print("✓ core.embeddings 导入成功")
    except Exception as e:
        print(f"✗ core.embeddings 导入失败: {e}")
    
    try:
        from core.memory import memory_manager
        print("✓ core.memory 导入成功")
    except Exception as e:
        print(f"✗ core.memory 导入失败: {e}")
    
    try:
        from core.rag import rag_service
        print("✓ core.rag 导入成功")
    except Exception as e:
        print(f"✗ core.rag 导入失败: {e}")
    
    try:
        from core.detector import hallucination_detector
        print("✓ core.detector 导入成功")
    except Exception as e:
        print(f"✗ core.detector 导入失败: {e}")
    
    print("模块导入测试完成\n")


def test_vectorstore():
    """测试向量数据库"""
    print("测试向量数据库...")
    
    from core.vectorstore import vector_store
    
    # 测试添加
    vector_store.add(
        collection_name="test",
        ids=["test1", "test2"],
        documents=["这是测试文档1", "这是测试文档2"]
    )
    print("✓ 添加文档成功")
    
    # 测试查询
    results = vector_store.query(
        collection_name="test",
        query_text="测试",
        n_results=2
    )
    print(f"✓ 查询成功，找到 {len(results['ids'][0])} 个结果")
    
    # 测试删除
    vector_store.delete(
        collection_name="test",
        ids=["test1", "test2"]
    )
    print("✓ 删除文档成功")
    
    print("向量数据库测试完成\n")


def test_memory():
    """测试记忆管理"""
    print("测试记忆管理...")
    
    from core.memory import memory_manager
    from models.memory import MemoryCreate, MemoryType, MemorySearch
    
    # 测试保存
    memory = memory_manager.save(MemoryCreate(
        memory_type=MemoryType.USER_PREFERENCE,
        content="用户喜欢简洁的回答风格",
        importance=0.8
    ))
    print(f"✓ 保存记忆成功，ID: {memory.id}")
    
    # 测试搜索
    results = memory_manager.search(MemorySearch(
        query="回答风格",
        limit=5
    ))
    print(f"✓ 搜索成功，找到 {len(results)} 条记忆")
    
    # 测试删除
    success = memory_manager.delete(memory.id)
    print(f"✓ 删除{'成功' if success else '失败'}")
    
    print("记忆管理测试完成\n")


def main():
    print("=" * 50)
    print("Agent Memory Manager - 测试脚本")
    print("=" * 50)
    print()
    
    # 测试导入
    test_imports()
    
    # 测试向量数据库
    test_vectorstore()
    
    # 测试记忆管理
    from utils.config import config
    if config.OPENAI_API_KEY:
        test_memory()
    else:
        print("跳过记忆管理测试（未配置OPENAI_API_KEY）\n")
    
    print("=" * 50)
    print("所有测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()