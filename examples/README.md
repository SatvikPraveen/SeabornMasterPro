# 🐍 Production-Ready Python Examples

This directory contains **production-ready Python scripts** that demonstrate how to use Seaborn in real-world applications. Unlike the notebooks (which are for interactive learning), these scripts are designed for production use with proper error handling, logging, and command-line interfaces.

---

## 📋 Available Scripts

### 1. **basic_workflow.py** - Complete Visualization Workflow
Entry-level script showing a complete data visualization workflow from loading data to saving plots.

**Features:**
- Data loading and validation
- Multiple plot types (distribution, scatter, categorical, heatmap)
- Command-line arguments
- Organized output management

**Usage:**
```bash
# Use default sales data
python basic_workflow.py

# Specify custom dataset
python basic_workflow.py --dataset employee_data

# Custom output directory
python basic_workflow.py --output ./my_plots
```

**Best for:** Getting started, learning the workflow

---

### 2. **production_dashboard.py** - Multi-Panel Dashboards
Creates comprehensive dashboards with multiple plots, KPIs, and metadata suitable for reports and presentations.

**Features:**
- Multi-panel layouts with GridSpec
- KPI summary panels
- Multiple dataset support (e-commerce, generic)
- Export to multiple formats (PNG, PDF, SVG)
- Timestamp and metadata tracking

**Usage:**
```bash
# Create e-commerce dashboard
python production_dashboard.py

# Export as PDF
python production_dashboard.py --format pdf

# Multiple formats
python production_dashboard.py --format png pdf svg

# Different dataset
python production_dashboard.py --dataset sales_data
```

**Best for:** Business reports, stakeholder presentations

---

### 3. **custom_styling.py** - Advanced Styling & Themes
Demonstrates comprehensive styling options including custom palettes, themes, and color theory.

**Features:**
- Theme comparisons (all 5 Seaborn themes)
- Color palette types (sequential, diverging, qualitative)
- Custom brand colors
- Colorblind-safe palettes
- Context scaling (paper, notebook, talk, poster)
- Gradient palettes

**Usage:**
```bash
# Create all styling examples
python custom_styling.py

#Show available palettes
python custom_styling.py --show-palettes

# Custom output
python custom_styling.py --output ./style_examples
```

**Best for:** Brand consistency, accessibility, presentations

---

### 4. **statistical_viz.py** - Statistical Analysis
Shows statistical visualization with confidence intervals, error bars, and significance testing.

**Features:**
- Estimator comparisons (mean, median, sum)
- Error bar types (CI, SD, SE)
- Bootstrap confidence intervals
- Regression with confidence bands
- Statistical significance annotations
- Custom estimator functions

**Usage:**
```bash
# Default 95% confidence interval
python statistical_viz.py

# 99% confidence interval
python statistical_viz.py --ci 99

# Custom bootstrap iterations
python statistical_viz.py --n-bootstrap 5000

# More samples per category
python statistical_viz.py --n-samples 200
```

**Best for:** Research, academic papers, statistical analysis

---

### 5. **batch_processing.py** - Process Multiple Datasets
Efficiently processes multiple datasets in batch with consistent visualizations.

**Features:**
- Automatic dataset discovery
- Batch processing (sequential or parallel)
- Automatic plot generation per dataset
- Master comparison report
- Summary statistics export
- JSON/CSV export

**Usage:**
```bash
# Process all CSV files
python batch_processing.py

# Process specific pattern
python batch_processing.py --pattern "sales*.csv"

# Only specific plot types
python batch_processing.py --plots distribution correlation

# Parallel processing (faster for many datasets)
python batch_processing.py --parallel

# Custom directories
python batch_processing.py --data-dir ./my_data --output ./batch_results
```

**Best for:** Large-scale analysis, multiple datasets, automation

---

### 6. **publication_figures.py** - Journal-Quality Figures
Creates publication-ready figures with proper sizing, DPI, and formatting for journals, conferences, and posters.

**Features:**
- Journal size presets (Nature, Science, single/double column)
- Presentation formats (4:3, 16:9)
- Poster sizes
- High DPI output (300, 600, 1200)
- Multiple format export (PNG, PDF, SVG, EPS)
- Font size presets
- Grayscale-friendly options

**Usage:**
```bash
# Journal double-column, 300 DPI
python publication_figures.py

# Nature single column
python publication_figures.py --size nature

# High resolution poster
python publication_figures.py --size poster --dpi 600

# Multiple formats
python publication_figures.py --formats pdf svg eps

# Show all size presets
python publication_figures.py --show-sizes

# Presentation format
python publication_figures.py --size presentation_wide --font presentation
```

**Size Presets:**
- `journal_single` - 3.5" × 2.625" (single column)
- `journal_double` - 7.0" × 5.25" (double column)
- `nature` - 89mm × 89mm (Nature journal)
- `science` - 55mm × 55mm (Science journal)
- `presentation` - 10" × 7.5" (4:3 aspect)
- `presentation_wide` - 12" × 6.75" (16:9 aspect)
- `poster` - 16" × 12" (large format)

**Best for:** Academic papers, journal submissions, conferences

---

### 7. **reusable_template.py** - Production Template
A complete template for creating your own visualization scripts with proper structure, error handling, and logging.

**Features:**
- Object-oriented design
- Comprehensive error handling
- Logging configuration
- Input validation
- Multiple plot types
- Data export functionality
- Command-line interface

