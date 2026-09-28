"""Offline statistical functions extracted from the experimental implementation."""
from __future__ import annotations

import argparse

import json

import math

import os

import pathlib

import time

from collections import defaultdict

import numpy as np

from .reliability import bootstrap_ci

LADDER = ['C0', 'C1', 'C2', 'C3', 'C4']

from .consensus import FAILURE_KEYS, SCORE_KEYS, PROGRAMMATIC_KEYS

def _read_jsonl(p: pathlib.Path) -> list[dict]:
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]

def holm(pvals: dict[str, float]) -> dict[str, float]:
    """Holm-Bonferroni 보정 p 값."""
    items = sorted(((p, k) for k, p in pvals.items() if p is not None and not math.isnan(p)))
    m = len(items)
    adj, running = {}, 0.0
    for i, (p, k) in enumerate(items):
        running = max(running, (m - i) * p)
        adj[k] = min(1.0, running)
    for k in pvals:
        adj.setdefault(k, float("nan"))
    return adj

def paired_scores(judgments: list[dict], a: str, b: str, key: str = "composite") -> tuple[list[float], list[float]]:
    """같은 (persona, seed) 의 조건 a/b 점수 쌍."""
    idx = {(j["meta"]["condition"], j["meta"]["persona_id"], j["meta"]["seed"]): j for j in judgments}
    xs, ys = [], []
    for (c, pid, s), j in idx.items():
        if c != a:
            continue
        jb = idx.get((b, pid, s))
        if jb:
            xs.append(float(j[key])); ys.append(float(jb[key]))
    return xs, ys

def wilcoxon_p(xs, ys) -> float:
    from scipy.stats import wilcoxon
    d = np.asarray(ys) - np.asarray(xs)
    d = d[d != 0]
    if len(d) < 5:
        return float("nan")
    try:
        return float(wilcoxon(d, alternative="two-sided").pvalue)
    except ValueError:
        return float("nan")

def winrate_with_ci(pairwise: list[dict], a: str, b: str, n_boot: int = 2000) -> dict:
    """pairwise.jsonl 행 = (persona, seed) 단위 3심판 다수결. winner 가 None(판정 불능)이면 제외하되 건수를 기록."""
    rows_all = [p for p in pairwise if p.get("pair") == [a, b]]
    rows = [p for p in rows_all if p.get("winner") in ("A", "B", "tie")]
    if not rows:
        return {"n": 0, "undecidable": len(rows_all)}
    vals = np.array([{"A": 0.0, "B": 1.0, "tie": 0.5}[p["winner"]] for p in rows])
    lo, hi = bootstrap_ci(vals, np.mean, n_boot=n_boot)
    per_judge = defaultdict(list)
    swapped = []
    for p in rows:
        for v in p.get("votes", []):
            if v.get("winner") in ("A", "B", "tie"):
                per_judge[v.get("judge_model")].append({"A": 0.0, "B": 1.0, "tie": 0.5}[v["winner"]])
            if "swapped" in v:
                swapped.append(bool(v["swapped"]))
    return {"n": int(len(vals)), "undecidable": len(rows_all) - len(rows), "b_winrate": round(float(vals.mean()), 3),
            "ci95": [round(lo, 3), round(hi, 3)],
            "per_judge": {k: round(float(np.mean(v)), 3) for k, v in per_judge.items()},
            "position_swapped_share": round(float(np.mean(swapped)), 3) if swapped else None}

