# 🤝 Contributing to SeabornMasterPro

Thank you for your interest in contributing! Contributions that improve the package,
the notebooks, the documentation or the app are all welcome, from typo fixes to new
estimators.

---

## 📌 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Development Setup](#-development-setup)
- [Project Layout](#-project-layout)
- [Quality Gates](#-quality-gates)
- [Adding Things](#-adding-things)
- [Pull Request Process](#-pull-request-process)

---

## 📜 Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Please be respectful
and inclusive in all interactions.

---

## 🛠 Development Setup

```bash
git clone https://github.com/SatvikPraveen/SeabornMasterPro.git
cd SeabornMasterPro
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[all,dev]"
pre-commit install
```

Python 3.10 or newer is required. `pip install -e ".[dev]"` is enough for package work;
`[all]` adds JupyterLab, Streamlit and Excel export.

Or use Docker:

```bash
docker build -t seaborn-masterpro .
docker run -p 8888:8888 -p 8501:8501 seaborn-masterpro
```

---

## 🧱 Project Layout

| Path | What lives there |
|---|---|
| `seabornmasterpro/` | The typed package. One module per concern: `theme`, `io`, `stats`, `annotate`, `color`, `layout`, `repro`, `datasets`, `benchmark`. |
| `utils/plot_utils.py` | Backward-compatible facade for the notebooks. Do not add new code here; add it to the package and re-export. |
| `notebooks/` | The eleven-notebook curriculum. Notebook 11 is the research workflow. |
| `examples/` | Command-line scripts built on the package. |
| `datasets/` | Generated CSVs and `MANIFEST.json`. Never edit CSVs by hand; change the generator. |
| `tests/` | Unit, property-based, app and notebook tests. |
| `docs/` | Methodology, API reference, best practices, troubleshooting. |

---

## ✅ Quality Gates

Every pull request must pass the same checks CI runs:

```bash
ruff check . && ruff format --check .     # lint and formatting
mypy                                      # static types for the package
pytest                                    # unit + property tests (fast)
pytest -m notebooks                       # executes all notebooks (slow, optional locally)
python scripts/build_api_reference.py --check
```

Conventions:

- **Docstrings** use the numpydoc layout and state the estimator or reference where relevant.
- **Determinism**: anything random takes a `seed` or `rng` argument and uses `numpy.random.Generator`.
- **Types**: the package is `py.typed`; new public functions need full annotations.
- **Tests**: add a test for every new public function. Prefer property tests (Hypothesis) for
  mathematical invariants such as symmetry, scale invariance and bounds.
- **Figures** in notebooks are saved with `save_fig()` into the matching `exports/NN_*/` folder.

---

## ➕ Adding Things

**A new estimator or plot helper.** Implement it in the appropriate `seabornmasterpro` module,
export it in that module's `__all__`, add it to `seabornmasterpro/__init__.py` if it is commonly
used, write tests, document it in `docs/methodology.md` if it is statistical, and regenerate
`docs/api_reference.md`.

**A new dataset.** Add a generator function and a `DatasetCard` to `seabornmasterpro/datasets.py`
using an independent `numpy.random.default_rng(seed)` stream, then run `smp-datasets` to
regenerate the CSVs and the manifest. Legacy datasets must remain bit-for-bit identical; CI checks
this.

**A new notebook.** Follow `NN_topic_name.ipynb`, import from `seabornmasterpro` (with the
`sys.path` fallback used in notebook 11), and add a row to `docs/feature_matrix.md`. Notebooks are
executed in CI, so keep runtimes under a few minutes and avoid network access where possible.

**A new example script.** Give it an `argparse` CLI with `--output`, make it runnable with
`python -W error::FutureWarning`, and document it in `examples/README.md`.

---

## 🔁 Pull Request Process

1. Fork, then create a branch: `git checkout -b feat/short-description`.
2. Make focused changes with clear commit messages (`feat:`, `fix:`, `docs:`, `test:`, `ci:` …).
3. Run the quality gates above.
4. Update `CHANGELOG.md` under an *Unreleased* heading.
5. Open a pull request describing the change, linking issues with `Closes #123`, and attaching a
   figure if the output changed.

Thank you for helping make SeabornMasterPro better 💙

— [Satvik Praveen](https://github.com/SatvikPraveen)
