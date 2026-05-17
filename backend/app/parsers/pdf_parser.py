import logging

import pdfplumber

from app.parsers.base import BaseParser

logger = logging.getLogger(__name__)


class PDFParser(BaseParser):
    def extract_text(self, file_path: str) -> str:
        texts = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        texts.append(page_text)
                    else:
                        logger.warning("Page %d in %s has no text layer", i + 1, file_path)
        except Exception:
            logger.exception("Failed to parse PDF: %s", file_path)
            raise
        return "\n\n".join(texts)
