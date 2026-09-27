"""Statistical inference helpers for visualization.

All routines are deterministic given a ``seed`` or ``rng`` argument, return plain
Python or pandas objects, and are documented with the estimator they implement.

References
----------
- Efron, B. & Tibshirani, R. (1993). *An Introduction to the Bootstrap*.
- Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.).
- Hedges, L. V. (1981). Distribution theory for Glass's estimator of effect size. *J. Educ. Stat.* 6(2).
- Cliff, N. (1993). Dominance statistics: ordinal analyses to answer ordinal questions. *Psychol. Bull.* 114(3).
- Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scand. J. Stat.* 6(2).
- Benjamini, Y. & Hochberg, Y. (1995). Controlling the false discovery rate. *J. R. Stat. Soc. B* 57(1).
"""

from __future__ import annotations

import itertools
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np
import pandas as pd
from scipy import stats as sps

__all__ = [
    "BootstrapResult",
    "PairwiseResult",
    "adjust_pvalues",
    "bootstrap_ci",
    "cliffs_delta",
    "cohens_d",
    "compare_groups",
    "glass_delta",
    "group_summary",
    "hedges_g",
    "interpret_effect_size",
    "p_to_stars",
    "permutation_test",
]

CorrectionMethod = Literal["none", "bonferroni", "holm", "fdr_bh"]
TestName = Literal["welch", "student", "mannwhitney", "permutation"]


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class BootstrapResult:
    """Point estimate and confidence interval from a bootstrap."""

    estimate: float
    low: float
    high: float
    confidence: float
    n_boot: int
    method: str
    samples: np.ndarray | None = field(default=None, repr=False, compare=False)

    def as_tuple(self) -> tuple[float, float]:
        """Return ``(low, high)``."""
        return self.low, self.high

    def to_dict(self) -> dict[str, float | int | str]:
        """Scalar fields only (drops ``samples``), e.g. for building a DataFrame row."""
        return {
            "estimate": self.estimate,
            "low": self.low,
            "high": self.high,
            "confidence": self.confidence,
            "n_boot": self.n_boot,
            "method": self.method,
        }


def _rng(seed: int | np.random.Generator | None) -> np.random.Generator:
    return seed if isinstance(seed, np.random.Generator) else np.random.default_rng(seed)


def bootstrap_ci(
    data: Sequence[float] | np.ndarray | pd.Series,
    statistic: Callable[[np.ndarray], float] = np.mean,
    *,
    confidence: float = 0.95,
    n_boot: int = 2000,
    method: Literal["percentile", "basic", "bca"] = "percentile",
    seed: int | np.random.Generator | None = 0,
    return_samples: bool = False,
) -> BootstrapResult:
    """Non-parametric bootstrap confidence interval for a univariate statistic.

    Parameters
    ----------
    data
        Sample values (NaNs are dropped).
    statistic
        Function reducing a 1-D array to a scalar.
    confidence
        Coverage level in (0, 1).
    n_boot
        Number of resamples.
    method
        ``percentile`` (default, matches Seaborn), ``basic`` (reverse percentile) or
        ``bca`` (bias-corrected and accelerated, via :func:`scipy.stats.bootstrap`).
    seed
        Integer seed or generator for reproducibility.
    return_samples
        Keep the bootstrap replicates in ``result.samples`` (percentile and basic
        methods only) so the sampling distribution can be plotted.
    """
    x = np.asarray(pd.Series(np.asarray(data, dtype=float)).dropna(), dtype=float)
    if x.size < 2:
        raise ValueError("bootstrap_ci requires at least two observations")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be in (0, 1)")
    rng = _rng(seed)
    est = float(statistic(x))
    alpha = 1 - confidence
    if method == "bca":
        res = sps.bootstrap(
            (x,),
            statistic,
            confidence_level=confidence,
            n_resamples=n_boot,
            method="BCa",
            random_state=rng,
            vectorized=False,
        )
        return BootstrapResult(
            est,
            float(res.confidence_interval.low),
            float(res.confidence_interval.high),
            confidence,
            n_boot,
            method,
        )
    idx = rng.integers(0, x.size, size=(n_boot, x.size))
    boots = np.apply_along_axis(statistic, 1, x[idx])
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    if method == "basic":
        lo, hi = 2 * est - hi, 2 * est - lo
    elif method != "percentile":
        raise ValueError("method must be 'percentile', 'basic' or 'bca'")
    return BootstrapResult(
        est,
        float(lo),
        float(hi),
        confidence,
        n_boot,
        method,
        samples=boots if return_samples else None,
    )


# ---------------------------------------------------------------------------
# Effect sizes
# ---------------------------------------------------------------------------
def _clean_pair(a: Any, b: Any) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray(pd.Series(np.asarray(a, dtype=float)).dropna(), dtype=float)
    y = np.asarray(pd.Series(np.asarray(b, dtype=float)).dropna(), dtype=float)
    if x.size < 2 or y.size < 2:
        raise ValueError("each group needs at least two observations")
    return x, y


