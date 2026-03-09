# 🔧 Seaborn Troubleshooting Guide

Common issues and their solutions when working with Seaborn visualizations.

---

## 🚨 Import and Installation Issues

### **Problem: ModuleNotFoundError: No module named 'seaborn'**
```python
ModuleNotFoundError: No module named 'seaborn'
```

**Solution:**
```bash
# Install seaborn
pip install seaborn

# Or with specific version
pip install seaborn>=0.12

# Verify installation
python -c "import seaborn; print(seaborn.__version__)"
```

---

### **Problem: ImportError with matplotlib backend**
```python
ImportError: Cannot load backend 'TkAgg'
```

**Solution:**
```python
# Add before importing matplotlib/seaborn
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import seaborn as sns
import matplotlib.pyplot as plt
```

---

## 📊 Plot Display Issues

### **Problem: Plots not showing**
```python
sns.histplot(data=df, x='column')
# Nothing appears!
```

**Solution:**
```python
# Add plt.show() at the end
sns.histplot(data=df, x='column')
plt.show()  # ← Must call this

# Or if in Jupyter
%matplotlib inline  # Add at top of notebook
```

---

### **Problem: Multiple plots overlapping**
```python
# Plots appear on top of each other
sns.scatterplot(...)
sns.lineplot(...)  # Overlaps with scatter
```

**Solution:**
```python
# Create new figure for each plot
plt.figure()
sns.scatter plot(...)
plt.show()

plt.figure()
sns.lineplot(...)
plt.show()

# Or use subplots
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
sns.scatterplot(..., ax=axes[0])
sns.lineplot(..., ax=axes[1])
plt.show()
```

---

### **Problem: Figure too small/large**
```python
# Plot is tiny or huge
```

**Solution:**
```python
# For axes-level plots
plt.figure(figsize=(10, 6))  # (width, height) in inches
sns.scatterplot(...)

# For figure-level plots
sns.relplot(..., height=5, aspect=1.5)  # width = height * aspect
```

---

## 🎨 Color and Style Issues

### **Problem: Colors not changing**
```python
sns.barplot(..., palette='Set2')  # Still using default colors!
```

**Solution:**
```python
# palette parameter must match the hue parameter
sns.barplot(data=df, x='category', y='value', hue='group', palette='Set2')
#                                                  ↑           ↑
#                                              These must align

# Without hue, use 'color' instead
sns.barplot(data=df, x='category', y='value', color='steelblue')
```

---

### **Problem: Legend not appearing**
```python
sns.scatterplot(data=df, x='x', y='y', hue='category')
# No legend shows!
```

**Solution:**
```python
# Ensure you're using hue/style/size
sns.scatterplot(data=df, x='x', y='y', hue='category')
plt.legend()  # Explicitly add legend

# Or position it
plt.legend(loc='upper right', title='Category')

# For figure-level plots
g = sns.relplot(data=df, x='x', y='y', hue='category')
g.add_legend()
```

---

### **Problem: Theme not applying**
```python
sns.set_theme(style='darkgrid')
# Still looks like default!
```

**Solution:**
```python
# Apply theme BEFORE creating plots
sns.set_theme(style='darkgrid')  # Do this first
sns.scatterplot(...)  # Then create plots

# If using figure-level functions
sns.set_theme(style='darkgrid')
g = sns.relplot(...)  # Theme will apply
```

---

## 📏 Axis and Label Issues

### **Problem: X-axis labels overlapping**
```python
# Labels are unreadable, all on top of each other
```

**Solution:**
```python
# Rotate labels
plt.xticks(rotation=45)

# Or rotate and align
plt.xticks(rotation=45, ha='right')

# For long labels, reduce font size
plt.xticks(rotation=90, fontsize=9)

# Or limit number of categories
top_10 = df.nlargest(10, 'value')
sns.barplot(data=top_10, ...)
```

---

### **Problem: Y-axis not starting at zero**
```python
# Bar chart doesn't start at 0, looks misleading
```

