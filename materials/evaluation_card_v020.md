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


## v0.2.0 사후 감사 보충 (2026-09-28)

위 본실험 평가 카드는 원문을 보존했다. 아래 내용은 저장 자료 재집계이며 점수·판정·확증 결과를 대체하지 않는다.

- GPT rationale 빈값 918/2,250(40.8%): 모두 해당 GPT의 failures_llm 7항목 False. 실패 항목만 근거를 쓰라는 동결 지침과 부합한다. 사후 주석 918건, API 호출 0회, 원본 빈값과 missing_fields 유지. 코드 F7_occupation 양성 28건은 별도 구분.
- C4 F1: 47/450(10.44%), C3 36/450(8.00%). 지자체 4→14세션이 순증 11건 중 10건. 정규식이 탐색 은유도 검출한다는 한계를 병기한다.
- S6 CSV 234행 전수 분류 100%; 행동 결함 54행 시드 또는 루브릭 연결 100%, 직접 시드 52/54(96.30%). 매핑률은 해결률이 아니다.
- C2→C3 갈래 승률: 직업 .567, 전직 .600, 희망리턴 .544, 지자체 .648(유효88/90), 대학 .522. 사후 기술 분석이며 기존 행 단위 부트스트랩 사용.
- P5 전 AI 합의 심사 등급 유지. 공개 및 익명화 승인 대기, 영어 대역 독립 검토·참고문헌 DOI 대조 미완료.
