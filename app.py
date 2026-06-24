"""
Streamlit前端界面
"""

import streamlit as st
import requests
import json
from typing import Dict, Any, List

# API配置
API_BASE_URL = "http://localhost:8000"

# 页面配置
st.set_page_config(
    page_title="Agent Memory Manager",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00ff88;
        text-align: center;
        margin-bottom: 2rem;
    }
    .memory-card {
        background-color: #1e1e1e;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #333;
        margin-bottom: 1rem;
    }
    .tag {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    .tag-memory { background-color: #4a9eff; color: white; }
    .tag-knowledge { background-color: #00c853; color: white; }
    .tag-warning { background-color: #ff9800; color: white; }
    .tag-error { background-color: #f44336; color: white; }
</style>
""", unsafe_allow_html=True)


def api_get(endpoint: str) -> Dict[str, Any]:
    """GET请求"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=30)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def api_post(endpoint: str, data: dict) -> Dict[str, Any]:
    """POST请求"""
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=60)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def api_delete(endpoint: str) -> Dict[str, Any]:
    """DELETE请求"""
    try:
        response = requests.delete(f"{API_BASE_URL}{endpoint}", timeout=30)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def main():
    # 标题
    st.markdown('<h1 class="main-header">🧠 Agent Memory Manager</h1>', unsafe_allow_html=True)
    st.markdown("### Agent记忆+知识库管理工具")
    
    # 侧边栏
    with st.sidebar:
        st.header("设置")
        
        # API配置
        api_url = st.text_input("API地址", value=API_BASE_URL)
        if api_url != API_BASE_URL:
            global API_BASE_URL
            API_BASE_URL = api_url
        
        st.divider()
        
        # 统计信息
        st.header("📊 统计")
        
        memory_count = api_get("/memory/stats/count")
        if "count" in memory_count:
            st.metric("记忆数量", memory_count["count"])
        
        knowledge_count = api_get("/knowledge/stats/count")
        if "count" in knowledge_count:
            st.metric("知识块数量", knowledge_count["count"])
    
    # 主内容区
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧠 记忆管理", "📚 知识库", "🔍 RAG查询", "⚠️ 幻觉检测", "📖 使用说明"
    ])
    
    with tab1:
        st.subheader("🧠 记忆管理")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 添加记忆")
            
            memory_type = st.selectbox(
                "记忆类型",
                options=["user_preference", "conversation", "fact", "instruction", "context"],
                format_func=lambda x: {
                    "user_preference": "用户偏好",
                    "conversation": "对话历史",
                    "fact": "事实知识",
                    "instruction": "指令",
                    "context": "上下文"
                }[x]
            )
            
            memory_content = st.text_area("记忆内容", height=100)
            memory_importance = st.slider("重要性", 0.0, 1.0, 0.5)
            
            if st.button("💾 保存记忆", use_container_width=True):
                if memory_content:
                    result = api_post("/memory", {
                        "memory_type": memory_type,
                        "content": memory_content,
                        "importance": memory_importance
                    })
                    if "id" in result:
                        st.success(f"记忆已保存！ID: {result['id']}")
                    else:
                        st.error(f"保存失败: {result.get('error', '未知错误')}")
                else:
                    st.error("请输入记忆内容")
        
        with col2:
            st.markdown("#### 搜索记忆")
            
            search_query = st.text_input("搜索关键词")
            search_type = st.selectbox(
                "过滤类型",
                options=[None, "user_preference", "conversation", "fact", "instruction", "context"],
                format_func=lambda x: "全部" if x is None else {
                    "user_preference": "用户偏好",
                    "conversation": "对话历史",
                    "fact": "事实知识",
                    "instruction": "指令",
                    "context": "上下文"
                }[x]
            )
            
            if st.button("🔍 搜索", use_container_width=True):
                if search_query:
                    result = api_post("/memory/search", {
                        "query": search_query,
                        "memory_type": search_type,
                        "limit": 10
                    })
                    if isinstance(result, list):
                        st.session_state["search_results"] = result
                        st.success(f"找到 {len(result)} 条记忆")
                    else:
                        st.error(f"搜索失败: {result.get('error', '未知错误')}")
                else:
                    st.error("请输入搜索关键词")
        
        # 显示搜索结果
        if "search_results" in st.session_state:
            st.divider()
            st.subheader("搜索结果")
            
            for memory in st.session_state["search_results"]:
                with st.container():
                    st.markdown(f"""
                    <div class="memory-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span class="tag tag-memory">{memory.get('memory_type', 'unknown')}</span>
                            <span style="color: #888; font-size: 0.8rem;">相似度: {memory.get('similarity', 0):.2%}</span>
                        </div>
                        <p style="margin: 0;">{memory.get('content', '')}</p>
                        <div style="margin-top: 0.5rem; color: #888; font-size: 0.8rem;">
                            重要性: {memory.get('importance', 0):.2f} | 
                            创建时间: {memory.get('created_at', '')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"删除", key=f"delete_{memory.get('id')}"):
                            result = api_delete(f"/memory/{memory.get('id')}")
                            if "message" in result:
                                st.success("删除成功")
                                st.rerun()
                            else:
                                st.error(f"删除失败: {result.get('error', '未知错误')}")
    
    with tab2:
        st.subheader("📚 知识库管理")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 添加文档")
            
            doc_title = st.text_input("文档标题")
            doc_type = st.selectbox(
                "文档类型",
                options=["text", "pdf", "markdown", "url"],
                format_func=lambda x: {
                    "text": "纯文本",
                    "pdf": "PDF",
                    "markdown": "Markdown",
                    "url": "URL"
                }[x]
            )
            
            doc_content = st.text_area("文档内容", height=200)
            doc_source = st.text_input("来源（可选）")
            
            if st.button("📄 添加文档", use_container_width=True):
                if doc_title and doc_content:
                    result = api_post("/knowledge", {
                        "title": doc_title,
                        "content": doc_content,
                        "doc_type": doc_type,
                        "source": doc_source
                    })
                    if "id" in result:
                        st.success(f"文档已添加！ID: {result['id']}")
                    else:
                        st.error(f"添加失败: {result.get('error', '未知错误')}")
                else:
                    st.error("请输入标题和内容")
        
        with col2:
            st.markdown("#### 文档列表")
            
            if st.button("🔄 刷新列表"):
                st.session_state["refresh_docs"] = True
            
            if st.session_state.get("refresh_docs", True):
                docs = api_get("/knowledge")
                if isinstance(docs, list):
                    st.session_state["documents"] = docs
                
                if "documents" in st.session_state:
                    for doc in st.session_state["documents"]:
                        st.markdown(f"""
                        <div class="memory-card">
                            <h4 style="margin: 0 0 0.5rem 0;">{doc.get('title', '未知')}</h4>
                            <div style="color: #888; font-size: 0.8rem;">
                                类型: {doc.get('doc_type', '未知')} | 
                                分块数: {doc.get('chunk_count', 0)}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"删除文档", key=f"delete_doc_{doc.get('id')}"):
                            result = api_delete(f"/knowledge/{doc.get('id')}")
                            if "message" in result:
                                st.success("删除成功")
                                st.rerun()
                            else:
                                st.error(f"删除失败: {result.get('error', '未知错误')}")
    
    with tab3:
        st.subheader("🔍 RAG查询")
        
        query = st.text_area("输入查询", height=100)
        top_k = st.slider("返回结果数", 1, 10, 5)
        
        if st.button("🔍 查询", use_container_width=True, type="primary"):
            if query:
                with st.spinner("正在查询..."):
                    result = api_post("/query", {
                        "query": query,
                        "top_k": top_k
                    })
                
                if "answer" in result:
                    st.session_state["query_result"] = result
                else:
                    st.error(f"查询失败: {result.get('error', '未知错误')}")
            else:
                st.error("请输入查询内容")
        
        # 显示查询结果
        if "query_result" in st.session_state:
            result = st.session_state["query_result"]
            
            st.divider()
            st.subheader("查询结果")
            
            # 回答
            st.markdown("#### 💬 回答")
            st.write(result.get("answer", ""))
            
            # 置信度
            confidence = result.get("confidence", 0)
            color = "green" if confidence > 0.7 else "orange" if confidence > 0.4 else "red"
            st.markdown(f"**置信度:** :{color}[{confidence:.2%}]")
            
            # 来源
            sources = result.get("sources", [])
            if sources:
                st.markdown("#### 📎 引用来源")
                for i, source in enumerate(sources):
                    st.markdown(f"""
                    <div class="memory-card">
                        <h4 style="margin: 0 0 0.5rem 0;">{source.get('document_title', '未知')}</h4>
                        <p style="margin: 0; color: #888; font-size: 0.9rem;">{source.get('chunk_content', '')}</p>
                        <div style="margin-top: 0.5rem; color: #888; font-size: 0.8rem;">
                            相似度: {source.get('similarity', 0):.2%}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 幻觉检测
            if st.button("⚠️ 检测幻觉"):
                with st.spinner("正在检测..."):
                    detect_result = api_post("/detect", {
                        "answer": result.get("answer", ""),
                        "context": "\n".join([s.get("chunk_content", "") for s in sources])
                    })
                
                if "hallucination_score" in detect_result:
                    st.session_state["detect_result"] = detect_result
    
    with tab4:
        st.subheader("⚠️ 幻觉检测")
        
        answer = st.text_area("输入AI回答", height=100)
        context = st.text_area("输入参考资料", height=100)
        
        if st.button("🔍 检测幻觉", use_container_width=True, type="primary"):
            if answer and context:
                with st.spinner("正在检测..."):
                    result = api_post("/detect", {
                        "answer": answer,
                        "context": context
                    })
                
                if "hallucination_score" in result:
                    st.session_state["detect_result"] = result
                else:
                    st.error(f"检测失败: {result.get('error', '未知错误')}")
            else:
                st.error("请输入回答和参考资料")
        
        # 显示检测结果
        if "detect_result" in st.session_state:
            result = st.session_state["detect_result"]
            
            st.divider()
            st.subheader("检测结果")
            
            # 幻觉分数
            score = result.get("hallucination_score", 0)
            color = "green" if score < 30 else "orange" if score < 60 else "red"
            st.markdown(f"**幻觉分数:** :{color}[{score}/100]")
            
            # 是否存在幻觉
            is_hallucination = result.get("is_hallucination", False)
            if is_hallucination:
                st.error("⚠️ 检测到幻觉！")
            else:
                st.success("✅ 未检测到明显幻觉")
            
            # 详细指标
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("事实准确性", f"{result.get('factual_accuracy', 0)}/100")
            with col2:
                st.metric("来源覆盖度", f"{result.get('source_coverage', 0)}/100")
            with col3:
                st.metric("推理质量", f"{result.get('reasoning_quality', 0)}/100")
            
            # 编造的声明
            hallucinated = result.get("hallucinated_claims", [])
            if hallucinated:
                st.markdown("#### ❌ 编造的声明")
                for claim in hallucinated:
                    st.write(f"- {claim}")
            
            # 有依据的声明
            supported = result.get("supported_claims", [])
            if supported:
                st.markdown("#### ✅ 有依据的声明")
                for claim in supported:
                    st.write(f"- {claim}")
            
            # 解释
            explanation = result.get("explanation", "")
            if explanation:
                st.markdown("#### 💬 详细解释")
                st.write(explanation)
    
    with tab5:
        st.subheader("📖 使用说明")
        
        st.markdown("""
        ### 功能介绍
        
        **Agent Memory Manager** 是一个Agent记忆+知识库管理工具，解决AI Agent的三大痛点：
        
        1. 🧠 **记不住** —— 用向量数据库存储长期记忆
        2. 📚 **容易幻觉** —— 用RAG基于真实知识回答
        3. ⚠️ **不透明** —— 显示回答来源，检测幻觉
        
        ### 核心功能
        
        #### 1. 记忆管理
        - 存储用户偏好、对话历史、事实知识
        - 基于语义搜索检索相关记忆
        - 支持编辑和删除
        
        #### 2. 知识库管理
        - 导入文档，自动分块和向量化
        - 支持多种文档格式
        - 可视化管理界面
        
        #### 3. RAG查询
        - 基于知识库回答问题
        - 显示引用来源
        - 计算置信度
        
        #### 4. 幻觉检测
        - 检测AI回答中的编造信息
        - 评估事实准确性
        - 标记可疑声明
        
        ### 面试亮点
        
        1. **深度理解Agent痛点** —— 从实际使用经验出发
        2. **向量数据库应用** —— ChromaDB + Embedding
        3. **RAG实现** —— 检索增强生成
        4. **幻觉检测** —— AI安全和可靠性
        5. **全栈能力** —— 前后端 + AI + 数据库
        """)


if __name__ == "__main__":
    main()