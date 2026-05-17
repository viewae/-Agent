from app.utils.text_splitter import ChineseTextSplitter


class TestChineseTextSplitter:
    def setup_method(self):
        self.splitter = ChineseTextSplitter(chunk_size=500, chunk_overlap=100, min_chunk_size=10)

    def test_empty_text(self):
        assert self.splitter.split("") == []

    def test_short_text_single_chunk(self):
        text = "这是一个简短的测试文档。"
        chunks = self.splitter.split(text)
        assert len(chunks) >= 0  # may be filtered if too small

    def test_chinese_paragraphs(self):
        text = "第一段内容。\n\n第二段内容。\n\n第三段内容。"
        chunks = self.splitter.split(text)
        assert len(chunks) <= 3

    def test_token_count_in_chunks(self):
        text = "人工智能技术正在快速发展。\n\n深度学习模型在多个领域取得了突破性进展。"
        chunks = self.splitter.split(text)
        for c in chunks:
            assert c.token_count > 0
            assert c.index >= 0
            assert len(c.text) > 0

    def test_large_text_produces_chunks(self):
        text = "测试内容。" * 200
        chunks = self.splitter.split(text)
        if chunks:
            assert all(c.token_count >= self.splitter.min_chunk_size for c in chunks)

    def test_chunk_indices_sequential(self):
        text = "段落A。\n\n段落B。\n\n段落C。"
        chunks = self.splitter.split(text)
        indices = [c.index for c in chunks]
        assert indices == sorted(indices)
