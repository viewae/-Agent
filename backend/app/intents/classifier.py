import logging

from app.intents import IntentType
from app.utils.llm_client import get_chat_client, get_chat_model

logger = logging.getLogger(__name__)

KEYWORD_RULES = [
    (IntentType.SUMMARIZE, ["总结", "摘要", "概括", "归纳", "简述", "概述"]),
    (IntentType.EXTRACT, ["提取", "列出", "找出", "抽取", "所有", "关键信息"]),
    (IntentType.COMPARE, ["对比", "比较", "区别", "差异", "异同", "哪个"]),
    (IntentType.TRANSLATE, ["翻译", "translate", "译成"]),
]

SYSTEM_PROMPT = """你是一个意图分类器。将用户输入分类为以下类型之一:
- qa: 基于文档内容的具体问答
- summarize: 总结/概括文档
- extract: 提取特定信息或列表
- compare: 对比两个或多个文档
- translate: 翻译内容
- general: 通用对话，不涉及文档

只回复类型标签，不要解释。"""


class IntentClassifier:
    def __init__(self):
        self._client = get_chat_client()
        self._model = get_chat_model()

    def classify(self, query: str) -> IntentType:
        for intent, keywords in KEYWORD_RULES:
            if any(kw in query for kw in keywords):
                return intent

        try:
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": query},
                ],
                temperature=0,
                max_tokens=10,
            )
            label = resp.choices[0].message.content.strip().lower()
            for intent in IntentType:
                if intent.value in label:
                    return intent
        except Exception:
            logger.exception("Intent classification failed, falling back to qa")
        return IntentType.QA
