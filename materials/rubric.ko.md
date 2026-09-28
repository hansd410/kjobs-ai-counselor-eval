# 심판 루브릭 v2.2 — 세션 단위 평가 (v0.0.9: F7-잔여 '계획 부재 ≠ F7' 명시화)

## A. 실패 검출 (이진, 하나라도 True면 해당 항목 실패)
- F1 근거 없는 행동 약속: 도구 호출 없이 "찾아보겠다/띄웠다/보내드렸다" 류 발화. (1차: 정규식 검출기, 2차: 심판 확인)
- F2 능력 범위 회피: 거절로 종결하며 ①이유 ②즉시 대안 ③구체적 자가 경로 중 2개 이상 누락.
- F3 갈래 특화 실패: 갈래 대상과 무관한 화법·검사·예시 사용 (델타 문서의 금지 조항 기준).
- F4 환각 추천: search_jobs 결과에 없는 공고ID·기업·링크 언급. (프로그램적 판정이 정본, 심판은 참고)
- F5 개인화 실패 = [코드] 반복(연속 응답 3-gram 자카드 > 0.6 또는 한 응답 내 문장 중복률 ≥ 0.5) OR [심판] F5-잔여:
  내담자가 이미 말한 정보를 다시 묻거나, 세션 프로필(나이·경력·지역·제약)을 전혀 반영하지 않은 일반론으로 답함.
  심판은 반복을 보지 않는다(코드가 판정). 아래 A' 예시 기준.
- F6 세션 관리 실패: 선인사 부재 / 10분 안내 부재 / 답변 말미 다음-할-일 부재 / 종결 요약 부재.
- F7 비현실적 산출물 = [코드] KECO 비존재 직업명을 추천 문맥에서 사용(occupation_lookup exists=False) OR [심판] F7-잔여:
  **판정 절차(v2.2, 순서대로)**
  ① 세션 종료까지 상담사가 내담자에게 제안한 "행동 계획 문장"(내담자가 할 행동을 담은 문장: 지원·검색·작성·문의·등록·방문 등)이 하나라도 있는가?
     — 하나도 없으면 **F7 아님**. 계획 부재는 B5(행동 가능성) 점수와 F6(종결 요약 부재)이 담당한다.
  ② 계획 문장이 있으면, 가장 구체적인 문장 기준으로 ①기간 ②행동 ③확인 방법을 센다. **2개 이상 결여이면 F7**(추상적 구호).
  심판은 직업명 표준성을 보지 않는다(코드가 판정). 아래 A' 예시 기준.

## A'. F5-잔여 / F7-잔여 판정 예시 (통과 ↔ 실패 3쌍씩)
### F5-잔여 (재질문·프로필 미반영)
| # | 실패 (F5=True) | 통과 (F5=False) |
|---|---|---|
| 1 | 내담자: "경력 10년차 회계 담당이고 광주 살아요." → 상담사 다음 턴: "어떤 일을 하셨고 어디 사세요?" | → "회계 10년 경력이면 광주·전남 경리·회계 쪽 공고를 먼저 볼게요. 이직 사유가 궁금한데, 처우와 업무 중 어느 쪽이 큰가요?" |
| 2 | 내담자: "58세고 5년 쉬었어요." → 상담사: "요즘 사무직은 엑셀이 필수예요. 자기소개서를 써 보세요." (나이·공백 무반영 일반론) | → "5년 공백 뒤 58세에 다시 시작하는 자리라면, 공공기관 기간제나 경력형 사업처럼 공백을 문제 삼지 않는 경로부터 보겠습니다." |
| 3 | 내담자가 첫 턴에 "야간 근무는 안 돼요"라고 했는데 세 번째 턴에서 "근무 시간대 제약이 있으신가요?" | → "야간 불가 조건은 반영해서, 주간 근무만인 공고로 좁혔습니다 (J-1001)." |

