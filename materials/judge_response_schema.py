"""Response schemas extracted for documentation; no API client included."""
FAILURE_KEYS = ["F1", "F2", "F3", "F4", "F5", "F6", "F7"]

PROGRAMMATIC_KEYS = ["F1", "F4", "F6"]

SCORE_KEYS = ["process", "exploration", "accuracy", "personalization", "actionability", "empathy", "branch_fit"]

SCORE_LABELS = {"process": "프로세스 준수", "exploration": "탐색 품질", "accuracy": "정보 정확성·근거성",
                "personalization": "개인화", "actionability": "행동 가능성", "empathy": "공감·태도", "branch_fit": "갈래 적합성"}
