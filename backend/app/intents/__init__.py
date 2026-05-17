import enum


class IntentType(str, enum.Enum):
    QA = "qa"
    SUMMARIZE = "summarize"
    EXTRACT = "extract"
    COMPARE = "compare"
    TRANSLATE = "translate"
    GENERAL = "general"
