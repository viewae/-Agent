from app.parsers.parser_factory import get_parser


class ParserService:
    def parse(self, file_path: str, file_type: str) -> str:
        parser = get_parser(file_type)
        return parser.extract_text(file_path)
