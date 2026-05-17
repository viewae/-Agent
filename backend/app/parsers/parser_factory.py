from app.exceptions import ValidationError
from app.parsers.base import BaseParser
from app.parsers.docx_parser import DocxParser
from app.parsers.pdf_parser import PDFParser
from app.parsers.txt_parser import TxtParser

PARSER_MAP: dict[str, BaseParser] = {
    "pdf": PDFParser(),
    "docx": DocxParser(),
    "txt": TxtParser(),
}


def get_parser(file_type: str) -> BaseParser:
    parser = PARSER_MAP.get(file_type.lower())
    if parser is None:
        raise ValidationError(f"No parser available for file type: .{file_type}")
    return parser