def cohens_d(a: Any, b: Any) -> float:
    """Cohen's *d* with the pooled (unbiased) standard deviation."""
    x, y = _clean_pair(a, b)
    nx, ny = x.size, y.size
    pooled = np.sqrt(((nx - 1) * x.var(ddof=1) + (ny - 1) * y.var(ddof=1)) / (nx + ny - 2))
    if pooled == 0:
        return 0.0 if x.mean() == y.mean() else float(np.inf) * np.sign(x.mean() - y.mean())
    return float((x.mean() - y.mean()) / pooled)


def hedges_g(a: Any, b: Any) -> float:
    """Hedges' *g*: Cohen's *d* with the small-sample bias correction J(df)."""
    x, y = _clean_pair(a, b)
    df = x.size + y.size - 2
    j = 1 - 3 / (4 * df - 1)
    return float(cohens_d(x, y) * j)


def glass_delta(treatment: Any, control: Any) -> float:
    """Glass's Δ: mean difference standardised by the *control* group's SD."""
    x, y = _clean_pair(treatment, control)
    sd = y.std(ddof=1)
    return float((x.mean() - y.mean()) / sd) if sd else float("nan")


def cliffs_delta(a: Any, b: Any) -> float:
    """Cliff's δ, a non-parametric dominance measure in [-1, 1]."""
    x, y = _clean_pair(a, b)
    # Rank-based O((n+m) log(n+m)) computation via Mann-Whitney U.
    u = sps.mannwhitneyu(x, y, alternative="two-sided").statistic
    return float(2 * u / (x.size * y.size) - 1)


def interpret_effect_size(value: float, kind: Literal["d", "delta"] = "d") -> str:
    """Verbal label for an effect size (Cohen 1988 for *d*; Romano et al. 2006 for δ)."""
    v = abs(value)
    if kind == "d":
        cuts = ((0.2, "negligible"), (0.5, "small"), (0.8, "medium"))
    else:
        cuts = ((0.147, "negligible"), (0.33, "small"), (0.474, "medium"))
    for cut, label in cuts:
        if v < cut:
            return label
    return "large"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def permutation_test(
    a: Any,
    b: Any,
    statistic: Callable[[np.ndarray, np.ndarray], float] | None = None,
    *,
    n_permutations: int = 5000,
    alternative: Literal["two-sided", "greater", "less"] = "two-sided",
    seed: int | np.random.Generator | None = 0,
) -> tuple[float, float]:
    """Exact-in-the-limit permutation test for a two-sample statistic.

    Returns
    -------
    (statistic, p_value)
        Observed statistic and Monte Carlo p-value with the +1 correction of
        Phipson & Smyth (2010) so that *p* is never exactly zero.
    """
    x, y = _clean_pair(a, b)
    stat = statistic or (lambda p, q: float(np.mean(p) - np.mean(q)))
    rng = _rng(seed)
    observed = float(stat(x, y))
    pooled = np.concatenate([x, y])
    n = x.size
    perms = np.empty(n_permutations)
    for i in range(n_permutations):
        rng.shuffle(pooled)
        perms[i] = stat(pooled[:n], pooled[n:])
    if alternative == "two-sided":
        extreme = np.sum(np.abs(perms) >= abs(observed))
    elif alternative == "greater":
        extreme = np.sum(perms >= observed)
    else:
        extreme = np.sum(perms <= observed)
    p = (extreme + 1) / (n_permutations + 1)
    return observed, float(min(p, 1.0))


def adjust_pvalues(
    pvalues: Sequence[float] | np.ndarray, method: CorrectionMethod = "holm"
) -> np.ndarray:
    """Multiple-comparison adjustment.

    Parameters
    ----------
    pvalues
        Raw p-values.
    method
        ``none``, ``bonferroni``, ``holm`` (step-down, controls FWER) or ``fdr_bh``
        (Benjamini-Hochberg, controls FDR).
    """
    p = np.asarray(pvalues, dtype=float)
    m = p.size
    if m == 0:
        return p
    if method == "none":
        return p.copy()
    if method == "bonferroni":
        return np.minimum(p * m, 1.0)
    order = np.argsort(p)
    ranked = p[order]
    adjusted = np.empty(m)
    if method == "holm":
        adjusted = np.maximum.accumulate(np.minimum(ranked * (m - np.arange(m)), 1.0))
    elif method == "fdr_bh":
        adjusted = np.minimum.accumulate((ranked * m / np.arange(1, m + 1))[::-1])[::-1]
        adjusted = np.minimum(adjusted, 1.0)
    else:
        raise ValueError("method must be one of none, bonferroni, holm, fdr_bh")
    out = np.empty(m)
    out[order] = adjusted
    return out


def p_to_stars(
    p: float,
    thresholds: Sequence[tuple[float, str]] = ((0.001, "***"), (0.01, "**"), (0.05, "*")),
    ns: str = "ns",
) -> str:
    """Map a p-value to conventional significance stars."""
    for cut, label in thresholds:
        if p < cut:
            return label
    return ns


