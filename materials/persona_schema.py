"""페르소나 계약. hidden_profile 은 상담사에게 절대 노출 금지 — 탐색 커버리지 채점 기준."""
from typing import Literal
from pydantic import BaseModel

class HiddenProfile(BaseModel):
    suitable_jobs: list[str]        # KECO 명칭 — 정답 직무
    constraints: list[str]          # 예: "야간 불가(육아)", "광주 외 이동 불가"
    key_facts: list[str]            # 상담사가 끌어내야 할 사실 (커버리지 분모)

class Persona(BaseModel):
    persona_id: str
    branch: Literal["career","outplacement","hope_return","local_gov","university"]
    surface: str                    # 첫 발화에서 드러나는 정보만
    behavior: Literal["짧은단답","감정적","비협조적","주제이탈","무리한요구","협조적"]
    openness_init: float            # 0~1. 상담 품질에 따라 ±0.1/턴 동적 조정
    hidden_profile: HiddenProfile