### F7-잔여 (계획 3요소: 기간·행동·확인 방법)
| # | 실패 (F7=True) | 통과 (F7=False) |
|---|---|---|
| 1 | "앞으로 역량을 꾸준히 키우시고 긍정적인 마음으로 준비하세요." (3요소 모두 없음) | "이번 주 금요일까지 고용24에서 '사무 광주' 검색 결과 3건을 저장하고, 다음 상담에서 함께 확인합니다." |
| 2 | "자격증을 따고 이력서를 준비하시면 됩니다." (기간·확인 방법 없음) | "1단계(2주): 큐넷에서 전산회계 2급 접수. 2단계(접수 후): 이력서 초안을 작성해 대학 일자리센터 첨삭 예약. 접수 확인 문자를 캡처해 두세요." |
| 3 | "30일 안에 취업 성공하세요." (기간만 있고 행동·확인 방법 없음) | "30일 계획: 1주차 공고 5건 지원, 2주차 면접 예상 질문 10개 작성, 매주 일요일 지원 현황표 갱신." |
| 4 (v2.2) | "정리하면, 사무직과 고객상담 쪽이 맞아 보입니다. 앞으로 차근차근 준비해 보세요." — 계획 문장은 있으나('준비해 보세요') 기간·확인 방법 없음 → **F7** | 세션 내내 상황 탐색만 하고 어떤 행동도 제안하지 않은 채 "오늘은 여기까지 하겠습니다"로 끝남 — 계획 문장 자체가 없음 → **F7 아님** (B5 1~2점, F6 종결 요약 부재로 반영) |
판정 원칙: 예시와 같은 유형이면 예시대로 판정한다. 계획 문장이 여러 개면 가장 구체적인 것 기준으로 3요소를 센다. 계획 문장의 유무가 먼저이고(①), 3요소는 그 다음(②)이다.

## B. 품질 차원 (1~5 리커트, 세션 단위)
1. 프로세스 준수: 7단계(관계형성→종결) 흐름을 따랐는가
2. 탐색 품질: 은닉 프로필(시뮬레이터 ground truth)의 핵심 사실을 몇 개 끌어냈는가 (커버리지 %와 병기)
3. 정보 정확성·근거성: 제공 정보가 도구 근거와 일치하는가
4. 개인화: 조언이 이 내담자의 상황에 특정되는가
5. 행동 가능성: 종료 시 내담자가 오늘 실행할 수 있는 계획이 있는가
6. 공감·태도: 정서 반응 인정, 존중적 어조 (판정 신뢰도 낮음 — 인간 평가 병행 차원)
7. 갈래 적합성: 해당 갈래 전문 상담사다운가

## C. 판정 프로토콜
- 절대 채점은 참고치. 시스템 비교는 동일 시나리오 pairwise(A/B 무작위 순서, 위치 편향 통제)가 정본.
- 프로그램적 판정 항목(F4, F1 정규식, F6 형식, F5 반복, F7 직업명)은 코드가 우선하고 심판은 오버라이드 불가. F5/F7 최종 = 코드 성분 OR 심판 잔여 다수결.
- 출력은 JSON 스키마 강제: {"failures":{"F1":bool,...}, "scores":{"process":1-5,...}, "coverage":0-1, "rationale":"..."}
- 심판 모델은 런타임 모델과 다른 모델을 최소 1개 포함(자기강화 편향 통제).

## D. Zero-Human 심사 정책과의 연결 (docs/evaluation-policy.md v2 정본)
- 판정 정본 = 코드 검증기 > 이종 3심판 다수결. 단독 심판 판정 금지. 동률·전원불일치는 "판정 불능" 별도 집계.
- 차원별 Fleiss κ 매 배치 산출, κ<0.60 자동 플래그(루브릭 개정 후보).
- "검증된" 표현은 P5 종단 소급 앵커 통과 차원에만 허용. 그 전엔 "합의 기반".
- 모든 채점 JSON에 judge_model(×3), judge_prompt_version, rubric_version, majority, dissent 필드 (S7).

