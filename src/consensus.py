"""P3-4 (v2): 3심판 합의 프로토콜 — 다수결 판정기 · 판정 불능 집계 · 차원별 Fleiss κ 모니터(J1·J2).

- 실패 F1~F7: 유효 심판 ≥3 의 다수결. 동률(짝수 심판)·유효 심판 <3 이면 '판정 불능(undecidable)'.
  코드 판정 항목(F1/F4/F6)은 검증기 결과가 그대로 정본(J3) — 합의 대상이 아니다.
- 점수 1~5: 중앙값(다수결의 순서형 대응) + 평균 병기. 최대-최소 차 ≥2 이면 dissent 로 기록.
- coverage: 중앙값.
- 배치 κ: 세션 묶음마다 차원별 Fleiss κ (실패=이진, 점수=5범주) + 점수는 ICC(2,k) 병기.
  플래그 규칙: 실패항목 = Fleiss κ < 0.60 / 점수차원 = ICC(2,k) < 0.60 (순서형 1~5 는 정확일치 κ 가 인접 점수 차이를
  불일치로 세어 과소평가되므로, S2' 와 같은 ICC 기준을 쓴다. Fleiss κ 는 참고로 함께 기록).
"""
from __future__ import annotations

import statistics
from collections import Counter

from .reliability import fleiss_kappa, icc2k

FAILURE_KEYS = ["F1", "F2", "F3", "F4", "F5", "F6", "F7"]
PROGRAMMATIC_KEYS = ["F1", "F4", "F6"]
PARTIAL_PROGRAMMATIC = {"F5": "F5_repeat", "F7": "F7_occupation"}   # v0.0.7: 코드 성분 OR LLM 잔여 판정
SCORE_KEYS = ["process", "exploration", "accuracy", "personalization", "actionability", "empathy", "branch_fit"]
KAPPA_FLAG = 0.60
MIN_JUDGES = 3


def majority_vote(labels: list[bool]) -> tuple[bool | None, str]:
    """(판정, 상태). 상태: 'majority' | 'unanimous' | 'tie' | 'insufficient'"""
    n = len(labels)
    if n < 2:                       # 타사 슬롯 대기 중에는 2심판도 허용(J1 미충족 표기). 1 이하는 판정 불능
        return None, "insufficient"
    yes = sum(1 for x in labels if x)
    if yes == n or yes == 0:
        return yes == n, "unanimous"
    if yes * 2 == n:
        return None, "tie"
    return yes * 2 > n, "majority"


def aggregate_session(verdicts: list[dict], programmatic: dict | None = None) -> dict:
    """verdicts: 각 심판의 SessionVerdict.model_dump() (error 가 있으면 제외).
    반환: failures / status / scores(median) / scores_mean / dissent / undecidable / n_judges / judge_models"""
    ok = [v for v in verdicts if not v.get("error")]
    n = len(ok)
    failures: dict[str, bool | None] = {}
    status: dict[str, str] = {}
    dissent: dict[str, list] = {}
    for k in FAILURE_KEYS:
        if k in PROGRAMMATIC_KEYS and programmatic is not None and k in programmatic:
            failures[k] = bool(programmatic[k]); status[k] = "programmatic"
            llm = [bool(v["failures_llm"].get(k)) for v in ok if v.get("failures_llm")]
            if llm and any(x != failures[k] for x in llm):
                dissent[k] = [v["judge_model"] for v in ok if v.get("failures_llm") and bool(v["failures_llm"].get(k)) != failures[k]]
            continue
        code_key = PARTIAL_PROGRAMMATIC.get(k)
        code_hit = bool(programmatic.get(code_key)) if (programmatic is not None and code_key and code_key in programmatic) else False
        labels = [bool((v.get("failures_llm") or v["failures"]).get(k)) for v in ok]   # LLM 잔여 판정
        verdict, st = majority_vote(labels)
        if code_hit:                                        # 코드 성분이 잡히면 실패 확정 (J3)
            failures[k] = True; status[k] = "programmatic+" + st
            if verdict is False:
                dissent[k] = [v["judge_model"] for v in ok]
            elif st in ("majority", "tie"):
                dissent[k] = [v["judge_model"] for v in ok if not bool((v.get("failures_llm") or v["failures"]).get(k))]
            continue
        failures[k] = verdict; status[k] = st
        if st in ("majority", "tie"):
            minority = (not verdict) if verdict is not None else None
            dissent[k] = [v["judge_model"] for v in ok if minority is None or bool((v.get("failures_llm") or v["failures"]).get(k)) == minority]
    scores, scores_mean, score_range = {}, {}, {}
    for k in SCORE_KEYS:
        vals = [int(v["scores"][k]) for v in ok if k in v.get("scores", {})]
        if vals:
            scores[k] = float(statistics.median(vals)); scores_mean[k] = round(sum(vals) / len(vals), 3)
            score_range[k] = max(vals) - min(vals)
            if score_range[k] >= 2:
                dissent["score:" + k] = vals
    covs = [float(v["coverage"]) for v in ok if v.get("coverage") is not None]
    undecidable = [k for k, st in status.items() if st in ("tie", "insufficient")]
    return {
        "failures": failures, "failure_status": status, "undecidable": undecidable,
        "scores": scores, "scores_mean": scores_mean, "score_range": score_range,
        "coverage": round(float(statistics.median(covs)), 3) if covs else None,
        "coverage_missing": n - len(covs),
        "dissent": dissent, "n_judges": n, "judge_models": [v["judge_model"] for v in ok],
        "consensus_ok": n >= 2 and not undecidable,
        "j1_met": n >= MIN_JUDGES,
        "per_judge": verdicts,
    }


