# 🗺️ Seaborn Plot Selection Decision Guide

Not sure which Seaborn plot to use? This guide helps you choose the right visualization for your data and question.

---

## 🎯 Quick Decision Tree

```
START
│
├─ Do you want to show DISTRIBUTION?
│   ├─ One variable?
│   │   ├─ Histogram → histplot()
│   │   ├─ Smooth density → kdeplot()
│   │   └─ Cumulative → ecdfplot()
│   └─ Two variables?
│       ├─ With marginals → jointplot()
│       ├─ Multiple groups → displot(col=...)
│       └─ Hexagonal bins → hexbin plot
│
├─ Do you want to show RELATIONSHIPS?
│   ├─ Scatter plot?
│   │   ├─ Single → scatterplot()
│   │   └─ Faceted → relplot(kind="scatter")
│   ├─ Line plot / Time series?
│   │   ├─ Single → lineplot()
│   │   └─ Faceted → relplot(kind="line")
│   └─ With regression?
│       ├─ Single → regplot()
│       └─ Faceted → lmplot()
│
├─ Do you want to show CATEGORIES?
│   ├─ Just counts?
│   │   └─ countplot()
│   ├─ Aggregated values?
│   │   ├─ With error bars → barplot()
│   │   └─ Trend over categories → pointplot()
│   └─ Full distribution?
│       ├─ Quartiles + outliers → boxplot()
│       ├─ Distribution shape → violinplot()
│       ├─ All points (small data) → stripplot() or swarmplot()
│       └─ Faceted comparison → catplot()
│
└─ Do you want to show MATRICES?
    ├─ Correlation → heatmap(cmap="RdBu_r")
    └─ With clustering → clustermap()
```

---

## 📊 Categorical Plots: Detailed Comparison

| Your Question | Best Plot | Why? |
|---------------|-----------|------|
| "How many items in each category?" | `countplot()` | Shows frequency only |
| "What's the average per category?" | `barplot()` | Shows mean with CI |
| "What's the range and median?" | `boxplot()` | Shows quartiles + outliers |
| "What's the distribution shape?" | `violinplot()` | Shows full density |
| "Show me all individual points" | `stripplot()` or `swarmplot()` | Every data point visible |
| "How does it trend across categories?" | `pointplot()` | Shows trends with CI |
| "Compare multiple groupings" | `catplot()` with faceting | Multiple dimensions |

---

## 📈 When to Use Figure-Level vs Axes-Level

| Situation | Use | Example |
|-----------|-----|---------|
| **Quick faceting needed** | Figure-level | `relplot(col="category")` |
| **Custom subplot layout** | Axes-level | `fig, ax = plt.subplots(2,2)` |
| **Combining different plot types** | Axes-level | Scatter + box in same figure |
| **Consistent multi-panel layout** | Figure-level | `displot()`, `catplot()` |
| **Maximum flexibility** | Axes-level | Complex dashboard |
| **Less code preferred** | Figure-level | One-liners with facets |

**Figure-Level Functions:**
- `relplot()` → `scatterplot()` + `lineplot()`
- `displot()` → `histplot()` + `kdeplot()` + `ecdfplot()`
- `catplot()` → All categorical plots
- `lmplot()` → `regplot()`
- `jointplot()` → (unique, no axes equivalent)

---

## 🎨 Color Palette Selection

| Data Type | Palette Type | Examples | When to Use |
|-----------|--------------|----------|-------------|
| **Ordered** (1→10, low→high) | Sequential | `Blues`, `Greens`, `YlOrRd` | Heatmaps, ordered categories |
| **Diverging** (negative ← 0 → positive) | Diverging | `RdBu`, `coolwarm`, `Spectral` | Correlations, deviations |
| **Unordered categories** | Qualitative | `Set1`, `Set2`, `tab10` | Species, regions, products |
| **Continuous gradients** | Sequential | `viridis`, `plasma` | Continuous numeric scales |

---

## 🔍 Distribution Plot Decision Matrix

| Question | Plot Type | Parameters to Consider |
|----------|-----------|------------------------|
| "What's the shape of the distribution?" | `kdeplot()` | `fill=True` for area |
| "How many bins should I use?" | `histplot()` | Start with `bins=20`, adjust |
| "Are there multiple modes?" | `kdeplot()` or `violinplot()` | Easier to see than histogram |
| "What's the cumulative distribution?" | `ecdfplot()` | Percentile interpretation |
| "Show two variables together" | `jointplot(kind="kde")` | Central + marginal |
| "Compare distributions across groups" | `displot(col=...)` | Faceted histograms/KDE |

---

## 📏 Error Bar Selection

