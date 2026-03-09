# 📚 Seaborn Best Practices Guide

This guide provides battle-tested best practices for creating effective, publication-quality visualizations with Seaborn.

---

## 🎨 Visual Design Principles

### **1. Choose the Right Plot Type**

**For Distributions:**
- Single variable → `histplot()`, `kdeplot()`, `ecdfplot()`
- Bivariate → `jointplot()`, `hexbin in scatterplot()`
- Multiple groups → `displot()` with faceting

**For Categories:**
- Count frequency → `countplot()`
- Aggregated values → `barplot()`
- Full distribution → `boxplot()`, `violinplot()`
- Individual points → `stripplot()`, `swarmplot()`
- Trends → `pointplot()`

**For Relationships:**
- Scatter → `scatterplot()` or `relplot(kind="scatter")`
- Line/Time series → `lineplot()` or `relplot(kind="line")`
- With regression → `regplot()` or `lmplot()`

**For Matrices:**
- Correlations → `heatmap()` with diverging palette
- Hierarchical clustering → `clustermap()`

---

## 🎨 Color Usage

### **Golden Rules:**

1. **Limit Colors:**
   - Maximum 5-7 distinct colors for categorical data
   - Use shades of the same color for ordered categories

2. **Choose Appropriate Palettes:**
   - **Sequential** (Blues, Greens): Ordered data, heatmaps
   - **Diverging** (RdBu, coolwarm): Data with meaningful center (0, mean)
   - **Qualitative** (Set2, tab10): Unordered categories

3. **Accessibility:**
   - Use colorblind-friendly palettes (`colorblind` palette)
   - Ensure sufficient contrast
   - Don't rely solely on color (use shapes, patterns, labels)

4. **Consistency:**
   - Use same colors for same categories across all plots
   - Create color dictionaries for precise mapping

```python
# Good: Consistent color mapping
category_colors = {
    'A': '#FF6B6B',
    'B': '#4ECDC4',
    'C': '#45B7D1'
}
sns.barplot(..., palette=category_colors)
sns.boxplot(..., palette=category_colors)
```

---

## 📏 Plot Sizing and Layout

### **Figure Sizes:**

```python
# Single plot
plt.figure(figsize=(10, 6))  # Width, Height in inches

# Multiple subplots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Figure-level functions
sns.relplot(..., height=5, aspect=1.5)  # height * aspect = width
```

### **Aspect Ratios:**
- **Square** (1:1): Correlation matrices, symmetric data
- **Wide** (1.5:1 or 2:1): Time series, distributions, bar charts
- **Tall** (1:1.5): Categorical data with many categories

### **Resolution:**
- **Screen**: 100-150 DPI
- **Print/Publication**: 300-600 DPI

```python
plt.savefig('plot.png', dpi=300, bbox_inches='tight')
```

---

## 📝 Labels and Annotations

### **Always Include:**

1. **Descriptive Title:** What does the plot show?
2. **Axis Labels:** Include units (e.g., "Sales ($)", "Distance (km)")
3. **Legend:** When using `hue`, `style`, or `size`
4. **Data Source:** In caption or subtitle

```python
plt.title("Monthly Sales Trends by Region (2024)", fontweight='bold', fontsize=14)
plt.xlabel("Month", fontsize=12)
plt.ylabel("Sales (USD)", fontsize=12)
plt.legend(title="Region", loc='upper left')
```

### **Fonts:**
- Title: 14-16pt, bold
- Axis labels: 12pt
- Tick labels: 10pt
- Annotations: 9-10pt

---

## 🔢 Statistical Considerations

### **Error Bars:**

```python
# Confidence Interval (default: 95%)
sns.barplot(..., errorbar='ci')  # Use for: inferring population mean

# Standard Deviation
sns.barplot(..., errorbar='sd')  # Use for: showing data spread

# Standard Error
sns.barplot(..., errorbar='se')  # Use for: precision of mean estimate

# No error bars
sns.barplot(..., errorbar=None)  # Use when: clutters the plot
```

### **Estimators:**

```python
# Mean (default) - affected by outliers
sns.barplot(..., estimator=np.mean)

# Median - robust to outliers
sns.barplot(..., estimator=np.median)

# Choose based on your data distribution
```

---

## 🚫 Common Pitfalls to Avoid

### **1. Truncated Y-Axis**
```python
# ❌ Bad: Exaggerates differences
ax.set_ylim(90, 100)

# ✅ Good: Start from 0 for bar charts
ax.set_ylim(0, 100)
```

### **2. Too Many Categories**
```python
# ❌ Bad: 20 categories in a bar chart
# ✅ Good: Group into "Top 10" + "Others"
```

### **3. Overplotting**
```python
# ❌ Bad: 10,000 points on scatterplot
sns.scatterplot(...)

# ✅ Good: Use hexbin or KDE
sns.jointplot(..., kind='hex')
```

### **4. Rainbow Palettes for Sequential Data**
```python
# ❌ Bad: Rainbow colors don't show order
sns.heatmap(..., cmap='rainbow')

# ✅ Good: Sequential palette
sns.heatmap(..., cmap='Blues')
```

### **5. Missing Context**
```python
# ❌ Bad: No title, labels, or units
sns.barplot(x='category', y='value', data=df)

# ✅ Good: Descriptive and complete
sns.barplot(x='category', y='value', data=df)
plt.title("Average Sales by Category")
plt.xlabel("Product Category")
plt.ylabel("Average Sales ($)")
```

---

## ✅ Quick Checklist

Before finalizing any visualization:

- [ ] Plot type appropriate for data?
- [ ] Colors intentional and accessible?
- [ ] Title describes what plot shows?
- [ ] Axis labels include units?
- [ ] Legend present if needed?
- [ ] Text readable at intended size?
- [ ] Error bars explained (if present)?
- [ ] No misleading truncation?
- [ ] Data source cited?
- [ ] Saved at appropriate resolution?

---

## 📊 Example: Before & After

### Before (Poor Practice):
```python
sns.barplot(x='day', y='total_bill', data=tips)
plt.show()
```

### After (Best Practice):
```python
# Apply consistent theme
sns.set_theme(style='whitegrid', context='notebook', palette='Set2')

# Create plot with proper sizing
plt.figure(figsize=(10, 6))
sns.barplot(
    data=tips,
    x='day',
    y='total_bill',
    errorbar='ci',
    palette='Set2',
    alpha=0.8
)

# Add descriptive labels
plt.title("Average Restaurant Bill by Day of Week", 
          fontweight='bold', fontsize=14)
plt.xlabel("Day of Week", fontsize=12)
plt.ylabel("Average Total Bill ($)", fontsize=12)

# Rotate x-labels if needed
plt.xticks(rotation=0)

# Save with high resolution
plt.tight_layout()
plt.savefig('restaurant_bills_by_day.png', dpi=300, bbox_inches='tight')
plt.show()
```

---

## 📚 Additional Resources

- [Seaborn Official Tutorial](https://seaborn.pydata.org/tutorial.html)
- [ColorBrewer (Palette Design)](https://colorbrewer2.org/)
- [Data Visualization Best Practices (Storytelling with Data)](http://www.storytellingwithdata.com/)

---

**Pro Tip:** Keep these best practices in mind, but remember: the best visualization is one that clearly communicates your story to your audience!