@dataclass(frozen=True)
class PairwiseResult:
    """One pairwise comparison between two groups."""

    group_a: str
    group_b: str
    n_a: int
    n_b: int
    mean_a: float
    mean_b: float
    statistic: float
    p_value: float
    p_adjusted: float
    effect_size: float
    effect_label: str
    effect_kind: str
    test: str
    stars: str

    @property
    def significant(self) -> bool:
        """Whether the adjusted p-value is below 0.05."""
        return self.p_adjusted < 0.05


def compare_groups(
    data: pd.DataFrame,
    x: str,
    y: str,
    *,
    test: TestName = "welch",
    correction: CorrectionMethod = "holm",
    order: Sequence[str] | None = None,
    pairs: Sequence[tuple[str, str]] | None = None,
    seed: int | np.random.Generator | None = 0,
    n_permutations: int = 5000,
) -> pd.DataFrame:
    """Run corrected pairwise comparisons across the levels of a categorical column.

    Parameters
    ----------
    data
        Long-form data.
    x
        Categorical column defining groups.
    y
        Numeric outcome.
    test
        ``welch`` (unequal-variance t), ``student`` (pooled t), ``mannwhitney`` or ``permutation``.
    correction
        Multiplicity adjustment applied across all pairs.
    order
        Group order; defaults to order of appearance.
    pairs
        Restrict to specific pairs; defaults to all combinations.
    seed, n_permutations
        Used only by the permutation test.

    Returns
    -------
    pandas.DataFrame
        One row per pair with statistic, raw and adjusted p, effect size and stars.
        The effect size is Hedges' *g* for t-tests and Cliff's δ otherwise.
    """
    if x not in data or y not in data:
        raise KeyError(f"columns {x!r} and {y!r} must be present")
    levels = list(order) if order is not None else list(pd.unique(data[x].dropna()))
    groups = {lvl: data.loc[data[x] == lvl, y].dropna().to_numpy(dtype=float) for lvl in levels}
    pairs = list(pairs) if pairs is not None else list(itertools.combinations(levels, 2))
    rows: list[dict[str, Any]] = []
    for a, b in pairs:
        ga, gb = groups[a], groups[b]
        if test == "welch":
            res = sps.ttest_ind(ga, gb, equal_var=False)
            stat, p = float(res.statistic), float(res.pvalue)
            eff, kind = hedges_g(ga, gb), "hedges_g"
        elif test == "student":
            res = sps.ttest_ind(ga, gb, equal_var=True)
            stat, p = float(res.statistic), float(res.pvalue)
            eff, kind = hedges_g(ga, gb), "hedges_g"
        elif test == "mannwhitney":
            res = sps.mannwhitneyu(ga, gb, alternative="two-sided")
            stat, p = float(res.statistic), float(res.pvalue)
            eff, kind = cliffs_delta(ga, gb), "cliffs_delta"
        elif test == "permutation":
            stat, p = permutation_test(ga, gb, n_permutations=n_permutations, seed=seed)
            eff, kind = cliffs_delta(ga, gb), "cliffs_delta"
        else:
            raise ValueError("test must be welch, student, mannwhitney or permutation")
        rows.append(
            {
                "group_a": str(a),
                "group_b": str(b),
                "n_a": int(ga.size),
                "n_b": int(gb.size),
                "mean_a": float(ga.mean()),
                "mean_b": float(gb.mean()),
                "statistic": stat,
                "p_value": p,
                "effect_size": eff,
                "effect_kind": kind,
                "test": test,
            }
        )
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["p_adjusted"] = adjust_pvalues(df["p_value"].to_numpy(), correction)
    df["effect_label"] = [
        interpret_effect_size(v, "d" if k == "hedges_g" else "delta")
        for v, k in zip(df["effect_size"], df["effect_kind"], strict=True)
    ]
    df["stars"] = df["p_adjusted"].map(p_to_stars)
    df["correction"] = correction
    cols = [
        "group_a",
        "group_b",
        "n_a",
        "n_b",
        "mean_a",
        "mean_b",
        "test",
        "statistic",
        "p_value",
        "p_adjusted",
        "correction",
        "effect_kind",
        "effect_size",
        "effect_label",
        "stars",
    ]
    return df[cols]


def group_summary(
    data: pd.DataFrame,
    x: str,
    y: str,
    *,
    statistic: Callable[[np.ndarray], float] = np.mean,
    confidence: float = 0.95,
    n_boot: int = 2000,
    seed: int | np.random.Generator | None = 0,
) -> pd.DataFrame:
    """Per-group estimate with bootstrap CI, ready to plot as error bars."""
    rows = []
    for lvl, sub in data.groupby(x, observed=True, sort=False):
        vals = sub[y].dropna().to_numpy(dtype=float)
        res = bootstrap_ci(vals, statistic, confidence=confidence, n_boot=n_boot, seed=seed)
        rows.append({x: lvl, "n": vals.size, **res.to_dict()})
    return pd.DataFrame(rows)
