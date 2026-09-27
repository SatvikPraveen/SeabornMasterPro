# 📐 Methodology: the estimators behind `seabornmasterpro`

This document states precisely what each statistical and perceptual routine computes,
which published definition it follows, and how it is validated. It is the reference to
cite in a methods section when a figure was produced with this package.

---

## 1. Uncertainty: `stats.bootstrap_ci`, `stats.group_summary`

**Estimator.** Non-parametric bootstrap of a univariate statistic *T* (default: the mean).
Given a sample *x₁…xₙ*, draw *B* resamples with replacement (default *B* = 2000), compute
*T\** on each, and form the interval from the empirical distribution of *T\**.

| `method` | Interval | Notes |
|---|---|---|
| `percentile` (default) | [*T\**₍α/2₎, *T\**₍1−α/2₎] | Identical to Seaborn's `errorbar=("ci", 95)` construction. Invariant to monotone transformations; can be biased for skewed statistics. |
| `basic` | [2*T̂* − *T\**₍1−α/2₎, 2*T̂* − *T\**₍α/2₎] | The reverse-percentile interval. |
| `bca` | Bias-corrected and accelerated, via `scipy.stats.bootstrap(method="BCa")` | Second-order accurate; preferred for small samples or skewed statistics. Slower. |

**Determinism.** Resampling uses `numpy.random.Generator` seeded from the `seed` argument
(default 0). The same seed and inputs give the same interval on every platform.

**Reference.** Efron & Tibshirani (1993), *An Introduction to the Bootstrap*, ch. 13–14.

**Validation.** `tests/test_stats.py` checks that the interval contains the point estimate,
that coverage on a known Normal population is near the nominal level over repeated draws,
and (via Hypothesis) that the interval is invariant to the order of the observations.

---

## 2. Effect sizes: `cohens_d`, `hedges_g`, `glass_delta`, `cliffs_delta`

All signed effect sizes follow the convention **first argument − second argument**.

**Cohen's *d*.** (x̄₁ − x̄₂) / *s*ₚ, with the pooled standard deviation
*s*ₚ = √[((*n*₁−1)*s*₁² + (*n*₂−1)*s*₂²) / (*n*₁+*n*₂−2)] using unbiased (ddof=1) variances.
Cohen (1988).

**Hedges' *g*.** *d* × *J*, with the small-sample correction *J* = 1 − 3 / (4·df − 1),
df = *n*₁+*n*₂−2. Hedges (1981). This is the effect size reported by `compare_groups`
for *t*-tests.

**Glass's Δ.** (x̄ₜ − x̄꜀) / *s*꜀, standardised by the *control* group only. Appropriate
when the treatment changes the variance.

**Cliff's δ.** P(*X* > *Y*) − P(*X* < *Y*), computed exactly from the Mann–Whitney *U*
statistic as 2*U*/(*n*₁*n*₂) − 1. Ranges over [−1, 1], is distribution-free, and is the
effect size reported for rank and permutation tests. Cliff (1993).

