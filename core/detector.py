"""
幻觉检测服务
"""

from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from utils.config import config


class HallucinationDetector:
    """幻觉检测服务"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.LLM_MODEL,
            openai_api_key=config.OPENAI_API_KEY,
            temperature=0
        )
    
    def detect(self, answer: str, context: str) -> Dict[str, Any]:
        """检测回答中的幻觉"""
        prompt = ChatPromptTemplate.from_template("""
你是一个AI回答质量评估专家。请分析以下回答是否存在幻觉（编造信息）。

参考资料：
{context}

AI回答：
{answer}

请从以下维度评估：

1. **事实准确性** - 回答中的事实是否与参考资料一致
2. **信息来源** - 回答中的信息是否能在参考资料中找到
3. **推理合理性** - 回答中的推理是否合理
4. **编造检测** - 是否有编造的信息

请用JSON格式返回评估结果：
{{
    "hallucination_score": 0-100的数字，越高表示幻觉越严重,
    "is_hallucination": true/false,
    "factual_accuracy": 0-100的数字,
    "source_coverage": 0-100的数字,
    "reasoning_quality": 0-100的数字,
    "hallucinated_claims": ["编造的声明1", "编造的声明2"],
    "supported_claims": ["有依据的声明1", "有依据的声明2"],
    "explanation": "详细解释"
}}""")
        
        try:
            response = self.llm.invoke(
                prompt.format(context=context, answer=answer)
            )
            
            # 解析JSON
            import json
            result = json.loads(response.content)
            
            return {
                "hallucination_score": result.get("hallucination_score", 0),
                "is_hallucination": result.get("is_hallucination", False),
                "factual_accuracy": result.get("factual_accuracy", 100),
                "source_coverage": result.get("source_coverage", 100),
                "reasoning_quality": result.get("reasoning_quality", 100),
                "hallucinated_claims": result.get("hallucinated_claims", []),
                "supported_claims": result.get("supported_claims", []),
                "explanation": result.get("explanation", "")
            }
        except Exception as e:
            return {
                "hallucination_score": 0,
                "is_hallucination": False,
                "factual_accuracy": 100,
                "source_coverage": 100,
                "reasoning_quality": 100,
                "hallucinated_claims": [],
                "supported_claims": [],
                "explanation": f"检测失败: {str(e)}"
            }
    
    def detect_batch(self, answers: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """批量检测"""
        results = []
        for item in answers:
            result = self.detect(item["answer"], item["context"])
            results.append(result)
        return results


# 创建全局实例
hallucination_detector = HallucinationDetector()