**Solution:**
```python
sns.barplot(...)
plt.ylim(0, None)  # Force y-axis to start at 0

# Or set specific range
plt.ylim(0, 100)
```

---

### **Problem: Axis labels missing**
```python
# No labels on axes!
```

**Solution:**
```python
# For axes-level plots
sns.scatterplot(...)
plt.xlabel('X Variable')
plt.ylabel('Y Variable')
plt.title('My Plot Title')

# For figure-level plots
g = sns.relplot(...)
g.set_axis_labels('X Variable', 'Y Variable')
g.fig.suptitle('My Plot Title', y=1.02)
```

---

## 📊 Data Issues

### **Problem: KeyError: 'column_name'**
```python
KeyError: 'total_bill'
```

**Solution:**
```python
# Check column names
print(df.columns.tolist())

# Verify exact spelling and case
df.columns = df.columns.str.strip()  # Remove whitespace
df.columns = df.columns.str.lower()  # Lowercase all

# Or use rename
df = df.rename(columns={'Total Bill': 'total_bill'})
```

---

### **Problem: TypeError: unhashable type: 'list'**
```python
TypeError: unhashable type: 'list'
```

**Solution:**
```python
# Trying to use list as hue
sns.scatterplot(data=df, x='x', y='y', hue=['A', 'B'])  # ❌ Wrong

# Use column name instead
sns.scatterplot(data=df, x='x', y='y', hue='category')  # ✅ Correct
```

---

### **Problem: Data not showing (empty plot)**
```python
# Axes appear but no data visible
```

**Solution:**
```python
# Check for NaN values
print(df.isna().sum())

# Drop NaN
df_clean = df.dropna(subset=['x', 'y'])
sns.scatterplot(data=df_clean, x='x', y='y')

# Or check data range
print(df[['x', 'y']].describe())

# Verify data types
print(df.dtypes)
```

---

## 🔢 Statistical Issues

### **Problem: ValueError: Setting an array element with a sequence**
```python
ValueError: setting an array element with a sequence
```

**Solution:**
```python
# Estimator returning array instead of scalar
def wrong_estimator(x):
    return x  # Returns array! ❌

def correct_estimator(x):
   return x.mean()  # Returns single value ✅

sns.barplot(data=df, x='category', y='value', estimator=correct_estimator)
```

---

### **Problem: Error bars too large/small**
```python
# Error bars don't look right
```

**Solution:**
```python
# Choose appropriate error bar type
sns.barplot(..., errorbar='ci')   # 95% confidence interval (default)
sns.barplot(..., errorbar='sd')   # Standard deviation
sns.barplot(..., errorbar='se')   # Standard error
sns.barplot(..., errorbar=('ci', 99))  # 99% CI
sns.barplot(..., errorbar=None)   # No error bars
```

---

## 🖼️ Saving Issues

### **Problem: Saved figure is blank/empty**
```python
plt.savefig('plot.png')
sns.scatterplot(...)  # Wrong order!
```

**Solution:**
```python
# Create plot FIRST, then save
sns.scatterplot(...)
plt.savefig('plot.png', dpi=300, bbox_inches='tight')
plt.show()  # Show after saving
```

---

### **Problem: Saved figure is cut off**
```python
# Labels or title cut off in saved image
```

**Solution:**
```python
# Use bbox_inches='tight'
plt.savefig('plot.png', bbox_inches='tight')

# Or adjust layout before saving
plt.tight_layout()
plt.savefig('plot.png')
```

---

### **Problem: Low quality saved image**
```python
# Image looks pixelated
```

**Solution:**
```python
# Increase DPI
plt.savefig('plot.png', dpi=300)  # Default is 100

# For publications
plt.savefig('plot.png', dpi=600, bbox_inches='tight')

# Save as vector format
plt.savefig('plot.pdf')  # Scalable!
plt.savefig('plot.svg')  # Also scalable
```

---

## ⚡ Performance Issues

