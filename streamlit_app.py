"""SeabornMasterPro explorer: gallery, data cards, group comparisons, palette checks.

Run from the repository root with ``streamlit run streamlit_app.py``; no
installation of the package is required because the repo root is added to
``sys.path`` before ``seabornmasterpro`` is imported.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from matplotlib.figure import Figure

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from seabornmasterpro import annotate, color, datasets, repro, stats  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
NOTEBOOK_FOLDERS: dict[str, str] = {
    "📘 01 - Setup and Basics": "exports/01_setup",
    "📊 02 - Distributions & Relationships": "exports/02_distributions",
    "📦 03 - Categorical & Matrix Plots": "exports/03_categorical",
    "📐 04 - Dashboards & Facets": "exports/04_dashboards",
    "🧪 05 - Real-World EDA": "exports/05_eda",
    "📈 06 - Time Series & Advanced Lineplots": "exports/06_timeseries",
    "🎯 07 - Figure-Level Functions": "exports/07_figure_level",
    "📊 08 - Advanced Categorical Plots": "exports/08_categorical",
    "🎨 09 - Styling & Customization": "exports/09_styling",
    "📐 10 - Statistical Parameters": "exports/10_statistical",
    "🔬 11 - Research Workflow": "exports/11_research",
}

PLOT_KINDS = ("scatter", "box", "violin", "hist", "line")
TESTS = ("welch", "student", "mannwhitney", "permutation")
CORRECTIONS = ("holm", "bonferroni", "fdr_bh", "none")
MAX_LEVELS = 8
MAX_PLOT_LEVELS = 12
SEABORN_PALETTES = (
    "colorblind",
    "deep",
    "muted",
    "pastel",
    "bright",
    "dark",
    "tab10",
    "Set2",
    "Paired",
    "husl",
    "viridis",
    "rocket",
    "mako",
)
VISION_TYPES = ("normal", "protanopia", "deuteranopia", "tritanopia", "achromatopsia")
NONE_LABEL = "(none)"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_dataset(name: str) -> pd.DataFrame:
    return datasets.load(name)


def numeric_columns(df: pd.DataFrame) -> list[str]:
    return [
        c
        for c in df.columns
        if pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_bool_dtype(df[c])
    ]


def categorical_columns(df: pd.DataFrame, max_levels: int | None = None) -> list[str]:
    cols = [
        c
        for c in df.columns
        if pd.api.types.is_bool_dtype(df[c])
        or pd.api.types.is_string_dtype(df[c])
        or isinstance(df[c].dtype, pd.CategoricalDtype)
    ]
    if max_levels is not None:
        cols = [c for c in cols if df[c].nunique() <= max_levels]
    return cols


def plottable_x_columns(df: pd.DataFrame) -> list[str]:
    return [
        c
        for c in df.columns
        if pd.api.types.is_numeric_dtype(df[c]) or pd.api.types.is_datetime64_any_dtype(df[c])
    ]


def show_figure(fig: Figure) -> None:
    st.pyplot(fig, width="stretch")
    plt.close(fig)


def optional_select(label: str, options: list[str], key: str) -> str | None:
    choice = st.selectbox(label, [NONE_LABEL, *options], key=key)
    return None if choice == NONE_LABEL else choice


def limit_levels(
    df: pd.DataFrame, column: str, cap: int = MAX_LEVELS, min_n: int = 2
) -> tuple[pd.DataFrame, list[str]]:
    """Keep the ``cap`` most frequent levels with at least ``min_n`` rows, warning about drops."""
    counts = df[column].astype(str).value_counts()
    usable = counts[counts >= min_n]
    if len(usable) < len(counts):
        st.warning(
            f"{len(counts) - len(usable)} level(s) of '{column}' have fewer than {min_n} "
            "observations and were dropped."
        )
    if len(usable) > cap:
        st.warning(
            f"'{column}' has {len(usable)} levels; only the {cap} most frequent are compared."
        )
    levels = [str(v) for v in usable.index[:cap]]
    sub = df[df[column].astype(str).isin(levels)].copy()
    sub[column] = sub[column].astype(str)
    return sub, levels


# ---------------------------------------------------------------------------
# Tab 1: Gallery
# ---------------------------------------------------------------------------
def render_gallery() -> None:
    st.markdown("Browse every plot exported by the curriculum notebooks.")
    section = st.selectbox("📂 Notebook section", list(NOTEBOOK_FOLDERS), key="gallery_section")
    image_dir = ROOT / NOTEBOOK_FOLDERS[section]
    if not image_dir.exists():
        st.warning("This section has no exported plots yet.")
        return
    image_files = sorted(image_dir.glob("*.png"))
    if not image_files:
        st.info("No plots found in this section yet.")
        return
    st.caption(f"{len(image_files)} figure(s) in `{image_dir.relative_to(ROOT)}`")
    for img_path in image_files:
        st.subheader(img_path.stem.replace("_", " ").title())
        st.image(str(img_path), width="stretch")


# ---------------------------------------------------------------------------
# Tab 2: Datasets
# ---------------------------------------------------------------------------
def render_data_card(card: datasets.DatasetCard, df: pd.DataFrame) -> None:
    st.subheader(card.name)
    st.markdown(card.description)
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", f"{len(df):,}")
    c2.metric("Columns", df.shape[1])
    c3.metric("Declared rows", f"{card.n_rows:,}")
    st.markdown(f"**Generative model:** {card.generative_model}")
    st.markdown(f"**Seed:** `{card.seed_note}` · **File:** `datasets/{card.filename}`")
    columns = pd.DataFrame({"column": list(card.columns), "type": list(card.columns.values())})
    st.dataframe(columns, hide_index=True, width="stretch")


def plot_selectors(df: pd.DataFrame, kind: str) -> dict[str, str | None]:
    numeric = numeric_columns(df)
    categorical = categorical_columns(df, MAX_PLOT_LEVELS)
    hue_options = categorical + [c for c in numeric if c not in categorical]
    c1, c2, c3 = st.columns(3)
    with c1:
        if kind in ("scatter", "line"):
            x = st.selectbox("x", plottable_x_columns(df), key="ds_x")
        elif kind == "hist":
            x = st.selectbox("x", numeric, key="ds_x")
        else:
            x = st.selectbox("x (categorical)", categorical or numeric, key="ds_x")
    with c2:
        y: str | None
        if kind == "hist":
            y = None
            st.caption("y is not used for histograms.")
        else:
            y_options = [c for c in numeric if c != x] or numeric
            y = st.selectbox("y", y_options, key="ds_y")
    with c3:
        hue = optional_select("hue", hue_options, key="ds_hue")
    return {"x": x, "y": y, "hue": hue}


def draw_dataset_plot(df: pd.DataFrame, kind: str, sel: dict[str, str | None]) -> Figure:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x, y, hue = sel["x"], sel["y"], sel["hue"]
    if kind == "scatter":
        sns.scatterplot(data=df, x=x, y=y, hue=hue, ax=ax, alpha=0.8)
    elif kind == "line":
        sns.lineplot(data=df, x=x, y=y, hue=hue, ax=ax)
    elif kind == "hist":
        sns.histplot(data=df, x=x, hue=hue, ax=ax, kde=True)
    elif kind == "box":
        sns.boxplot(data=df, x=x, y=y, hue=hue, ax=ax)
    elif kind == "violin":
        sns.violinplot(data=df, x=x, y=y, hue=hue, ax=ax, inner="quart")
    title = f"{kind}: {x}" if y is None else f"{kind}: {y} vs {x}"
    annotate.stylize_plot(title=title, ax=ax, rotate_xticks=30 if kind in ("box", "violin") else 0)
    return fig


def render_datasets() -> None:
    name = st.selectbox("Dataset", list(datasets.REGISTRY), key="ds_name")
    df = load_dataset(name)
    render_data_card(datasets.REGISTRY[name], df)

    st.markdown("#### Preview")
    st.dataframe(df.head(20), hide_index=True, width="stretch")

    st.markdown("#### Summary statistics")
    st.dataframe(df.describe(include="all").T, width="stretch")

    st.markdown("#### Interactive plot")
    kind = st.radio("Plot kind", PLOT_KINDS, horizontal=True, key="ds_kind")
    if not numeric_columns(df):
        st.info("This dataset has no numeric columns to plot.")
        return
    sel = plot_selectors(df, kind)
    if sel["x"] is None:
        st.info("No suitable x column for this plot kind.")
        return
    show_figure(draw_dataset_plot(df, kind, sel))


# ---------------------------------------------------------------------------
# Tab 3: Compare groups
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CompareConfig:
    df: pd.DataFrame
    x: str | None
    y: str | None
    test: str = "welch"
    correction: str = "holm"
    n_perm: int = 1000


def compare_controls() -> CompareConfig:
    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.selectbox("Dataset", list(datasets.REGISTRY), key="cmp_name")
    df = load_dataset(name)
    groups = categorical_columns(df)
    numeric = numeric_columns(df)
    if not groups or not numeric:
        return CompareConfig(df, None, None)
    default_x = groups.index("Arm") if "Arm" in groups else 0
    default_y = numeric.index("Outcome") if "Outcome" in numeric else 0
    with c2:
        x = st.selectbox("Group column", groups, index=default_x, key="cmp_x")
    with c3:
        y = st.selectbox("Numeric column", numeric, index=default_y, key="cmp_y")
    c4, c5, c6 = st.columns(3)
    with c4:
        test = st.selectbox("Test", TESTS, key="cmp_test")
    with c5:
        correction = st.selectbox("Correction", CORRECTIONS, key="cmp_corr")
    with c6:
        n_perm = st.slider("Permutations", 200, 5000, 1000, step=100, key="cmp_nperm")
    return CompareConfig(df, x, y, test, correction, n_perm)


def draw_comparison(
    df: pd.DataFrame, x: str, y: str, order: list[str], res: pd.DataFrame
) -> Figure:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=df, x=x, y=y, order=order, hue=x, legend=False, palette="colorblind", ax=ax)
    sns.stripplot(data=df, x=x, y=y, order=order, color="0.25", size=2.5, alpha=0.5, ax=ax)
    annotate.annotate_pairwise(ax, res, order=order, show_effect=True)
    annotate.stylize_plot(title=f"{y} by {x}", ax=ax)
    return fig


def render_compare() -> None:
    st.markdown(
        "Pairwise tests with multiplicity correction and effect sizes "
        "(`stats.compare_groups`), plus bootstrap group summaries."
    )
    cfg = compare_controls()
    if cfg.x is None or cfg.y is None:
        st.info("This dataset needs at least one categorical and one numeric column.")
        return
    sub, order = limit_levels(cfg.df, cfg.x)
    if len(order) < 2:
        st.info("Need at least two groups to compare.")
        return
    res = stats.compare_groups(
        sub,
        cfg.x,
        cfg.y,
        test=cfg.test,  # type: ignore[arg-type]
        correction=cfg.correction,  # type: ignore[arg-type]
        order=order,
        n_permutations=cfg.n_perm,
    )
    n_sig = int(res["p_adjusted"].lt(0.05).sum())
    st.markdown(
        f"**{len(res)} pairwise comparisons, {n_sig} significant after `{cfg.correction}`.**"
    )
    st.dataframe(res, hide_index=True, width="stretch")
    show_figure(draw_comparison(sub, cfg.x, cfg.y, order, res))

    st.markdown("#### Bootstrap group summary (mean, 95% CI)")
    summary = stats.group_summary(sub, cfg.x, cfg.y)
    st.dataframe(summary, hide_index=True, width="stretch")


# ---------------------------------------------------------------------------
# Tab 4: Palette check
# ---------------------------------------------------------------------------
def parse_hex_list(text: str) -> list[str]:
    return [tok.strip() for tok in text.split(",") if tok.strip()]


def palette_input() -> tuple[str, list[str]]:
    mode = st.radio("Source", ("Seaborn palette", "Custom hex"), horizontal=True, key="pal_mode")
    if mode == "Seaborn palette":
        c1, c2 = st.columns([2, 1])
        name = c1.selectbox("Palette", SEABORN_PALETTES, key="pal_name")
        n = c2.slider("Colours", 2, 12, 6, key="pal_n")
        return name, [mcolors.to_hex(c) for c in sns.color_palette(name, n)]
    text = st.text_input(
        "Comma-separated hex colours", "#0072B2, #E69F00, #009E73, #CC79A7", key="pal_hex"
    )
    return "custom", parse_hex_list(text)


def draw_cvd_grid(colors: list[str]) -> Figure:
    grid = color.cvd_palette_grid(colors)
    img = np.stack([grid[k] for k in VISION_TYPES])
    fig, ax = plt.subplots(figsize=(max(3.0, 0.7 * len(colors)), 2.6))
    ax.imshow(img, aspect="auto", interpolation="nearest")
    ax.set_yticks(range(len(VISION_TYPES)), VISION_TYPES)
    ax.set_xticks(range(len(colors)), [str(i) for i in range(len(colors))])
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    return fig


def render_palette_report(report: color.PaletteReport) -> None:
    if report.passes:
        st.success("PASS: colours stay distinguishable under CVD and clear the contrast floor.")
    else:
        st.error("FAIL: see warnings below.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Colours", report.n_colors)
    c2.metric("Min ΔE (normal)", f"{report.min_delta_e:.1f}")
    c3.metric("Min contrast on white", f"{report.min_contrast_on_white:.2f}:1")
    c4.metric("Min contrast on black", f"{report.min_contrast_on_black:.2f}:1")
    cvd = pd.DataFrame(
        {
            "vision": list(report.min_delta_e_cvd),
            "min ΔE": list(report.min_delta_e_cvd.values()),
            "ok": [v >= report.threshold for v in report.min_delta_e_cvd.values()],
        }
    )
    st.dataframe(cvd, hide_index=True, width="stretch")
    for w in report.warnings:
        st.warning(w)


def render_palette() -> None:
    st.markdown(
        "Checks pairwise ΔE*ab in normal vision and under simulated colour-vision "
        "deficiencies, plus WCAG contrast against the background."
    )
    name, colors = palette_input()
    if len(colors) < 2:
        st.info("Enter at least two colours.")
        return
    try:
        report = color.validate_palette(colors)
    except ValueError as exc:
        st.error(f"Could not parse colours: {exc}")
        return
    st.caption(f"Palette `{name}`: {', '.join(colors)}")
    render_palette_report(report)
    st.markdown("#### Simulated vision")
    show_figure(draw_cvd_grid(colors))


# ---------------------------------------------------------------------------
# Tab 5: Environment
# ---------------------------------------------------------------------------
def render_environment() -> None:
    st.markdown("#### Captured environment")
    st.json(repro.capture_environment())
    manifest = ROOT / "datasets" / "MANIFEST.json"
    st.markdown("#### Dataset manifest")
    if not manifest.exists():
        st.info("`datasets/MANIFEST.json` not found; run `smp-datasets` to regenerate.")
        return
    checks = repro.verify_manifest(manifest)
    table = pd.DataFrame({"file": list(checks), "sha256 matches": list(checks.values())})
    n_ok = int(table["sha256 matches"].sum())
    if n_ok == len(table):
        st.success(f"All {len(table)} files match the manifest.")
    else:
        st.error(f"{len(table) - n_ok} of {len(table)} files differ from the manifest.")
    st.dataframe(table, hide_index=True, width="stretch")


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
def main() -> None:
    st.set_page_config(page_title="SeabornMasterPro Explorer", layout="wide")
    st.title("📊 SeabornMasterPro Research Explorer")
    st.caption(
        "Exported figures, deterministic datasets with data cards, corrected group "
        "comparisons, palette accessibility and environment capture."
    )
    gallery, data, compare, palette, env = st.tabs(
        ["🖼 Gallery", "🗂 Datasets", "⚖️ Compare groups", "🎨 Palette check", "🧾 Environment"]
    )
    with gallery:
        render_gallery()
    with data:
        render_datasets()
    with compare:
        render_compare()
    with palette:
        render_palette()
    with env:
        render_environment()


main()