def compute_stats(judgments: list[dict], pairwise: list[dict], pairs: list[tuple[str, str]] | None = None) -> dict:
    conds = sorted({j["meta"]["condition"] for j in judgments}, key=lambda c: LADDER.index(c) if c in LADDER else 99)
    if pairs is None:
        pairs = [(conds[i], conds[i + 1]) for i in range(len(conds) - 1)]
        for extra in (("C2", "C3"), ("C3", "C4")):
            if extra[0] in conds and extra[1] in conds and extra not in pairs:
                pairs.append(extra)
    comparisons = {}
    for a, b in pairs:
        xs, ys = paired_scores(judgments, a, b)
        comp = {"n_pairs": len(xs), "mean_a": round(float(np.mean(xs)), 3) if xs else None,
                "mean_b": round(float(np.mean(ys)), 3) if ys else None,
                "diff_mean": round(float(np.mean(np.subtract(ys, xs))), 3) if xs else None,
                "wilcoxon_p": wilcoxon_p(xs, ys) if xs else float("nan")}
        if xs:
            d = np.subtract(ys, xs)
            lo, hi = bootstrap_ci(d, np.mean)
            comp["diff_ci95"] = [round(lo, 3), round(hi, 3)]
        comp["pairwise"] = winrate_with_ci(pairwise, a, b)
        comparisons[f"{a}~{b}"] = comp
    adj = holm({k: v["wilcoxon_p"] for k, v in comparisons.items()})
    for k, v in comparisons.items():
        v["wilcoxon_p_holm"] = adj[k]
        v["significant_005"] = (not math.isnan(adj[k])) and adj[k] < 0.05
    per_cond = {}
    for c in conds:
        rows = [j for j in judgments if j["meta"]["condition"] == c]
        per_cond[c] = {"n": len(rows), "composite_mean": round(float(np.mean([r["composite"] for r in rows])), 3),
                       "composite_sd": round(float(np.std([r["composite"] for r in rows])), 3),
                       "failure_rate": {k: round(float(np.mean([r["failures"].get(k, False) for r in rows])), 3) for k in FAILURE_KEYS},
                       "scores_mean": {k: round(float(np.mean([r["scores"].get(k, 0) for r in rows])), 3) for k in SCORE_KEYS}}
    return {"conditions": per_cond, "comparisons": comparisons, "n_judged": len(judgments), "pairs": pairs}

def render_report(stats: dict, lc: dict | None, smoke: bool = False) -> str:
    L = ["# 통계 리포트", ""] + (["> 스모크 런 — 결론 인용 금지 (심판 미검증).", ""] if smoke else []) + ["## 조건별 종합점수", "", "| 조건 | n | 평균 | SD | 실패율(F1..F7) |", "|---|---|---|---|---|"]
    for c, v in stats["conditions"].items():
        L.append(f"| {c} | {v['n']} | {v['composite_mean']} | {v['composite_sd']} | " + "/".join(f"{v['failure_rate'][k]:.2f}" for k in FAILURE_KEYS) + " |")
    L += ["", "## 비교 (B − A)", "", "| 비교 | n쌍 | Δ평균 [95% CI] | Wilcoxon p | Holm p | 유의 | B 승률 [95% CI] |", "|---|---|---|---|---|---|---|"]
    for k, v in stats["comparisons"].items():
        pw = v["pairwise"]
        wr = f"{pw.get('b_winrate')} {pw.get('ci95')}" if pw.get("n") else "-"
        p = v["wilcoxon_p"]; ph = v["wilcoxon_p_holm"]
        L.append(f"| {k} | {v['n_pairs']} | {v['diff_mean']} {v.get('diff_ci95', '')} | {p:.4f} | {ph:.4f} | {'예' if v['significant_005'] else '아니오'} | {wr} |"
                 if not (isinstance(p, float) and math.isnan(p)) else f"| {k} | {v['n_pairs']} | {v['diff_mean']} | n/a | n/a | - | {wr} |")
    if lc:
        L += ["", "## 최적화 학습곡선", f"- 반복 {lc['iterations']}회, best {lc['best_initial']} → {lc['best_final']}, 게이트 실패 {lc['gate_fail_count']}회",
              f"- 정체 상태: {'예 (마지막 개선 후 ' + str(lc.get('since_improve_final')) + '회) → 정체 대응 사다리 적용' if lc.get('plateau_final') else '아니오'}",
              f"- 플롯: {lc['png'] or '(matplotlib 없음)'}"]
    return "\n".join(L) + "\n"
