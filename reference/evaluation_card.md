# 평가 카드 (Evaluation Card) v2

> 루브릭 동결: **rubric-freeze-v2.2.1** · rubric sha e5ddf42fb3

생성: 2026-09-26 18:09 · 결과 경로: `results/exp_full` · 단계: **P4 이전/종료 (인간 평가자 0명)**

## 0. 주장 등급 (주장 사다리)
- 현재 허용 주장: 전 세션을 코드 검증기와 이종 3중 AI 합의로 심사했고, 판정 불능·저합의 차원까지 투명하게 집계했으며 전 과정이 감사 가능하다.
- 표기 등급: **AI 합의 심사 (consensus-based)** — P5 전이므로 '검증된(validated)' 표현 불가

## 1. 심판 구성·버전 (J1, S7)
- 심판 3개: claude-opus-4-6, openai/gpt-5.4, claude-sonnet-4-6 · 공급자 anthropic, openai · 이종 공급자 포함
- 런타임 모델 claude-sonnet-4-6 · 판정 정본: 코드 검증기(F1, F4, F6) > 3심판 다수결 (J3). 단독 심판 경로 없음
- 심판 프롬프트/루브릭 버전: v1.6/v2.2 (동결 버전 단일)
- 페어와이즈 위치 무작위: C0~C1 스왑비율 0.504, C1~C2 스왑비율 0.487, C2~C3 스왑비율 0.48, C3~C4 스왑비율 0.504

## 2. 합의율 모니터 (J2)
- 배치 세션 2250건 · 판정 불능 세션 0건 {}
- κ<0.60 자동 플래그: F2, F3, F5, F7 (루브릭 개정 후보 — 개정 시 버전 분리 재채점)

| 실패항목 | Fleiss κ | 정본 |
|---|---|---|
| F1 | 0.999 | 코드 |
| F2 | 0.131 ⚑ | 다수결 |
| F3 | 0.012 ⚑ | 다수결 |
| F4 | 0.988 | 코드 |
| F5 | 0.187 ⚑ | 다수결 |
| F6 | 1.0 | 코드 |
| F7 | 0.101 ⚑ | 다수결 |

| 점수차원 | Fleiss κ | ICC(2,k) |
|---|---|---|
| process | 0.609 | 0.947 |
| exploration | 0.465 | 0.85 |
| accuracy | 0.472 | 0.838 |
| personalization | 0.365 | 0.843 |
| actionability | 0.41 | 0.893 |
| empathy | 0.434 | 0.794 |
| branch_fit | 0.401 | 0.854 |

- 심판별 선택 필드 누락(판정은 유효, 근거 인용 없음): claude-opus-4-6:rationale 2건(0%), openai/gpt-5.4:rationale 918건(41%)

## 2-1. 지표 해킹 점검 — held-out 심판 (S4)
- held-out 심판 google/gemini-3.1-pro (실제 id gemini-3.1-pro-preview) · 최적화 루프·상시 앙상블 미참여 · C3 vs C4 445쌍
- held-out B 승률 0.703 [0.661, 0.746] vs 3심판 다수결 0.737 · 일치율 0.787 · κ 0.471
- 판정: held-out 심판도 같은 방향(CI 하한 > 0.5) — 지표 해킹 징후 없음

## 3. AI 심사 규모 (S3)
- 채점 세션 2250건 = 조건 5(C0, C1, C2, C3, C4) × 시나리오 150 × 시드 3 · 판정 불능 세션 0건(은폐 없이 집계)
- S3 기준(≥2250): 충족

## 4. 종단 인간 감사 (P5, S1'·S2')
- 미수행 (설계상 P5 에서 1회). 준비 명령: `python -m lab.calibration.anchor sample/sheets/reliability` (P5-1)

## 5. 감사 자료 위치 (S7)
- 전 세션 전사·도구로그: `results/exp_full/sessions.jsonl`
- 전 세션 채점 JSON(심판×3 원판정·majority·dissent·undecidable): `results/exp_full/judgments.jsonl` · 합의율: `results/exp_full/consensus.json` · 페어와이즈: `results/exp_full/pairwise.jsonl`
- 소급 앵커 원자료: `results/exp_full/anchor` (rater_*.csv, blind_key.json, calibration.json)
- 실험 설정: `results/exp_full/config.json` · 통계: `results/exp_full/stats.json` · 회귀 시드: `counselor-lab/regression/seeds.jsonl`
