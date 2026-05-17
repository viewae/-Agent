import logging

import chardet

from app.parsers.base import BaseParser

logger = logging.getLogger(__name__)

ENCODINGS = ["utf-8", "gbk", "gb2312", "latin-1"]


class TxtParser(BaseParser):
    def extract_text(self, file_path: str) -> str:
        with open(file_path, "rb") as f:
            raw = f.read()

        detected = chardet.detect(raw)
        encoding = detected.get("encoding") if detected else None
        if encoding and encoding.lower() in ("gb2312", "gb18030"):
            encoding = "gbk"

        for enc in filter(None, [encoding, *ENCODINGS]):
            try:
                return raw.decode(enc)
            except (UnicodeDecodeError, LookupError):
                continue

        return raw.decode("utf-8", errors="replace")
