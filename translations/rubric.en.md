# English companion to the frozen judging rubric

Informational translation, v0.2.0 submission package, 2026-09-28. The Korean original is authoritative and was used in the experiment. This translation is not a new scoring instrument and has not been used to rescore results. Freeze tag: `rubric-freeze-v2.2.1`; the rubric's internal heading is **v2.2** (the freeze also includes judge prompt v1.6).

## A. Failure detection (binary; any positive occurrence makes the session positive)

- **F1 — Unsupported action promises:** statements such as “I will look it up,” “I displayed it,” or “I sent it” without a supporting tool call. First stage: regex detector; second stage: judge review. The implementation's code verdict takes precedence.
- **F2 — Evasion of capability limits:** ending with a refusal while omitting at least two of (1) a reason, (2) an immediate alternative, and (3) a concrete route the client can pursue independently.
- **F3 — Failure of branch specialization:** language, assessments, or examples unrelated to the branch's target clients, according to prohibitions in its delta document.
- **F4 — Hallucinated recommendations:** mentioning job posting IDs, companies, or links absent from `search_jobs` results. The programmatic verdict is authoritative; the judge's assessment is supplementary.
- **F5 — Failure of personalization:** [code] repetition (consecutive-response character 3-gram Jaccard similarity >0.6, or within-response sentence duplication ratio ≥0.5) **OR** [judge] residual F5: asking again for information the client already provided, or giving generic advice without incorporating the session profile (age, experience, location, constraints). Judges assess the residual component, not repetition. Use the examples in A′.
- **F6 — Failure of session management:** no counselor-initiated greeting, no ten-minute notice, no next-action line at the end of a response, or no closing summary.
- **F7 — Unrealistic outputs:** [code] recommending a job title not found in the KECO lookup (`occupation_lookup` returns `exists=False`) **OR** [judge] residual F7, assessed in this order:
  1. By session end, is there at least one proposed action-plan sentence describing something the client should do (apply, search, write, inquire, register, visit, etc.)? If there is none, **F7=False**. Absence of a plan is reflected in B5 (actionability) and F6 (absence of a closing summary).
  2. If a plan sentence exists, assess the most specific one for a timeframe, an action, and a way to check completion. **F7=True only when at least two of these three elements are absent** (an abstract slogan).
  Judges do not assess whether job titles are standardized; code assesses that component.

## A′. Residual F5 and F7 examples

### Residual F5 — Re-asking and failure to reflect the profile

| # | Failure (True) | Pass (False) |
|---|---|---|
| 1 | Client: “I have ten years of accounting experience and live in Gwangju.” Counselor next turn: “What work have you done, and where do you live?” | “With ten years in accounting, we can first look at bookkeeping/accounting positions in Gwangju and South Jeolla. What matters more in your reason for moving: compensation or the work itself?” |
| 2 | Client: “I'm 58 and have been out of work for five years.” Counselor: “Excel is essential for office work these days. Write a cover letter.” (generic advice ignoring age and the gap) | “For returning at 58 after a five-year gap, let's start with routes such as fixed-term public-sector work or experience-based programs that do not penalize the gap.” |
| 3 | The client says “I cannot work nights” in turn one; the counselor asks “Do you have any restrictions on work hours?” in turn three. | “I incorporated your no-night-work condition and narrowed the list to day-shift postings (J-1001).” |

### Residual F7 — Timeframe, action, and completion check

| # | Failure (True) | Pass (False) |
|---|---|---|
| 1 | “Keep developing your capabilities and prepare with a positive attitude.” (all three elements absent) | “By this Friday, save three results for ‘office Gwangju’ on Employment24, and review them together at the next counseling session.” |
| 2 | “Get a certificate and prepare your résumé.” (no timeframe or completion check) | “Stage 1 (two weeks): register for Computerized Accounting Level 2 on Q-Net. Stage 2 (after registration): draft your résumé and book feedback at the university career center. Save a screenshot of the registration confirmation message.” |
| 3 | “Succeed in finding employment within 30 days.” (timeframe only) | “30-day plan: apply to five postings in week one, write ten anticipated interview questions in week two, and update the application tracker every Sunday.” |
| 4 (v2.2) | “To summarize, office work and customer counseling seem suitable. Prepare step by step.” A plan sentence exists (“prepare”), but lacks a timeframe and completion check: **F7=True**. | A session only explores the situation, proposes no action, and ends with “We will stop here today.” There is no plan sentence: **F7=False**; reflect this in B5 (1–2 points) and F6 (no closing summary). |

