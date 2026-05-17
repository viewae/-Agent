from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable

from app.intents import IntentType
from app.services.rag_service import RAGService
from app.utils.llm_client import get_chat_client, get_chat_model


class TaskExecutor(ABC):
    def __init__(self):
        self._rag = RAGService()

    @abstractmethod
    def execute(
        self,
        instruction: str,
        document_ids: list[int] | None,
        chat_history: list[dict] | None,
        steps_callback: Callable[[str], None] | None,
    ) -> str:
        ...

    def _rag_answer(self, query, document_ids, chat_history) -> str:
        result = self._rag.answer(query, document_ids, chat_history)
        return result["answer"]


class QAExecutor(TaskExecutor):
    def execute(self, instruction, document_ids, chat_history, steps_callback):
        if steps_callback:
            steps_callback("检索相关文档片段")
        answer = self._rag_answer(instruction, document_ids, chat_history)
        if steps_callback:
            steps_callback("生成回答")
        return answer


class SummarizeExecutor(TaskExecutor):
    def execute(self, instruction, document_ids, chat_history, steps_callback):
        if steps_callback:
            steps_callback("检索文档内容")
        answer = self._rag_answer(
            f"请对以下文档内容进行全面总结：{instruction}",
            document_ids, chat_history,
        )
        if steps_callback:
            steps_callback("生成总结")
        return answer


class ExtractExecutor(TaskExecutor):
    def execute(self, instruction, document_ids, chat_history, steps_callback):
        if steps_callback:
            steps_callback("检索相关信息")
        answer = self._rag_answer(
            f"请以结构化列表形式提取以下信息：{instruction}",
            document_ids, chat_history,
        )
        if steps_callback:
            steps_callback("整理提取结果")
        return answer


class CompareExecutor(TaskExecutor):
    def execute(self, instruction, document_ids, chat_history, steps_callback):
        if steps_callback:
            steps_callback("检索各文档相关内容")
        answer = self._rag_answer(
            f"请进行文档对比分析：{instruction}\n请以对比表格或分点形式呈现。",
            document_ids, chat_history,
        )
        if steps_callback:
            steps_callback("生成对比分析")
        return answer


class TranslateExecutor(TaskExecutor):
    def execute(self, instruction, document_ids, chat_history, steps_callback):
        if steps_callback:
            steps_callback("检索原文内容")
        answer = self._rag_answer(
            f"请将以下内容翻译：{instruction}",
            document_ids, chat_history,
        )
        if steps_callback:
            steps_callback("生成翻译结果")
        return answer


class GeneralExecutor(TaskExecutor):
    def __init__(self):
        super().__init__()
        self._llm_client = get_chat_client()
        self._llm_model = get_chat_model()

    def execute(self, instruction, document_ids, chat_history, steps_callback):
        if steps_callback:
            steps_callback("处理通用指令")
        messages = [{"role": "system", "content": "你是一个智能助手。"}]
        if chat_history:
            messages.extend(chat_history)
        messages.append({"role": "user", "content": instruction})
        resp = self._llm_client.chat.completions.create(
            model=self._llm_model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
        )
        return resp.choices[0].message.content


EXECUTOR_MAP: dict[IntentType, TaskExecutor] = {
    IntentType.QA: QAExecutor(),
    IntentType.SUMMARIZE: SummarizeExecutor(),
    IntentType.EXTRACT: ExtractExecutor(),
    IntentType.COMPARE: CompareExecutor(),
    IntentType.TRANSLATE: TranslateExecutor(),
    IntentType.GENERAL: GeneralExecutor(),
}
