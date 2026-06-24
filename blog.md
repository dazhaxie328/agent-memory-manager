# 我做了一个Agent记忆管理工具，解决了AI Agent的三大痛点

## 背景

最近几个月，我一直在深度使用AI Agent（主要是Hermes Agent），用它来写代码、做研究、管理项目。

用着用着，我发现了一个很烦的问题：**Agent记不住我**。

每次开新对话，我都要重新介绍自己：
- "我是做Web3的"
- "我喜欢简洁的回答风格"
- "我之前跟你说过那个项目..."

更烦的是，Agent还会**编造信息**。有一次我问它某个项目的TVL，它信誓旦旦地说了一个数字，我一查，完全是编的。

还有就是**决策不透明**。Agent给出一个建议，我问它为什么，它说"根据分析"，但我不知道它分析了什么。

这三个问题，我相信所有深度使用AI Agent的人都遇到过：
1. **记不住** —— 每次对话都是新的
2. **容易幻觉** —— 会编造不存在的信息
3. **不透明** —— 不知道为什么这么回答

所以，我做了一个工具来解决这些问题：**Agent Memory Manager**。

## 项目介绍

Agent Memory Manager 是一个Agent记忆+知识库管理工具，核心功能：

### 1. 长期记忆

用向量数据库（ChromaDB）存储Agent的记忆，包括：
- 用户偏好（"喜欢简洁回答"）
- 对话历史（"之前讨论过XX项目"）
- 事实知识（"用户的生日是XX"）

Agent回答问题时，会先检索相关记忆，然后基于记忆回答。

这样，Agent就"记住"你了。

### 2. 知识库管理

你可以导入文档（文本、PDF、Markdown），系统会自动：
- 分块（Chunking）
- 向量化（Embedding）
- 存储到向量数据库

Agent回答问题时，会从知识库检索相关内容，然后基于真实数据回答。

这样，Agent就不会编造信息了。

### 3. RAG查询

RAG（Retrieval Augmented Generation）是检索增强生成的缩写。

简单说就是：
1. 用户提问
2. 系统从知识库检索相关内容
3. 把检索到的内容 + 用户问题一起发给LLM
4. LLM基于真实内容回答

这样，Agent的回答就有依据了。

### 4. 幻觉检测

即使有了RAG，Agent还是可能编造信息。

所以，我加了一个幻觉检测模块：
- 输入：AI的回答 + 参考资料
- 输出：幻觉分数、编造的声明、有依据的声明

用LLM来评估LLM的回答，有点"以毒攻毒"的意思。

## 技术实现

### 技术栈

- **Python 3.10+** —— 主语言
- **LangChain** —— Agent框架
- **ChromaDB** —— 向量数据库
- **OpenAI API** —— AI模型
- **FastAPI** —— 后端API
- **Streamlit** —— 前端界面

### 架构设计

```
┌─────────────────────────────────────────────┐
│                用户界面 (Streamlit)           │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│              API层 (FastAPI)                  │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│              服务层                           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │ 记忆管理 │ │ 知识库  │ │ 幻觉检测 │        │
│  └────┬────┘ └────┬────┘ └────┬────┘        │
│       │           │           │              │
└───────┼───────────┼───────────┼──────────────┘
        │           │           │
┌───────▼───────────▼───────────▼──────────────┐
│              数据层                           │
│  ┌─────────────┐ ┌─────────────┐             │
│  │  ChromaDB   │ │   OpenAI    │             │
│  │ (向量数据库) │ │  (Embedding) │             │
│  └─────────────┘ └─────────────┘             │
└──────────────────────────────────────────────┘
```

### 核心代码

#### 1. 记忆管理

```python
class MemoryManager:
    def save(self, memory: MemoryCreate) -> MemoryResponse:
        # 生成向量
        embedding = embedding_service.embed_text(memory.content)
        
        # 保存到向量数据库
        vector_store.add(
            collection_name=self.collection_name,
            ids=[memory_id],
            documents=[memory.content],
            embeddings=[embedding],
            metadatas=[metadata]
        )
    
    def search(self, search: MemorySearch) -> List[MemoryResponse]:
        # 生成查询向量
        query_embedding = embedding_service.embed_text(search.query)
        
        # 查询相似记忆
        results = vector_store.query(
            collection_name=self.collection_name,
            query_text=search.query,
            query_embedding=query_embedding,
            n_results=search.limit
        )
```

#### 2. RAG查询

```python
class RAGService:
    def query(self, request: QueryRequest) -> QueryResponse:
        # 检索相关文档
        results = vector_store.query(
            collection_name=self.collection_name,
            query_text=request.query,
            n_results=request.top_k
        )
        
        # 生成回答
        context = "\n\n".join(results["documents"][0])
        answer = self._generate_answer(request.query, context)
        
        return QueryResponse(
            query=request.query,
            answer=answer,
            sources=sources,
            confidence=confidence
        )
```

#### 3. 幻觉检测

```python
class HallucinationDetector:
    def detect(self, answer: str, context: str) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_template("""
你是一个AI回答质量评估专家。请分析以下回答是否存在幻觉。

参考资料：
{context}

AI回答：
{answer}

请评估：
1. 事实准确性
2. 信息来源
3. 推理合理性
4. 编造检测
        """)
        
        response = self.llm.invoke(prompt.format(...))
        return json.loads(response.content)
```

## 遇到的挑战

### 1. 记忆的检索准确性

一开始，记忆检索的准确性不高。用户问"我喜欢什么风格"，系统检索出来的却是无关的记忆。

解决方案：
- 优化Embedding模型选择
- 调整相似度阈值
- 增加记忆的重要性权重

### 2. 幻觉检测的准确性

幻觉检测本身也可能"幻觉"——用LLM检测LLM，有点套娃的意思。

解决方案：
- 设计更详细的评估prompt
- 多维度评估（事实准确性、来源覆盖度、推理质量）
- 设置置信度阈值

### 3. 知识库的分块策略

文档分块太大，检索不精确；分块太小，丢失上下文。

解决方案：
- 使用RecursiveCharacterTextSplitter
- 设置合理的chunk_size和chunk_overlap
- 保留文档元数据

## 总结

这个项目的核心价值：

1. **解决真实痛点** —— 不是为了做而做，是真正解决了使用Agent时遇到的问题
2. **技术栈主流** —— ChromaDB、LangChain、RAG，都是当前AI领域的热门技术
3. **完整工程实现** —— 前后端 + AI + 数据库，展示了全栈能力
4. **可扩展性强** —— 可以接入不同的LLM、不同的向量数据库

如果你也在用AI Agent，或者在做AI相关的开发，欢迎试试这个工具。

项目地址：https://github.com/dazhaxie328/agent-memory-manager

---

*作者：王维 | Web3/AI从业者 | 公众号：小果叮*