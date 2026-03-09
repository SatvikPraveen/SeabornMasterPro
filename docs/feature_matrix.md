# 📊 SeabornMasterPro Feature Matrix

This matrix shows which Seaborn features are covered in each notebook.

---

## 🗺️ Notebook Coverage Overview

| Notebook | Focus | Level | Key Functions |
|----------|-------|-------|---------------|
| **01** | Setup & Basics | Beginner | `histplot()`, `scatterplot()`, `boxplot()` |
| **02** | Distributions & Relationships | Beginner-Intermediate | `kdeplot()`, `ecdfplot()`, `lineplot()`, `regplot()`, `residplot()` |
| **03** | Categorical & Matrix | Intermediate | `countplot()`, `violinplot()`, `swarmplot()`, `stripplot()`, `pointplot()`, `heatmap()`, `clustermap()` |
| **04** | Multi-Panel Dashboards | Intermediate | `pairplot()`, `displot()`, `catplot()`, `FacetGrid()` |
| **05** | Real-World EDA | Intermediate | Integration of multiple plots |
| **06** | Time Series (EXPANDED) | Intermediate-Advanced | `lineplot()` advanced features, multi-series, confidence intervals, seasonality |
| **07** | Figure-Level Functions | Advanced | `relplot()`, `lmplot()`, `jointplot()`, `displot()`, axes vs figure-level |
| **08** | Advanced Categorical | Advanced | `barplot()`, custom estimators, statistical annotations |
| **09** | Styling & Customization | Advanced | Themes, palettes, custom colors, color theory |
| **10** | Statistical Parameters | Advanced | `estimator`, `errorbar`, custom aggregations |

---

## 📈 Plot Type Coverage

| Plot Function | Notebook(s) | Type | Purpose |
|---------------|-------------|------|---------|
| **Distribution Plots** ||||
| `histplot()` | 01, 02, 05 | Axes | Histogram with bins |
| `kdeplot()` | 02, 05 | Axes | Kernel density estimate |
| `ecdfplot()` | 02 | Axes | Cumulative distribution |
| `rugplot()` | 02 | Axes | Data ticks on axis |
| `displot()` | 04, 07 | Figure | Faceted distributions |
| **Relationship Plots** ||||
| `scatterplot()` | 01, 02, 07 | Axes | Scatter plot |
| `lineplot()` | 02, 06 | Axes | Line plot / time series |
| `regplot()` | 02 | Axes | Regression plot |
| `residplot()` | 02 | Axes | Residual plot |
| `relplot()` | 07 | Figure | Faceted scatter/line |
| `lmplot()` | 07 | Figure | Faceted regression |
| `jointplot()` | 07 | Figure | Bivariate with marginals |
| **Categorical Plots** ||||
| `barplot()` | 08 | Axes | Aggregated values with error bars |
| `countplot()` | 03, 08 | Axes | Frequency counts |
| `boxplot()` | 01, 03 | Axes | Box-and-whisker |
| `violinplot()` | 03 | Axes | Violin (distribution shape) |
| `stripplot()` | 03 | Axes | Jittered points |
| `swarmplot()` | 03 | Axes | Positioned points 
 |
| `pointplot()` | 03 | Axes | Point estimates with CI |
| `catplot()` | 04 | Figure | Faceted categorical |
| **Matrix Plots** ||||
| `heatmap()` | 03, 05 | Axes | Heatmap with annotations |
| `clustermap()` | 03 | Figure | Clustered heatmap |
| **Multi-Panel** ||||
| `pairplot()` | 04 | Figure | Pairwise relationships |
| `FacetGrid()` | 04 | Figure | Custom grid |

---

## 🎨 Styling & Customization Coverage

| Feature | Notebook(s) | Description |
|---------|-------------|-------------|
| **Themes** | 09 | `set_theme()`, styles, contexts |
| **Palettes** | 09 | Sequential, diverging, qualitative |
| **Custom Colors** | 09 | Hex codes, color dictionaries |
| **Color Theory** | 09 | When to use which palette type |
| **Plot Utilities** | All | `plot_utils.py` functions |

---

## 📊 Advanced Features Coverage