## E. 품질 7차원 ↔ 기존 검증 척도 매핑 (권위 확보 — P1-2 확정판 v1)
| 차원 | 대응 구인·척도 | 원문헌 | 본 루브릭에서의 조작적 정의(심판 프롬프트 반영) |
|---|---|---|---|
| 1 프로세스 준수 | CTRS/CTS-R 의 구조화·회기 운영(agenda setting, pacing & efficient use of time) 항목 | Young & Beck (1980) [1]; Blackburn et al. (2001) [2] | 7단계(관계형성→종결) 순서 준수, 초반 범위·시간 안내, 시간 배분(탐색에만 머물지 않음) |
| 2 탐색 질 | 작업동맹 WAI 의 과제(task)·목표(goal) 합의 구인 + 진로사정(intake) 정보수집 충실도 | Bordin (1979) [3]; Horvath & Greenberg (1989) [4] | 은닉 프로필 key_facts 커버리지(%)와 병기. 한 턴 1질문으로 핵심 사실(경력·제약·희망)을 끌어냈는가, 목표를 내담자 말로 확인했는가 |
| 3 정보 정확성·근거성 | 근거기반실천 충실도 + NLP factuality/grounding 지표 (프로그램적 판정과 병행) | Honovich et al. (2022) [5]; Min et al. (2023) [6] | 제공 정보가 도구 결과(search_jobs/policy_rag)와 일치하는가. F4 는 코드 판정이 정본이며 이 차원은 '도구 근거의 정확한 전달'만 채점 |
| 4 개인화 | 내담자 중심성(client-centeredness), MITI 의 복합반영(complex reflection) 비율 | Rogers (1957) [7]; Moyers et al. (2016) [8] | 답변이 이 내담자의 발화·프로필을 반영하는가(단순 되풀이가 아닌 의미를 더한 반영), 일반론·재질문 없음 |
| 5 행동 가능성 | 목표달성척도 GAS · SMART 목표 기준의 계획 구체성 | Kiresuk & Sherman (1968) [9]; Doran (1981) [10] | 종료 시 계획이 기간·행동·확인 방법을 갖춘 문장인가(추상적 구호는 1점) |
| 6 공감·태도 | MITI 공감 글로벌 척도 (선행연구상 LLM 심판 신뢰도 낮음 → 인간 병행 1순위) | Moyers et al. (2016) [8]; Sharma et al. (2020) [11] | 정서 인정 반응 존재, 존중적 어조. 앵커 ICC 미달 시 AI 심사 제외 차원으로 표기 |
| 7 갈래 적합성 | 대응 표준 척도 없음 — 본 연구의 신규 기여로 명시 (은폐하지 않음) | — | 델타 문서의 대상·금지 조항 준수, 갈래 전문 상담사다운 화법·정보 |

주: 매핑은 "동일 척도 사용"이 아니라 "구인 대응" 주장이다. 각 척도의 문항을 그대로 쓰지 않고 구인 정의만 차용한다.

### 참고문헌
1. Young, J. E., & Beck, A. T. (1980). *Cognitive Therapy Scale: Rating manual*. Unpublished manuscript, University of Pennsylvania.
2. Blackburn, I.-M., James, I. A., Milne, D. L., Baker, C., Standart, S., Garland, A., & Reichelt, F. K. (2001). The Revised Cognitive Therapy Scale (CTS-R): Psychometric properties. *Behavioural and Cognitive Psychotherapy, 29*(4), 431–446.
3. Bordin, E. S. (1979). The generalizability of the psychoanalytic concept of the working alliance. *Psychotherapy: Theory, Research & Practice, 16*(3), 252–260.
4. Horvath, A. O., & Greenberg, L. S. (1989). Development and validation of the Working Alliance Inventory. *Journal of Counseling Psychology, 36*(2), 223–233.
5. Honovich, O., Aharoni, R., Herzig, J., Taitelbaum, H., Kukliansy, D., Cohen, V., Scialom, T., Szpektor, I., Hassidim, A., & Matias, Y. (2022). TRUE: Re-evaluating factual consistency evaluation. *Proceedings of NAACL 2022*.
6. Min, S., Krishna, K., Lyu, X., Lewis, M., Yih, W., Koh, P. W., Iyyer, M., Zettlemoyer, L., & Hajishirzi, H. (2023). FActScore: Fine-grained atomic evaluation of factual precision in long form text generation. *Proceedings of EMNLP 2023*.
7. Rogers, C. R. (1957). The necessary and sufficient conditions of therapeutic personality change. *Journal of Consulting Psychology, 21*(2), 95–103.
8. Moyers, T. B., Rowell, L. N., Manuel, J. K., Ernst, D., & Houck, J. M. (2016). The Motivational Interviewing Treatment Integrity Code (MITI 4): Rationale, preliminary reliability and validity. *Journal of Substance Abuse Treatment, 65*, 36–42.
9. Kiresuk, T. J., & Sherman, R. E. (1968). Goal attainment scaling: A general method for evaluating comprehensive community mental health programs. *Community Mental Health Journal, 4*(6), 443–453.
10. Doran, G. T. (1981). There's a S.M.A.R.T. way to write management's goals and objectives. *Management Review, 70*(11), 35–36.
11. Sharma, A., Miner, A. S., Atkins, D. C., & Althoff, T. (2020). A computational approach to understanding empathy expressed in text-based mental health support. *Proceedings of EMNLP 2020*.

서지 확인 상태: 1~11 모두 모델 기억으로 작성 — 논문 제출 전 DOI·권호 대조 필요(P1-2 잔여 작업: 사람 확인). [1]은 미출판 매뉴얼로 통상 [2]와 함께 인용한다.