def batch_kappa(aggregates: list[dict]) -> dict:
    """배치(세션 목록)의 차원별 심판 간 일치도. per_judge 가 있는 집계 dict 목록을 받는다."""
    out = {"failures": {}, "scores": {}, "n_sessions": 0, "flags": [], "kappa_threshold": KAPPA_FLAG}
    rows = [a for a in aggregates if a.get("per_judge")]
    if not rows:
        return out
    k_judges = min(len([p for p in a["per_judge"] if not p.get("error")]) for a in rows)
    if k_judges < 2:
        return out
    out["n_sessions"] = len(rows)
    for fk in FAILURE_KEYS:
        key = "failures_llm"          # κ 는 심판 원판정(LLM) 기준. 코드 성분은 κ 대상이 아니다
        mat = [[bool(p[key].get(fk)) for p in a["per_judge"] if not p.get("error")][:k_judges] for a in rows if all(p.get(key) for p in a["per_judge"] if not p.get("error"))]
        if not mat:
            continue
        kappa = fleiss_kappa(mat)
        base_rate = sum(sum(r) for r in mat) / (len(mat) * k_judges)
        out["failures"][fk] = {"kappa": None if kappa != kappa else round(kappa, 3), "positive_rate": round(base_rate, 3),
                               "programmatic": fk in PROGRAMMATIC_KEYS, "partial_programmatic": fk in PARTIAL_PROGRAMMATIC,
                               "flag": (kappa == kappa) and kappa < KAPPA_FLAG and 0.0 < base_rate < 1.0}
    for sk in SCORE_KEYS:
        mat = [[int(p["scores"][sk]) for p in a["per_judge"] if not p.get("error") and sk in p.get("scores", {})][:k_judges] for a in rows]
        mat = [r for r in mat if len(r) == k_judges]
        if not mat:
            continue
        kappa = fleiss_kappa(mat)
        icc = icc2k(mat)
        out["scores"][sk] = {"kappa": None if kappa != kappa else round(kappa, 3), "icc2k": None if icc != icc else round(icc, 3),
                             "mean_range": round(sum(max(r) - min(r) for r in mat) / len(mat), 3),
                             "flag": (icc == icc) and icc < KAPPA_FLAG}      # 점수차원은 ICC(2,k) 기준
    out["flags"] = [k for k, v in out["failures"].items() if v["flag"]] + [k for k, v in out["scores"].items() if v["flag"]]
    out["undecidable_sessions"] = sum(1 for a in rows if a.get("undecidable"))
    out["undecidable_by_key"] = dict(Counter(k for a in rows for k in a.get("undecidable", [])))
    return out


def render_kappa_md(k: dict, title: str = "심판 합의율 (J2)") -> str:
    L = [f"## {title}", "", f"세션 {k.get('n_sessions', 0)}건 · 판정 불능 세션 {k.get('undecidable_sessions', 0)}건 {k.get('undecidable_by_key', {})} · 기준 κ ≥ {k.get('kappa_threshold', KAPPA_FLAG)}", "",
         "| 실패항목 | Fleiss κ | 양성률 | 판정 정본 | 플래그 |", "|---|---|---|---|---|"]
    for fk, v in k.get("failures", {}).items():
        L.append(f"| {fk} | {v['kappa']} | {v['positive_rate']} | {'코드' if v['programmatic'] else ('코드 성분 + 다수결(잔여)' if v.get('partial_programmatic') else '다수결')} | {'⚑ κ<0.60' if v['flag'] else ''} |")
    L += ["", "| 점수차원 | Fleiss κ(5범주, 참고) | ICC(2,k) | 평균 최대차 | 플래그(ICC<0.60) |", "|---|---|---|---|---|"]
    for sk, v in k.get("scores", {}).items():
        L.append(f"| {sk} | {v['kappa']} | {v['icc2k']} | {v['mean_range']} | {'⚑ ICC<0.60' if v['flag'] else ''} |")
    if k.get("flags"):
        L += ["", f"**자동 플래그(루브릭 개정 후보)**: {', '.join(k['flags'])}"]
    return "\n".join(L) + "\n"


def pairwise_majority(votes: list[str | None]) -> tuple[str | None, str]:
    """페어와이즈 3심판 다수결: 'A'|'B'|'tie' 중 최다. 동률이면 판정 불능."""
    valid = [v for v in votes if v in ("A", "B", "tie")]
    if len(valid) < MIN_JUDGES:
        return None, "insufficient"
    c = Counter(valid).most_common()
    if len(c) > 1 and c[0][1] == c[1][1]:
        return None, "tie"
    return c[0][0], "unanimous" if c[0][1] == len(valid) else "majority"


def main(argv=None):
    """judgments.jsonl 에서 배치 κ 재계산:  python -m lab.judge.consensus --out results/exp_smoke"""
    import argparse, json, pathlib
    ap = argparse.ArgumentParser(prog="lab.judge.consensus"); ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = pathlib.Path(a.out)
    rows = [json.loads(l) for l in (out / "judgments.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    k = batch_kappa(rows)
    (out / "consensus.json").write_text(json.dumps(k, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "consensus.md").write_text(render_kappa_md(k), encoding="utf-8")
    print(render_kappa_md(k))


if __name__ == "__main__":
    main()