**Usage:**
```bash
# Scatter plot
python reusable_template.py --data my_data.csv --scatter --x col1 --y col2

# Distribution plot
python reusable_template.py --data my_data.csv --dist Price

# Categorical plot
python reusable_template.py --data my_data.csv --cat Category Revenue

# Correlation heatmap
python reusable_template.py --data my_data.csv --heatmap

# With styling
python reusable_template.py --data my_data.csv --scatter --x col1 --y col2 --hue category --style dark --palette Set2

# Multiple plots
python reusable_template.py --data my_data.csv --scatter --x col1 --y col2 --dist col1 --heatmap
```

**Best for:** Starting new projects, production deployments

---

## 🚀 Quick Start

### Prerequisites
```bash
# Ensure you're in the project virtual environment
source ../venv/bin/activate  # On macOS/Linux
# or
..\venv\Scripts\activate  # On Windows

# All dependencies should already be installed
```

### Run Your First Example
```bash
# Navigate to examples directory
cd examples

# Run basic workflow
python basic_workflow.py

# Check the output
ls ../exports/examples/
```

---

## 📊 Comparison: Scripts vs Notebooks

| Feature | Notebooks | Scripts |
|---------|-----------|---------|
| **Purpose** | Interactive learning | Production execution |
| **Execution** | Cell-by-cell | Complete run |
| **Error Handling** | Limited | Comprehensive |
| **Logging** | Print statements | Structured logging |
| **CLI Arguments** | ❌ | ✅ |
| **Automation** | Difficult | Easy (cron, CI/CD) |
| **Version Control** | Harder to diff | Easy to diff |
| **Reusability** | Copy cells | Import modules |
| **Documentation** | Markdown cells | Docstrings |
| **Testing** | Manual | Automated possible |

---

## 🎯 When to Use Each Script

### For Learning & Exploration
→ Use **notebooks** in `/notebooks/` directory

### For Quick Analysis
→ Use **basic_workflow.py**

### For Business Reports
→ Use **production_dashboard.py**

### For Brand Consistency
→ Use **custom_styling.py**

### For Research/Academia
→ Use **statistical_viz.py** and **publication_figures.py**

### For Automation
→ Use **batch_processing.py**

### For New Projects
→ Copy and modify **reusable_template.py**

---

## 🛠️ Common Patterns

### Pattern 1: Batch Processing
```bash
# Process all datasets and create standardized reports
python batch_processing.py --parallel --plots all
```

### Pattern 2: Publication Workflow
```bash
# Create journal-ready figures
python publication_figures.py --size journal_double --dpi 300 --formats pdf svg
```

### Pattern 3: Custom Analysis
```bash
# Start from template
cp reusable_template.py my_analysis.py

# Edit my_analysis.py with your specific logic
# Run it
python my_analysis.py --data my_data.csv --scatter --x feature1 --y feature2
```

### Pattern 4: Automated Reporting
```bash
# Schedule with cron (Linux/macOS)
# Add to crontab: 0 9 * * 1 cd /path/to/project && python examples/production_dashboard.py

# Or Windows Task Scheduler
```

---

## 💡 Pro Tips

1. **Use virtual environment**: Always activate `venv` before running
2. **Check help**: All scripts have `--help` for full options
3. **Test with samples**: Use provided datasets in `/datasets/` first
4. **Chain operations**: Use shell pipes and redirects
5. **Version control**: Scripts are git-friendly (unlike notebooks)
6. **Import utilities**: All scripts use `/utils/plot_utils.py`
7. **Logging**: Check console output for debugging info
8. **Error handling**: Scripts validate inputs before processing

---

## 📁 Output Structure

Scripts create organized output directories:

```
exports/
├── examples/              # basic_workflow.py
├── batch_processing/      # batch_processing.py
│   ├── dataset1/
│   │   ├── distributions.png
│   │   ├── correlation.png
│   │   └── summary.json
│   ├── dataset2/
│   └── master_report.png
└── publication/           # publication_figures.py
    ├── scatter_plot_journal_double.pdf
    ├── multiplot_journal_double.pdf
    └── ...
```

---

## 🔧 Customization

### Modify Existing Scripts
```python
# Example: Change default theme in any script
apply_theme(style="dark", palette="colorblind")

# Example: Add custom plot type
def create_my_custom_plot(data, output_dir):
    # Your custom logic here
    pass
```

### Create New Scripts
```bash
# Copy template
cp reusable_template.py my_new_script.py

# Modify for your needs
# Add to git
git add my_new_script.py
```

---

## 🐛 Troubleshooting

### Import Errors
```bash
# Ensure you're in virtual environment
which python  # Should show path to venv/bin/python

# Ensure utils is in path (scripts handle this automatically)
```

### Missing Data
```bash
# Check datasets exist
ls ../datasets/

# Generate datasets if needed
python ../scripts/generate_datasets.py
```

### Permission Errors
```bash
# Make scripts executable (Linux/macOS)
chmod +x *.py
```

---

## 📚 Additional Resources

- **Notebooks**: `/notebooks/` - Interactive learning
- **Utilities**: `/utils/plot_utils.py` - Reusable functions
- **Documentation**: `/docs/` - Best practices, guides
- **Tests**: `/tests/` - Unit tests for utilities

---

## 🤝 Contributing

To add a new example script:

1. Follow the existing structure
2. Include docstrings and help text
3. Add command-line arguments
4. Include error handling
5. Update this README
6. Test with sample data

---

## 📄 License

Same as main project (MIT License)

---

**Need help?** Check the main [README.md](../README.md) or open an issue on GitHub.
