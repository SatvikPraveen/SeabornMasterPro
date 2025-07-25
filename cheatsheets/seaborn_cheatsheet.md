# 📑 `cheatsheets/seaborn_cheatsheet.md`

> 🧠 Master Seaborn with this single-page summary — covering syntax, plot types, arguments, and best practices. Ideal for quick reference, interviews, and revision.

---

## 🎨 Basic Setup

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Apply theme
sns.set_theme(style="whitegrid", context="notebook", palette="deep")
```

---

## 📦 Built-In Datasets

```python
sns.get_dataset_names()
df = sns.load_dataset("tips")
```

---

## 🧭 Styling & Themes

```python
sns.set_style("whitegrid")           # Themes: white, dark, ticks
sns.set_context("notebook")          # Contexts: paper, talk, poster
sns.set_palette("muted")             # Palettes: deep, bright, Set2...
```

---

## 📊 Distribution Plots

| Plot      | Function                                         |
| --------- | ------------------------------------------------ |
| Histogram | `sns.histplot(data, x="col", bins=20, kde=True)` |
| KDE       | `sns.kdeplot(data, x="col", fill=True)`          |
| ECDF      | `sns.ecdfplot(data, x="col", hue="group")`       |
| Rug       | `sns.rugplot(data, x="col")`                     |

---

## 📈 Relationship Plots

| Plot        | Function                                        |
| ----------- | ----------------------------------------------- |
| Scatterplot | `sns.scatterplot(data, x, y, hue, style, size)` |
| Lineplot    | `sns.lineplot(data, x, y, ci="sd")`             |
| Regplot     | `sns.regplot(x, y, data, ci=95)`                |
| Residuals   | `sns.residplot(x, y, data)`                     |

---

## 📦 Categorical Plots

| Plot       | Function                                                   |
| ---------- | ---------------------------------------------------------- |
| Barplot    | `sns.barplot(x, y, data, ci, estimator=np.mean)`           |
| Countplot  | `sns.countplot(x, data)`                                   |
| Boxplot    | `sns.boxplot(x, y, data)`                                  |
| Violinplot | `sns.violinplot(x, y, data, split=True, inner="quartile")` |
| Stripplot  | `sns.stripplot(x, y, data, jitter=True)`                   |
| Swarmplot  | `sns.swarmplot(x, y, data)`                                |
| Pointplot  | `sns.pointplot(x, y, data, hue, dodge=True)`               |

---

## 📐 Matrix Plots

| Plot       | Function                                                |
| ---------- | ------------------------------------------------------- |
| Heatmap    | `sns.heatmap(corr_matrix, annot=True, cmap="coolwarm")` |
| Clustermap | `sns.clustermap(df, annot=True, cmap="viridis")`        |

---

## 🧩 Multi-Panel Plots

| Plot              | Use                             |
| ----------------- | ------------------------------- |
| `sns.pairplot()`  | Pairwise numeric scatter matrix |
| `sns.catplot()`   | Faceted categorical plots       |
| `sns.displot()`   | Faceted histograms or KDEs      |
| `sns.FacetGrid()` | Fully customizable grid maps    |

---

## 🕒 Time Series (Lineplot)

```python
sns.lineplot(data=df, x="Date", y="value")
# Optional:
df["rolling_avg"] = df["value"].rolling(7).mean()
```

---

## 🔧 Axis & Titles

```python
plt.title("Title")
plt.xlabel("X-axis Label")
plt.ylabel("Y-axis Label")
plt.xticks(rotation=45)
plt.tight_layout()
```

---

## 🧰 Common Parameters

| Param        | Use                                      |
| ------------ | ---------------------------------------- |
| `hue=`       | Color separation by category             |
| `style=`     | Marker/line style by group               |
| `size=`      | Marker size                              |
| `ci=`        | Confidence interval                      |
| `estimator=` | Custom agg function (e.g., `np.median`)  |
| `palette=`   | Set color palette                        |
| `dodge=`     | Separate elements (e.g., in `pointplot`) |

---

## 🖼 Saving Plots

```python
plt.savefig("plot_name.png", dpi=300, bbox_inches="tight")
```

Or via utility:

```python
from plot_utils import save_fig
save_fig("exports/01_intro/plot.png")
```

---

## 📆 Formatting Date Axes (for Time Series)

```python
from plot_utils import format_date_axis
format_date_axis(date_format="%b %Y", major_locator="month")
```

---

## 🧠 Best Practices

- ✅ Use `FacetGrid` or `catplot` for subgroup comparisons
- ✅ Combine Seaborn with Matplotlib for full control
- ✅ Always check `df.info()` and `.describe()` before plotting
- ✅ Rotate x-ticks for categorical axis when needed
- ✅ Save high-res PNGs for publication

---