| Feature | Notebook(s) | Details |
|---------|-------------|---------|
| **Custom Estimators** | 08, 10 | `np.median`, `np.sum`, percentiles, custom functions |
| **Error Bars** | 08, 10 | `errorbar="ci"`, `"sd"`, `"se"`, `("pi", 95)` |
| **Faceting** | 04, 07 | `col`, `row`, `col_wrap` parameters |
| **Hue/Style/Size** | 02, 03, 04, 06, 07 | Multiple visual encodings |
| **Confidence Intervals** | 06, 08, 10 | CI calculation and visualization |
| **Time Series** | 06 | Multi-series, seasonality, rolling stats, events |
| **Statistical Annotations** | 08 | P-values, significance markers |

---

## 📚 Conceptual Coverage

| Concept | Notebook(s) | What You Learn |
|---------|-------------|----------------|
| **Axes vs Figure-Level** | 07 | When to use each paradigm |
| **Best Practices** | docs/best_practices.md | Visualization principles |
| **Plot Selection** | docs/plot_comparison.md | Decision guide |
| **Troubleshooting** | docs/troubleshooting.md | Common issues & solutions |
| **Color Theory** | 09 | Sequential vs diverging vs qualitative |
| **Statistical Parameters** | 10 | Estimators, error bars, aggregations |
| **EDA Workflow** | 05 | Complete exploratory workflow |

---

## 🎯 Learning Path

### **Beginner Path:**
1. Notebook 01: Setup & Basics
2. Notebook 02: Distributions & Relationships
3. Notebook 03: Categorical & Matrix
4. docs/best_practices.md

### **Intermediate Path:**
5. Notebook 04: Multi-Panel Dashboards
6. Notebook 05: Real-World EDA
7. Notebook 06: Time Series
8. docs/plot_comparison.md

### **Advanced Path:**
9. Notebook 07: Figure-Level Functions
10. Notebook 08: Advanced Categorical
11. Notebook 09: Styling & Customization
12. Notebook 10: Statistical Parameters

---

## ✅ Coverage Checklist

### **Core Seaborn Functions (30/30)** ✅
- [x] Distribution plots (4/4): `histplot`, `kdeplot`, `ecdfplot`, `rugplot`
- [x] Relationship plots (4/4): `scatterplot`, `lineplot`, `regplot`, `residplot`
- [x] Categorical plots (7/7): `barplot`, `countplot`, `boxplot`, `violinplot`, `stripplot`, `swarmplot`, `pointplot`
- [x] Matrix plots (2/2): `heatmap`, `clustermap`
- [x] Figure-level (6/6): `relplot`, `displot`, `catplot`, `lmplot`, `jointplot`, `pairplot`
- [x] Grid (1/1): `FacetGrid`

### **Advanced Features** ✅
- [x] Custom estimators
- [x] Error bar options (ci, sd, se, pi)
- [x] Faceting (col, row, col_wrap)
- [x] Multi-dimensional encoding (hue, style, size)
- [x] Custom color palettes
- [x] Time series advanced features
- [x] Statistical annotations
- [x] Themes and styling

### **Documentation** ✅
- [x] Best practices guide
- [x] Plot selection decision guide
- [x] Troubleshooting guide
- [x] Feature matrix (this file)
- [x] Utility functions documented

---

## 🚀 What's NOT Covered (Advanced/Specialized)

- **Animation** - Requires matplotlib.animation
- **3D Plots** - Requires mplot3d
- **Geographic Maps** - Requires geopandas/cartopy
- **Interactive Plots** - Requires plotly/bokeh
- **Network Graphs** - Requires networkx
- **Statistical Models** - Requires statsmodels (beyond visualization)

---

## 📊 Quick Lookup: "I need to... "

| Task | Notebook | Function |
|------|----------|----------|
| ...show distribution of one variable | 02 | `histplot()` or `kdeplot()` |
| ...compare two variables | 02, 07 | `scatterplot()` or `jointplot()` |
| ...show correlation matrix | 03, 05 | `heatmap()` |
| ...compare categories | 03, 08 | `barplot()`, `boxplot()`, or `violinplot()` |
| ...create time series | 06 | `lineplot()` |
| ...make multi-panel plots | 04, 07 | `relplot()`, `displot()`, or `catplot()` |
| ...customize colors | 09 | Color palettes and theory |
| ...add statistical tests | 08, 10 | Statistical annotations |
| ...understand figure vs axes | 07 | Figure-level concepts |

---

**Note:** All notebooks use functions from `utils/plot_utils.py` for consistent theming, saving, and styling.
