# Production-Ready Python Examples

This directory contains **command-line scripts** that show how to use the
`seabornmasterpro` package in real-world applications. Unlike the notebooks
(which are for interactive learning), these scripts are designed for automation:
argparse interfaces, deterministic seeding, structured logging and exports with
embedded provenance.

Every script imports directly from the package:

```python
from seabornmasterpro import apply_theme, save_fig, set_seed
from seabornmasterpro.theme import JOURNALS, figsize_for, journal_context
from seabornmasterpro.stats import compare_groups, group_summary
from seabornmasterpro.annotate import annotate_pairwise
from seabornmasterpro.color import validate_palette, cvd_palette_grid
from seabornmasterpro.repro import write_manifest
```

Each script inserts the repository root into `sys.path` before importing, so
they also run from a plain checkout without `pip install -e .`.

---

## Quick start

```bash
# From the repository root
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[all]"

python examples/basic_workflow.py
ls exports/examples/
```

All scripts accept `--output DIR` and `--help`. Default output locations are
listed in [Output structure](#output-structure).

---

## Available scripts

### 1. `basic_workflow.py` - complete visualization workflow

Loads a CSV from `datasets/`, draws a distribution, a scatter, a bar chart with a
95% bootstrap CI and a correlation heatmap, and saves each PNG with provenance
metadata via `save_fig`.

| Flag | Default | Description |
|------|---------|-------------|
| `--dataset NAME` | `sales_data` | Dataset in `datasets/` (without `.csv`) |
| `--output DIR` | `exports/examples` | Output directory |
| `--seed N` | `0` | Seed for bootstrap error bars |

```bash
python examples/basic_workflow.py
python examples/basic_workflow.py --dataset employee_data --output ./my_plots
```

---

### 2. `production_dashboard.py` - multi-panel dashboards

GridSpec dashboard with a KPI panel and linked charts. Exports through
`io.save_publication_figure`, which embeds the environment, package versions and
git revision in the PNG/PDF/SVG metadata; the same record is written to
`<name>.provenance.json`.

| Flag | Default | Description |
|------|---------|-------------|
| `--dataset NAME` | `ecommerce_data` | Dataset (any name containing `ecommerce` gets the e-commerce layout, others a generic one) |
| `--output DIR` | `exports/examples` | Output directory |
| `--format FMT [FMT ...]` | `png` | `png`, `pdf`, `svg` |
| `--dpi N` | `300` | Raster resolution |
| `--title TEXT` | venue default | Override the dashboard title |
| `--seed N` | `0` | Seed for bootstrap error bars |

```bash
python examples/production_dashboard.py
python examples/production_dashboard.py --format png pdf svg
python examples/production_dashboard.py --dataset sales_data --dpi 200
```

---

### 3. `custom_styling.py` - styling, themes and CVD accessibility

Axes styles, plotting contexts, sequential/diverging/qualitative palettes,
brand colours, explicit colour mappings and gradient colormaps. It finishes with
an accessibility check: `color.validate_palette` reports the minimum CIELAB
distance between colours in normal vision and under simulated protanopia,
deuteranopia and tritanopia, and `color.cvd_palette_grid` renders each palette
as those viewers see it (`cvd_simulation.png`, `palette_accessibility.json`).

| Flag | Default | Description |
|------|---------|-------------|
| `--output DIR` | `exports/examples` | Output directory |
| `--show-palettes` | | Print palette information and exit |
| `--check NAME [NAME ...]` | | Extra Seaborn palettes to include in the CVD check |
| `--threshold X` | `10` | Minimum acceptable ΔE between colours |

```bash
python examples/custom_styling.py
python examples/custom_styling.py --check Set1 husl tab10
python examples/custom_styling.py --show-palettes
```

---

### 4. `statistical_viz.py` - confidence intervals and pairwise tests

Estimator and error-bar comparisons, bootstrap sampling distributions
(`stats.bootstrap_ci`), per-group means with bootstrap CIs
(`stats.group_summary`), regression with confidence bands, and pairwise group
comparisons with multiplicity correction and effect sizes
(`stats.compare_groups`) drawn as stacked significance brackets
(`annotate.annotate_pairwise`). Test results are exported to
`pairwise_tests.csv` and `group_summary.csv`.

| Flag | Default | Description |
|------|---------|-------------|
| `--output DIR` | `exports/examples` | Output directory |
| `--ci {68,90,95,99}` | `95` | Confidence level |
| `--n-bootstrap N` | `1000` | Bootstrap resamples |
| `--n-samples N` | `100` | Observations per group |
| `--test {welch,student,mannwhitney,permutation}` | `welch` | Pairwise test |
| `--correction {none,bonferroni,holm,fdr_bh}` | `holm` | Multiple-comparison correction |
| `--seed N` | `42` | Random seed |

```bash
python examples/statistical_viz.py
python examples/statistical_viz.py --ci 99 --n-bootstrap 5000
python examples/statistical_viz.py --test mannwhitney --correction fdr_bh
```

---

### 5. `batch_processing.py` - process many datasets

Discovers CSVs, produces distribution / correlation / categorical figures and a
`summary.json` per dataset, a cross-dataset master report, and a `MANIFEST.json`
with the SHA-256 of every output (`repro.write_manifest`). Verify later with
`seabornmasterpro.repro.verify_manifest`.

| Flag | Default | Description |
|------|---------|-------------|
| `--data-dir DIR` | `datasets/` | Directory to scan |
| `--output DIR` | `exports/batch_processing` | Output directory |
| `--pattern GLOB` | `*.csv` | File pattern |
| `--plots {all,distribution,correlation,category} ...` | `all` | Plot types |
| `--parallel` | | Use a process pool |
| `--seed N` | `0` | Seed for bootstrap error bars |

```bash
python examples/batch_processing.py
python examples/batch_processing.py --pattern "s*.csv" --plots distribution correlation
python examples/batch_processing.py --parallel --output ./batch_results
```

---

### 6. `publication_figures.py` - journal-quality figures

Size presets are derived from `theme.JOURNALS` (Nature, Science, IEEE,
Elsevier, PLOS, ACM, presentation, poster); figures are drawn inside
`theme.journal_context` with `theme.figsize_for`, panels are labelled with
`layout.label_panels`, and exports go through `io.save_publication_figure`
(PDF/SVG keep editable text).

| Flag | Default | Description |
|------|---------|-------------|
| `--output DIR` | `exports/publication` | Output directory |
| `--size PRESET` | `journal_double` | `<venue>_single` / `<venue>_double` for each venue, `presentation`, `poster`, plus legacy aliases `journal_single`, `journal_double`, `presentation_wide`, `nature`, `science` |
| `--font {auto,journal,presentation,poster}` | `auto` | Typography override (`auto` uses the venue's fonts) |
| `--dpi {150,300,600,1200}` | `300` | Raster resolution |
| `--formats FMT ...` | `png pdf` | `png`, `pdf`, `svg`, `eps` |
| `--show-sizes` | | Print every preset and render a demo figure for each |
| `--seed N` | `0` | Seed for bootstrap error bars |

```bash
python examples/publication_figures.py
python examples/publication_figures.py --size nature_single --dpi 600 --formats pdf svg
python examples/publication_figures.py --show-sizes
```

---

### 7. `reusable_template.py` - production template

A pipeline class to copy for new projects: input validation, structured logging,
deterministic seeding and multi-format export with provenance.

| Flag | Default | Description |
|------|---------|-------------|
| `--data FILE` | required | CSV / Excel / JSON / Parquet input |
| `--output DIR` | `./output` | Output directory |
| `--scatter` + `--x COL --y COL [--hue COL]` | | Scatter plot |
| `--dist COL` | | Distribution plot |
| `--cat X Y` + `--kind {bar,box,violin,point}` | `bar` | Categorical plot |
| `--heatmap` | | Correlation heatmap |
| `--style`, `--palette` | `whitegrid`, `deep` | Theme |
| `--formats FMT ...`, `--dpi N` | `png`, `300` | Export settings |
| `--seed N` | `0` | Random seed |

```bash
python examples/reusable_template.py --data datasets/sales_data.csv \
    --scatter --x "Units Sold" --y "Total Sales" --hue Region
python examples/reusable_template.py --data datasets/sales_data.csv \
    --dist "Total Sales" --cat Product "Total Sales" --kind box --heatmap --formats png pdf
```

---

## Output structure

```
exports/
├── examples/              # basic_workflow, custom_styling, production_dashboard, statistical_viz
│   ├── total_sales_distribution.png
│   ├── cvd_simulation.png
│   ├── ecommerce_data_dashboard.png (+ .provenance.json)
│   ├── statistical_annotations.png, pairwise_tests.csv
│   └── ...
├── batch_processing/      # batch_processing
│   ├── <dataset>/{distributions,correlation,categories}.png + summary.json
│   ├── master_report.png, batch_summary.csv
│   └── MANIFEST.json
└── publication/           # publication_figures
    ├── scatter_plot_journal_double.{png,pdf}
    └── ...
output/                    # reusable_template (default, relative to the cwd)
```

Every PNG/PDF/SVG written by these scripts carries a provenance record
(timestamp, Python and package versions, platform, git revision) in its
metadata; read it back with e.g. `PIL.Image.open(path).info["Provenance"]`.

---

## Scripts vs notebooks

| Feature | Notebooks | Scripts |
|---------|-----------|---------|
| Purpose | Interactive learning | Production execution |
| CLI arguments | no | yes |
| Automation (cron, CI) | difficult | easy |
| Reproducibility | manual | seeded, provenance embedded, manifests |
| Version control | hard to diff | easy to diff |

---

## Customization

```python
# Change the theme in any script
apply_theme(style="dark", palette="colorblind")

# Start a new script from the template
cp examples/reusable_template.py my_analysis.py
```

---

## Troubleshooting

- **Import errors** - run `pip install -e ".[all]"` from the repository root, or
  run the scripts from a checkout (they add the repository root to `sys.path`).
- **Missing datasets** - regenerate them with `smp-datasets` (or
  `python -m seabornmasterpro.datasets`); `datasets/MANIFEST.json` lists the
  expected SHA-256 digests.
- **Font warnings** - journal presets prefer Arial/Helvetica/Times; matplotlib
  falls back to DejaVu when they are not installed.

---

## Additional resources

- `notebooks/` - interactive curriculum
- `seabornmasterpro/` - the package (`theme`, `io`, `stats`, `annotate`, `color`, `layout`, `repro`, `datasets`, `benchmark`)
- `utils/plot_utils.py` - backward-compatible facade for older notebooks
- `docs/` - guides and best practices
- `tests/` - unit tests

---

## License

Same as the main project: GPL-3.0-or-later.
