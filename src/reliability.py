"""신뢰도 통계: ICC(2,k), Cohen κ, Fleiss κ. (evaluation-policy S2 기준: ICC ≥ 0.60, κ ≥ 0.70)"""
from __future__ import annotations

import math
from collections import Counter

import numpy as np


def icc2k(matrix) -> float:
    """ICC(2,k) — 양방향 무선효과, 평균 측정치 (Shrout & Fleiss 1979).
    matrix: n(대상) × k(평가자) 실수 배열. NaN 이 있는 행은 제외."""
    m = np.asarray(matrix, dtype=float)
    m = m[~np.isnan(m).any(axis=1)]
    n, k = m.shape
    if n < 2 or k < 2:
        return float("nan")
    grand = m.mean()
    row_means = m.mean(axis=1)
    col_means = m.mean(axis=0)
    ss_rows = k * ((row_means - grand) ** 2).sum()
    ss_cols = n * ((col_means - grand) ** 2).sum()
    ss_total = ((m - grand) ** 2).sum()
    ss_err = ss_total - ss_rows - ss_cols
    msr = ss_rows / (n - 1)
    msc = ss_cols / (k - 1)
    mse = ss_err / ((n - 1) * (k - 1))
    denom = msr + (msc - mse) / n
    if denom == 0:
        return float("nan")
    return float((msr - mse) / denom)


def cohen_kappa(a, b) -> float:
    a, b = list(a), list(b)
    assert len(a) == len(b) and a, "길이 불일치/빈 입력"
    n = len(a)
    cats = sorted(set(a) | set(b), key=str)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum((ca[c] / n) * (cb[c] / n) for c in cats)
    if pe == 1:
        return 1.0
    return float((po - pe) / (1 - pe))


def fleiss_kappa(ratings) -> float:
    """ratings: n(대상) × k(평가자) 범주 라벨 (bool/int/str)."""
    rows = [list(r) for r in ratings]
    n = len(rows)
    if n == 0:
        return float("nan")
    k = len(rows[0])
    cats = sorted({c for r in rows for c in r}, key=str)
    if len(cats) < 2:
        return 1.0
    counts = np.array([[sum(1 for c in r if c == cat) for cat in cats] for r in rows], dtype=float)
    p_j = counts.sum(axis=0) / (n * k)
    P_i = ((counts ** 2).sum(axis=1) - k) / (k * (k - 1))
    P_bar = P_i.mean()
    P_e = (p_j ** 2).sum()
    if P_e == 1:
        return 1.0
    return float((P_bar - P_e) / (1 - P_e))


def majority(labels) -> bool:
    labels = [bool(x) for x in labels]
    return sum(labels) * 2 > len(labels)


def bootstrap_ci(values, stat, n_boot: int = 1000, alpha: float = 0.05, seed: int = 0):
    rng = np.random.default_rng(seed)
    arr = np.asarray(values)
    boots = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(arr), len(arr))
        try:
            boots.append(stat(arr[idx]))
        except Exception:
            continue
    if not boots:
        return (math.nan, math.nan)
    return (float(np.nanpercentile(boots, 100 * alpha / 2)), float(np.nanpercentile(boots, 100 * (1 - alpha / 2))))
