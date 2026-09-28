import json
import pathlib
import numpy as np
from .reliability import bootstrap_ci, cohen_kappa

def _read(p): return [json.loads(l) for l in pathlib.Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]

def report(out: pathlib.Path, pair, spec: str, log=print) -> dict:
    a, b = pair
    H = {(r["persona_id"], r["seed"]): r for r in _read(out / "heldout" / "pairwise_heldout.jsonl")}
    E = {(r["persona_id"], r["seed"]): r for r in _read(out / "pairwise.jsonl") if r["pair"] == [a, b]}
    keys = [k for k in H if k in E and H[k].get("winner") in ("A", "B", "tie") and E[k].get("winner") in ("A", "B", "tie")]
    val = {"A": 0.0, "B": 1.0, "tie": 0.5}
    hv = np.array([val[H[k]["winner"]] for k in keys]); ev = np.array([val[E[k]["winner"]] for k in keys])
    lo, hi = bootstrap_ci(hv, np.mean)
    agree = float(np.mean([H[k]["winner"] == E[k]["winner"] for k in keys]))
    kappa = cohen_kappa([H[k]["winner"] for k in keys], [E[k]["winner"] for k in keys])
    per_judge = {}
    for m in sorted({v["judge_model"] for k in keys for v in E[k]["votes"]}):
        pairs = [(H[k]["winner"], next(v["winner"] for v in E[k]["votes"] if v["judge_model"] == m)) for k in keys]
        pairs = [(x, y) for x, y in pairs if y in ("A", "B", "tie")]
        per_judge[m] = {"agreement": round(float(np.mean([x == y for x, y in pairs])), 3), "kappa": round(cohen_kappa([x for x, _ in pairs], [y for _, y in pairs]), 3),
                        "b_winrate": round(float(np.mean([val[y] for _, y in pairs])), 3)}
    errors = sum(1 for r in H.values() if r.get("error"))
    rep = {"heldout_judge": spec, "resolved_model": next((r.get("resolved_model") for r in H.values()), None), "pair": [a, b], "n": len(keys), "errors": errors,
           "heldout_b_winrate": round(float(hv.mean()), 3), "heldout_ci95": [round(lo, 3), round(hi, 3)],
           "ensemble_b_winrate": round(float(ev.mean()), 3), "agreement_with_majority": round(agree, 3), "kappa_with_majority": round(kappa, 3),
           "per_judge": per_judge, "swapped_share": round(float(np.mean([H[k]["swapped"] for k in keys])), 3),
           "direction_consistent": bool(lo > 0.5) == bool(ev.mean() > 0.5) and lo > 0.5,
           "s4_verdict": ("held-out 심판도 같은 방향(CI 하한 > 0.5) — 지표 해킹 징후 없음" if lo > 0.5 else
                          ("held-out 심판은 우위를 지지하지 않음 — 최적화 효과가 심판 취향에 의존할 가능성" if hi < 0.5 or hv.mean() <= 0.5 else "held-out 심판 결과 불확정(CI 가 0.5 포함)"))}
    md = [f"# S4 held-out 심판 재판정 — {a} vs {b}", "",
          f"- held-out 심판: {spec} (실제 id: {rep['resolved_model']}) · 상시 앙상블 미편입 · 쌍 {rep['n']} · 오류 {errors} · 스왑 비율 {rep['swapped_share']}",
          f"- **held-out B 승률 {rep['heldout_b_winrate']} [{rep['heldout_ci95'][0]}, {rep['heldout_ci95'][1]}]** vs 3심판 다수결 {rep['ensemble_b_winrate']}",
          f"- 다수결과 일치율 {rep['agreement_with_majority']} · Cohen κ {rep['kappa_with_majority']}", "",
          "| 앙상블 심판 | held-out 과 일치율 | κ | 그 심판의 B 승률 |", "|---|---|---|---|"]
    md += [f"| {m} | {v['agreement']} | {v['kappa']} | {v['b_winrate']} |" for m, v in per_judge.items()]
    md += ["", f"**판정**: {rep['s4_verdict']}"]
    (out / "heldout" / "heldout_report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "heldout" / "heldout_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    log("\n".join(md))
    return rep