| Goal | Use | Interpretation |
|------|-----|----------------|
| **Show uncertainty in mean** | `errorbar="ci"` | 95% CI: "We're 95% confident true mean is in this range" |
| **Show data spread** | `errorbar="sd"` | ~68% of data within ±1 SD |
| **Show precision of estimate** | `errorbar="se"` | How precise is our mean estimate? |
| **Predict future observations** | `errorbar=("pi", 95)` | Where will 95% of new observations fall? |
| **Clean visualization** | `errorbar=None` | No error bars (when they clutter) |

---

## 🧮 Estimator Selection

| Question | Estimator | Why? |
|----------|-----------|------|
| "What's typical?" | `np.mean` (default) | Good for normal distributions |
| "What's typical (with outliers)?" | `np.median` | Robust to outliers |
| "What's the total?" | `np.sum` | Total sales, counts, etc. |
| "What's the range?" | Custom: `lambda x: x.max() - x.min()` | Variability measure |
| "What's the 90th percentile?" | `lambda x: np.percentile(x, 90)` | High-end performance |

---

## 📊 Multi-Dimensional Data

| Number of Variables | Best Approach | Example |
|---------------------|---------------|---------|
| **1 variable** | Single distribution plot | `histplot(x)` |
| **2 variables** | Scatter or jointplot | `scatterplot(x, y)` |
| **3 variables** | Add `hue` | `scatterplot(x, y, hue=z)` |
| **4 variables** | Add `size` | `scatterplot(x, y, hue=z, size=w)` |
| **5 variables** | Add `style` | `scatterplot(x, y, hue=z, size=w, style=v)` |
| **6+ variables** | Faceting | `relplot(x, y, hue=z, col=w, row=v)` |
| **Many variables** | Pairplot or heatmap | `pairplot()` or correlation matrix |

---

## ⏱️ Time Series Specifics

| Scenario | Plot | Key Parameters |
|----------|------|----------------|
| **Single time series** | `lineplot()` | `x="date", y="value"` |
| **Multiple series** | `lineplot(hue=...)` | Different colors per series |
| **With confidence bands** | `lineplot(errorbar="ci")` | Shows uncertainty |
| **Seasonal patterns** | Aggregate + `lineplot()` | Group by day/month/quarter |
| **Comparing many series** | `relplot(col=...)` | Faceted time series |
| **With events** | `lineplot()` + `axvline()` | Annotate important dates |

---

## 🎯 Common Use Cases

### **Comparing Groups**
- **Few categories (< 5):** `barplot()` or `boxplot()`
- **Many categories (> 10):** `heatmap()` or filter to top N
- **With subcategories:** Use `hue` parameter

### **Showing Trends**
- **Over time:** `lineplot()` or `pointplot()`
- **Across ordered categories:** `pointplot()`
- **With faceting:** `relplot(kind="line")`

### **Exploring Correlations**
- **Two variables:** `jointplot(kind="reg")`
- **Many variables:** `pairplot()` or `heatmap(corr())`
- **With clusters:** `clustermap()`

### **Publication-Quality Figures**
- **Use figure-level functions** for consistent layouts
- **Set appropriate context:** `sns.set_context("paper")` or `"talk"`
- **Choose colorblind-friendly palettes**
- **Save with high DPI:** `dpi=300` or `600`

---

## 📝 Quick Reference Table

| I want to show... | Use this plot |
|-------------------|---------------|
| Frequency counts | `countplot()` |
| Averages with error bars | `barplot()` |
| Medians and quartiles | `boxplot()` |
| Distribution shapes | `violinplot()` or `kdeplot()` |
| All individual points | `stripplot()` or `swarmplot()` |
| Correlation between two variables | `scatterplot()` or `jointplot()` |
| Time trends | `lineplot()` |
| Time trends with facets | `relplot(kind="line")` |
| Regression line | `regplot()` or `lmplot()` |
| Correlation matrix | `heatmap()` |
| Hierarchical patterns | `clustermap()` |
| Distribution + count | `histplot()` |
| Cumulative distribution | `ecdfplot()` |
| Multiple distributions | `displot(col=...)` or `catplot()` |
| Pairwise relationships | `pairplot()` |

---

## Pro Tips

1️⃣ **Start Simple:** Begin with basic plot, then add `hue`, `style`, `size` as needed

2️⃣ **Iterate:** Try 2-3 plot types before deciding

3️⃣ **Consider Your Audience:** Technical → more detail okay; Executive → simpler is better

4️⃣ **Tell a Story:** Choose plots that highlight your key message

5️⃣ **Test Colorblind:** Use online simulators to verify accessibility

---

**Remember:** The best plot is the one that most clearly answers your question and communicates to your audience!
