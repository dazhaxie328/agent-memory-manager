# Agent Memory Manager

Agent记忆+知识库管理工具，让AI Agent真正"记住"用户，基于真实知识回答。

## 解决的问题

| 问题 | 解决方案 |
|------|----------|
| Agent记不住 | 向量数据库存储长期记忆 |
| Agent容易幻觉 | RAG基于真实知识回答 |
| 决策不透明 | 回答溯源，显示引用来源 |
| 知识无法管理 | 可视化知识库管理界面 |

## 核心功能

- 🧠 **长期记忆** —— Agent记住用户偏好、历史对话
- 📚 **知识库管理** —— 导入文档，Agent基于真实数据回答
- 🔍 **记忆检索** —— 查看Agent记住了什么，可编辑删除
- 📎 **回答溯源** —— 显示Agent回答引用了哪些知识
- ⚠️ **幻觉检测** —— 标记Agent回答中可能编造的内容

## 技术栈

- **Python 3.10+**
- **LangChain** —— Agent框架
- **ChromaDB** —— 向量数据库
- **OpenAI API** —— AI模型
- **FastAPI** —— 后端API
- **Streamlit** —— 前端界面

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 启动后端
python -m uvicorn api.main:app --reload

# 启动前端
streamlit run app.py
```

## 项目结构

```
agent-memory-manager/
├── app.py                   # Streamlit 前端
├── api/
│   ├── main.py             # FastAPI 后端
│   └── services/
│       ├── memory.py       # 记忆管理服务
│       ├── knowledge.py    # 知识库服务
│       ├── rag.py          # RAG检索服务
│       └── detector.py     # 幻觉检测服务
├── core/
│   ├── embeddings.py       # 向量化处理
│   ├── vectorstore.py      # 向量数据库
│   └── llm.py             # LLM封装
├── models/
│   ├── memory.py           # 记忆数据模型
│   └── knowledge.py        # 知识数据模型
├── utils/
│   ├── config.py           # 配置管理
│   └── helpers.py          # 工具函数
├── data/
│   └── chroma/             # ChromaDB数据
├── requirements.txt
├── .env.example
└── README.md
```

## 使用示例

```python
from core.memory import MemoryManager
from core.rag import RAGService

# 初始化
memory = MemoryManager()
rag = RAGService()

# 存储记忆
memory.save("user_preference", "用户喜欢简洁的回答风格")

# 检索相关记忆
memories = memory.search("回答风格", limit=5)

# 基于知识库回答
answer = rag.query("什么是向量数据库？")
print(answer.response)
print(answer.sources)  # 显示引用来源
```

## 面试亮点

1. **深度理解Agent痛点** —— 从实际使用经验出发
2. **向量数据库应用** —— ChromaDB + Embedding
3. **RAG实现** —— 检索增强生成
4. **幻觉检测** —— AI安全和可靠性
5. **全栈能力** —— 前后端 + AI + 数据库

## License

MIT