**Verbal labels** (`interpret_effect_size`).
*d*/*g*: |·| < 0.2 negligible, < 0.5 small, < 0.8 medium, else large (Cohen, 1988).
δ: |·| < 0.147 negligible, < 0.33 small, < 0.474 medium, else large (Romano et al., 2006).

**Validation.** Tests check antisymmetry (*d*(a, b) = −*d*(b, a)), scale invariance
(*d*(ka, kb) = *d*(a, b) for *k* > 0), zero for identical samples, and recovery of a
planted effect in the `clinical_trial` dataset within its bootstrap interval.

---

## 3. Two-sample tests: `permutation_test`, `compare_groups`

| `test` | Statistic | Null distribution | Effect size |
|---|---|---|---|
| `welch` (default) | Welch's *t* (unequal variances) | Student *t* with Welch–Satterthwaite df | Hedges' *g* |
| `student` | Pooled-variance *t* | Student *t*, df = *n*₁+*n*₂−2 | Hedges' *g* |
| `mannwhitney` | Mann–Whitney *U* | Exact for small *n*, Normal approximation otherwise (SciPy) | Cliff's δ |
| `permutation` | Difference in means (or a user statistic) | Monte Carlo: *N* random relabellings (default 5000) | Cliff's δ |

**Permutation *p*-value.** *p* = (*b* + 1) / (*N* + 1), where *b* counts permutations at
least as extreme as the observed statistic. The +1 correction (Phipson & Smyth, 2010)
guarantees *p* > 0 and makes the test exact under the null. Two-sided tests compare
absolute values.

**Defaults are deliberate.** Welch's *t* is the default because it is robust to unequal
variances at negligible cost when variances are equal (Delacre, Lakens & Leys, 2017).

---

## 4. Multiplicity: `adjust_pvalues`

| `method` | Controls | Procedure |
|---|---|---|
| `bonferroni` | FWER | *p*ᵢ × *m*, capped at 1 |
| `holm` (default) | FWER | Step-down: sort ascending, *p*₍ᵢ₎ × (*m* − *i* + 1), enforce monotonicity with a cumulative max |
| `fdr_bh` | FDR | Step-up: *p*₍ᵢ₎ × *m* / *i*, enforce monotonicity with a reverse cumulative min |
| `none` | — | Raw *p*-values |

Holm is uniformly more powerful than Bonferroni while offering the same guarantee, which
is why it is the default. Benjamini–Hochberg is appropriate when many comparisons are
exploratory and a controlled proportion of false discoveries is acceptable.

**References.** Holm (1979); Benjamini & Hochberg (1995).

**Validation.** Adjusted *p*-values are checked to be ≥ raw, ≤ 1, monotone in the raw
ordering, and equal to `statsmodels.stats.multitest.multipletests` output when
statsmodels is installed.

---

## 5. Colour and accessibility: `color`

**Colour-vision-deficiency simulation** (`simulate_cvd`). Colours are linearised from sRGB
(IEC 61966-2-1 inverse companding), multiplied by the Machado, Oliveira & Fernandes (2009)
matrices for protanopia, deuteranopia and tritanopia at severity 1.0, and re-encoded to
sRGB. Achromatopsia uses the Rec. 709 luminance weights (0.2126, 0.7152, 0.0722).

**Perceptual distance** (`delta_e`, `min_pairwise_distance`). CIE76 ΔE\*ab: Euclidean
distance in CIELAB computed from linear sRGB via the D65 XYZ matrix. CIE76 is used rather
than CIEDE2000 because the question is *are these categories distinguishable*, for which
the simpler metric is adequate and easier to reason about. As a rule of thumb ΔE < 2 is
imperceptible and ΔE > 10 is clearly distinct.

**Contrast** (`contrast_ratio`, `relative_luminance`). WCAG 2.1 relative luminance and
contrast ratio (*L*₁ + 0.05)/(*L*₂ + 0.05). Success Criterion 1.4.11 requires ≥ 3:1 for
graphical objects; 1.4.3 requires ≥ 4.5:1 for normal text.

**`validate_palette`** reports the minimum pairwise ΔE in normal vision and under each
deficiency, the minimum contrast against the chosen background, and passes only when all
thresholds are met. Seaborn's `colorblind` palette passes the ΔE checks but its yellow
fails 3:1 on white, which the report says explicitly.

**Validation.** Tests assert that pure red and green collapse under protanopia and
deuteranopia, that grey is invariant under every simulation, that black/white contrast is
21:1, that ΔE is zero for identical colours and symmetric, and that CIELAB white is
(100, 0, 0) within tolerance.

---

## 6. Figure geometry: `theme`

Journal presets encode published author guidelines as `JournalSpec` records
(single-column width, double-column width, maximum height, base and minimum font sizes,
line width, font family). Widths in millimetres are converted at 25.4 mm/in.

| Key | Single | Double | Source |
|---|---|---|---|
| `nature` | 89 mm | 183 mm | Nature "Formatting guide: figures" |
| `science` | 55 mm | 120 mm | Science "Instructions for authors" |
| `ieee` | 3.5 in | 7.16 in | IEEE Transactions template |
| `elsevier` | 90 mm | 190 mm | Elsevier artwork guidelines |
| `plos` | 5.2 in | 7.5 in | PLOS figure guidelines |
| `acm` | 3.33 in | 7 in | ACM `acmart` column widths |

`publication_rc` also sets `pdf.fonttype = 42` and `svg.fonttype = "none"` so text
remains editable in vector editors, removes top and right spines, and disables the legend
frame. `journal_context` applies these inside `matplotlib.rc_context`, so nothing leaks
into subsequent cells.

---

## 7. Provenance and integrity: `io`, `repro`

`save_fig` embeds a JSON provenance record in the file's metadata: PNG `tEXt` chunks
(`Software`, `Provenance`), PDF document info (`Creator`, `Subject`) and SVG
`<metadata>` (`Creator`, `Description`). The record contains the UTC timestamp, Python
and platform, versions of numpy, pandas, scipy, matplotlib, seaborn, statsmodels and
scikit-learn when installed, the `seabornmasterpro` version and the short git revision.
Pass `sidecar=True` to also write it as `<figure>.<ext>.json`.

`write_manifest` records SHA-256 digests and sizes for a set of files together with the
same environment record; `verify_manifest` re-hashes and reports per-file agreement.
`datasets/MANIFEST.json` is regenerated by `smp-datasets` and checked in CI.

---

## 8. Datasets: `datasets`

Every table has a `DatasetCard` (name, description, generative model, column roles, row
count, seed note), modelled on Gebru et al. (2021). The six original datasets replay the
exact legacy `np.random.seed(0)` stream so that all figures in notebooks 01–10 remain
reproducible bit-for-bit. The three research datasets use independent
`numpy.random.default_rng` streams and have known ground truth:

* `clinical_trial` — planted standardised differences (Placebo vs High ≈ 0.78).
* `sensor_readings` — additive diurnal, weekly, trend and noise components with 0.4% labelled anomalies.
* `gene_expression` — two co-regulated modules shifted by +1.8 and −1.2 log₂ units in the treated condition.

---

## References

* Benjamini, Y. & Hochberg, Y. (1995). Controlling the false discovery rate. *J. R. Stat. Soc. B*, 57(1), 289–300.
* Cliff, N. (1993). Dominance statistics: ordinal analyses to answer ordinal questions. *Psychol. Bull.*, 114(3), 494–509.
* Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.). Erlbaum.
* Delacre, M., Lakens, D. & Leys, C. (2017). Why psychologists should by default use Welch's t-test instead of Student's t-test. *Int. Rev. Soc. Psychol.*, 30(1), 92–101.
* Efron, B. & Tibshirani, R. J. (1993). *An Introduction to the Bootstrap*. Chapman & Hall.
* Gebru, T. et al. (2021). Datasheets for datasets. *Commun. ACM*, 64(12), 86–92.
* Hedges, L. V. (1981). Distribution theory for Glass's estimator of effect size and related estimators. *J. Educ. Stat.*, 6(2), 107–128.
* Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scand. J. Stat.*, 6(2), 65–70.
* Machado, G. M., Oliveira, M. M. & Fernandes, L. A. F. (2009). A physiologically-based model for simulation of color vision deficiency. *IEEE TVCG*, 15(6), 1291–1298.
* Phipson, B. & Smyth, G. K. (2010). Permutation p-values should never be zero. *Stat. Appl. Genet. Mol. Biol.*, 9(1), Article 39.
* Romano, J., Kromrey, J. D., Coraggio, J. & Skowronek, J. (2006). Appropriate statistics for ordinal level data. *Annual meeting of the Florida Association of Institutional Research*.
* W3C (2018). *Web Content Accessibility Guidelines (WCAG) 2.1*, SC 1.4.3 and 1.4.11.
