from dataclasses import dataclass, field
import re

import tiktoken

from app.config import settings


@dataclass
class ChunkInfo:
    index: int
    text: str
    token_count: int


class ChineseTextSplitter:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100, min_chunk_size: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self._encoder = tiktoken.get_encoding("cl100k_base")

    def _count_tokens(self, text: str) -> int:
        return len(self._encoder.encode(text))

    def split(self, text: str) -> list[ChunkInfo]:
        text = self._clean(text)
        if not text:
            return []

        paragraphs = self._split_paragraphs(text)
        chunks = []
        for para in paragraphs:
            para_tokens = self._count_tokens(para)
            if para_tokens <= self.chunk_size:
                chunks.append(para)
            else:
                chunks.extend(self._split_long_paragraph(para))
        chunks = self._merge_short_chunks(chunks)

        result = []
        for i, chunk_text in enumerate(chunks):
            tc = self._count_tokens(chunk_text)
            if tc >= self.min_chunk_size:
                result.append(ChunkInfo(index=i, text=chunk_text, token_count=tc))
        return result

    def _clean(self, text: str) -> str:
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _split_paragraphs(self, text: str) -> list[str]:
        return [p.strip() for p in re.split(r'\n\n+', text) if p.strip()]

    def _split_long_paragraph(self, paragraph: str) -> list[str]:
        sentences = re.split(r'(?<=[。！？；])', paragraph)
        chunks = []
        current = ""

        for sent in sentences:
            tentative = current + sent
            if self._count_tokens(tentative) > self.chunk_size and current:
                chunks.append(current)
                current = sent
            else:
                current = tentative

        if current:
            current_tokens = self._count_tokens(current)
            if current_tokens <= self.chunk_size:
                chunks.append(current)
            else:
                chunks.extend(self._split_by_tokens(current))
        return chunks

    def _split_by_tokens(self, text: str) -> list[str]:
        tokens = self._encoder.encode(text)
        chunks = []
        start = 0
        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self._encoder.decode(chunk_tokens)
            chunks.append(chunk_text)
            start = end - self.chunk_overlap
            if start >= len(tokens):
                break
        return chunks

    def _merge_short_chunks(self, chunks: list[str]) -> list[str]:
        if not chunks:
            return chunks
        merged = []
        buffer = ""
        for ch in chunks:
            tentative = buffer + ch if buffer else ch
            if self._count_tokens(tentative) <= self.chunk_size:
                buffer = tentative
            else:
                if buffer:
                    merged.append(buffer)
                buffer = ch
        if buffer:
            merged.append(buffer)
        return merged