### **Problem: Plotting is very slow**
```python
# Takes minutes to create plot
```

**Solution:**
```python
# For large datasets, sample first
df_sample = df.sample(10000)  # Random 10k rows
sns.scatterplot(data=df_sample, ...)

# Or use hexbin for dense scatterplots
sns.jointplot(data=df, x='x', y='y', kind='hex')

# Reduce bootstrap iterations
sns.barplot(..., errorbar=('ci', 95), n_boot=100)  # Default is 1000
```

---

### **Problem: Out of memory error**
```python
MemoryError
```

**Solution:**
```python
# Work with smaller chunks
# Sample data
df_small = df.sample(frac=0.1)  # 10% of data

# Or use aggregation first
df_agg = df.groupby('category')['value'].mean().reset_index()
sns.barplot(data=df_agg, x='category', y='value')
```

---

## 🎯 FacetGrid Issues

### **Problem: Can't modify FacetGrid plots**
```python
g = sns.relplot(...)
plt.title('Title')  # Doesn't work!
```

**Solution:**
```python
# Use FacetGrid methods
g = sns.relplot(...)
g.fig.suptitle('Overall Title', y=1.02)
g.set_axis_labels('X Label', 'Y Label')
g.set_titles('Category: {col_name}')

# For individual axes
for ax in g.axes.flat:
    ax.set_xlabel('Custom X Label')
```

---

### **Problem: Too many facets making plot unreadable**
```python
# 20+ subplots crammed together
```

**Solution:**
```python
# Use col_wrap to control layout
sns.relplot(..., col='category', col_wrap=4)  # 4 columns max

# Or filter to top categories
top_categories = df['category'].value_counts().head(8).index
df_filtered = df[df['category'].isin(top_categories)]
sns.relplot(data=df_filtered, ..., col='category')
```

---

## 🎨 Heatmap Issues

### **Problem: Heatmap values not showing**
```python
# Want to see numbers in heatmap cells
```

**Solution:**
```python
# Use annot=True
sns.heatmap(corr_matrix, annot=True)

# Customize annotation format
sns.heatmap(corr_matrix, annot=True, fmt='.2f')  # 2 decimal places
```

---

### **Problem: Heatmap colors not intuitive**
```python
# Colors don't match data meaning
```

**Solution:**
```python
# For correlations (-1 to 1), use diverging palette centered at 0
sns.heatmap(corr, cmap='RdBu_r', center=0, vmin=-1, vmax=1)

# For positive-only data, use sequential
sns.heatmap(data, cmap='Blues')
```

---

## 💡 Pro Tips

### **Debugging Workflow:**

1. **Print your data first**
   ```python
   print(df.head())
   print(df.dtypes)
   print(df.describe())
   ```

2. **Start simple, add complexity**
   ```python
   # Start basic
   sns.scatterplot(data=df, x='x', y='y')
   
   # Then add features one by one
   sns.scatterplot(data=df, x='x', y='y', hue='category')
   sns.scatterplot(data=df, x='x', y='y', hue='category', size='value')
   ```

3. **Check Seaborn version**
   ```python
   import seaborn as sns
   print(sns.__version__)
   
   # Upgrade if needed
   # pip install --upgrade seaborn
   ```

4. **Reset matplotlib settings**
   ```python
   import matplotlib.pyplot as plt
   plt.rcdefaults()  # Reset to defaults
   sns.set_theme()  # Reapply seaborn theme
   ```

---

## 📚 Additional Resources

- [Seaborn API Documentation](https://seaborn.pydata.org/api.html)
- [Seaborn FAQ](https://seaborn.pydata.org/faq.html)
- [Matplotlib Troubleshooting](https://matplotlib.org/stable/faq/index.html)
- [Stack Overflow: [seaborn] tag](https://stackoverflow.com/questions/tagged/seaborn)

---

**Still stuck?** Check GitHub Issues or Stack Overflow with the `[seaborn]` tag!
