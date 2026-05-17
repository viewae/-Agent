from unittest.mock import patch

from app.intents import IntentType
from app.intents.classifier import IntentClassifier


class TestIntentClassifier:
    def setup_method(self):
        self.classifier = IntentClassifier()

    def test_keyword_summarize(self):
        for kw in ["总结", "摘要", "概括", "归纳"]:
            assert self.classifier.classify(f"请{kw}这份文档") == IntentType.SUMMARIZE

    def test_keyword_extract(self):
        for kw in ["提取", "列出", "找出"]:
            assert self.classifier.classify(f"请{kw}所有日期") == IntentType.EXTRACT

    def test_keyword_compare(self):
        for kw in ["对比", "比较", "区别"]:
            assert self.classifier.classify(f"请{kw}这两个文档") == IntentType.COMPARE

    def test_keyword_translate(self):
        assert self.classifier.classify("翻译这段内容") == IntentType.TRANSLATE

    def test_default_fallback(self):
        # When no keyword matches and LLM is mocked to return unexpected
        with patch.object(self.classifier._client.chat.completions, "create") as mock_create:
            mock_create.return_value.choices = [
                type("Choice", (), {"message": type("Msg", (), {"content": "unknown"})})()
            ]
            result = self.classifier.classify("你好")
            assert result == IntentType.QA

    def test_llm_classification_qa(self):
        with patch.object(self.classifier._client.chat.completions, "create") as mock_create:
            mock_create.return_value.choices = [
                type("Choice", (), {"message": type("Msg", (), {"content": "qa"})})()
            ]
            result = self.classifier.classify("这份文档讲了什么内容")
            assert result == IntentType.QA