Apply examples consistently to equivalent cases. If several plan sentences exist, use the most specific one. First establish whether a plan exists; only then count its elements.

## B. Quality dimensions (session-level, 1–5 Likert)

1. **Process adherence:** follows the seven-stage flow from relationship building to closing.
2. **Exploration quality:** elicits key facts from the hidden profile (simulator ground truth); report coverage percentage alongside the score.
3. **Information accuracy and grounding:** information agrees with tool evidence.
4. **Personalization:** advice is specific to this client's circumstances.
5. **Actionability:** the client has a plan they can act on today at session end.
6. **Empathy and attitude:** recognizes emotional responses and uses a respectful tone. Judge reliability is relatively low; this dimension requires parallel human assessment.
7. **Branch fit:** behaves like a specialist counselor for the relevant branch.

## C. Judgment protocol

Absolute ratings are supplementary. System comparisons use paired sessions from the same scenario, with randomized A/B placement to control position bias. Code takes precedence for F4, F1 regex rules, F6 format rules, F5 repetition, and F7 occupational-title checks; judges cannot override it. Final F5/F7 = code component OR majority residual judgment.

Outputs follow a forced JSON schema: `{"failures":{"F1":bool,...},"scores":{"process":1-5,...},"coverage":0-1,"rationale":"..."}`. Include at least one judge model different from the runtime model to mitigate self-reinforcement bias.

## D. Connection to the zero-human evaluation policy

The authority hierarchy is code verifier > heterogeneous three-judge majority. Single-judge decisions are not authoritative. Ties/all-disagree cases are reported separately as undecidable. Compute dimension-wise Fleiss' κ for every batch; κ<0.60 triggers a flag for potential rubric revision. Before the terminal P5 retrospective human audit, claims remain **AI consensus assessment**. Stronger claims are restricted to dimensions passing that audit. Preserve judge model IDs, judge prompt and rubric versions, majority decisions, and dissent in judgment JSON (S7).

## E. Mapping the seven dimensions to established constructs

| Dimension | Corresponding construct / instrument | Source | Operational definition in this rubric |
|---|---|---|---|
| Process | CTRS/CTS-R structure and session management: agenda setting, pacing, efficient use of time | Young & Beck (1980) [1]; Blackburn et al. (2001) [2] | Seven-stage order, early scope/time notice, time allocation beyond exploration |
| Exploration | WAI task/goal agreement and completeness of career intake | Bordin (1979) [3]; Horvath & Greenberg (1989) [4] | Hidden-profile key-fact coverage; one question per turn to elicit experience, constraints and preferences; confirm goals in the client's words |
| Accuracy / grounding | Evidence-based practice fidelity and NLP factuality/grounding measures | Honovich et al. (2022) [5]; Min et al. (2023) [6] | Agreement with search_jobs/policy_rag results; because F4 is authoritative code, rate faithful communication of tool evidence here |
| Personalization | Client-centeredness; MITI complex reflection | Rogers (1957) [7]; Moyers et al. (2016) [8] | Incorporates utterances and profile with added meaning rather than simple repetition; avoids generic advice and repeated questions |
| Actionability | Goal Attainment Scaling (GAS); SMART goal specificity | Kiresuk & Sherman (1968) [9]; Doran (1981) [10] | Closing plan includes timeframe, action, and a way to check completion; abstract slogans score 1 |
| Empathy | MITI global empathy rating; priority for human comparison given concerns about LLM-judge reliability | Moyers et al. (2016) [8]; Sharma et al. (2020) [11] | Emotional acknowledgment and respectful tone; flag as excluded from AI assessment if anchor ICC does not meet its threshold |
| Branch fit | No corresponding standardized instrument; an explicitly new construct in this study | — | Adheres to delta-document target populations and prohibitions; branch-specialist language and information |

This is **construct correspondence**, not a claim that the original instruments were administered. Their items are not reproduced; only construct definitions are borrowed.

### References and source limitation

The following reference list is preserved verbatim from the frozen Korean artifact. Its source explicitly states that all eleven references were drafted from model memory and require DOI/volume/issue verification before submission. This translation does not certify their bibliographic accuracy. Reference [1] is an unpublished manual, ordinarily cited alongside [2].

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
