# 🎨 SeabornMasterPro

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-darkgreen.svg)](https://www.python.org/)
[![Jupyter Notebooks](https://img.shields.io/badge/Jupyter-Notebook-orange.svg)](https://jupyter.org/)
[![Seaborn Mastery](https://img.shields.io/badge/Seaborn-100%25-brightgreen.svg)](https://seaborn.pydata.org/)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-blueviolet.svg)](https://www.docker.com/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)](https://streamlit.io/)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-lightgrey.svg)](https://github.com/SatvikPraveen/SeabornMasterPro/pulls)
[![Last Commit](https://img.shields.io/github/last-commit/SatvikPraveen/SeabornMasterPro.svg)](https://github.com/SatvikPraveen/SeabornMasterPro/commits)

---

## 📌 Overview

**SeabornMasterPro** is an open-source, end-to-end visualization mastery project built to help you **learn, recall, and reuse** Seaborn effectively — from plotting basics to dashboard-level visual storytelling.

🎯 Ideal for:

- Learners who want structured notebooks and projects
- Practitioners who want reusable utilities and themes
- Professionals who need dashboards, cheatsheets, and reproducible setups

---

## 📽️ Project Preview

Here’s a glimpse into the Seaborn visualizations and dashboards created in this project:

### 🧭 Streamlit EDA Dashboard

> Powered by `streamlit_app.py`, this dashboard provides real-time interaction with synthetic datasets.

![Streamlit Dashboard Preview](exports/04_dashboards/campaign_facetgrid_scatter.png)

---

### 📊 Real-World Visual Storytelling

> Plots generated using `notebooks/05_realworld_EDA.ipynb` and reusable functions from `plot_utils.py`.

![E-Commerce EDA Preview](exports/05_eda/ecommerce_correlation_heatmap.png)

---

## 🧠 Learning Outcomes

By working through this project, you'll be able to:

- 📊 Visualize structured data with Seaborn’s full plotting suite
- 🧱 Build custom dashboards using Streamlit and save visual reports
- ♻️ Reuse plot components using `plot_utils.py`
- 📦 Package everything in a container-ready environment

---

## 🧱 Project Structure

```bash
SeabornMasterPro/
├── notebooks/               # Modular notebooks (merged logically)
│   ├── 01_setup_and_basics.ipynb
│   ├── 02_distributions_relationships.ipynb
│   ├── 03_categorical_matrixplots.ipynb
│   ├── 04_multi_custom_dashboards.ipynb
│   ├── 05_realworld_EDA.ipynb
│   └── 06_timeseries_lineplots.ipynb
├── utils/                   # Reusable helper functions
│   └── plot_utils.py        # Theme, save_fig, annotate, format_date_axis, etc.
├── scripts/                 # Dataset generators and helpers
│   └── generate_datasets.py
├── datasets/                # Synthetic datasets (auto-generated)
│   ├── ecommerce_data.csv
│   ├── employee_data.csv
│   ├── marketing_campaign.csv
│   ├── sales_data.csv
│   ├── student_scores.csv
│   └── web_traffic.csv
├── exports/                 # Saved visuals & reports
│   ├── 01_basics/
│   ├── 02_distributions/
│   ├── 03_categorical/
│   ├── 04_dashboards/
│   ├── 05_realworld/
│   └── 06_timeseries/
├── cheatsheets/             # Markdown cheatsheets
│   └── seaborn_cheatsheet.md
├── streamlit_app.py         # Interactive EDA dashboard
├── requirements.txt         # Project dependencies
├── Dockerfile               # Container setup
├── .dockerignore
├── .gitignore
├── README.md
└── LICENSE
```

---

## 🌟 Features

- 📘 **Modular notebooks** for each topic
- 📊 Full Seaborn coverage: `histplot`, `kdeplot`, `scatterplot`, `heatmap`, `pairplot`, `catplot`, `FacetGrid`, and more
- 🎨 Unified visual style via `plot_utils.py`
- 📁 Exports saved with `save_fig()` into logical folders
- 🗂️ Cheatsheet in Markdown for quick revision
- 🌐 Streamlit dashboard to explore visualizations interactively
- 🐳 Docker support for full reproducibility

---

## ✅ Mastery Checklist

- [x] Setup environment and install dependencies
- [x] Master Seaborn basics, distributions, relationships
- [x] Learn categorical & matrix visualizations
- [x] Build dashboards and multi-panel plots
- [x] Analyze real-world synthetic datasets
- [x] Use `.pipe()` and `plot_utils.py` for reusability
- [x] Run everything inside Docker or via Streamlit

---

## 🔧 Setup Instructions

### ▶️ Install Requirements

```bash
pip install -r requirements.txt
```

Or using Conda:

```bash
conda create -n seabornpro python=3.10
conda activate seabornpro
pip install -r requirements.txt
```

---

## 🐳 Run in Docker (JupyterLab)

```bash
docker build -t seaborn-masterpro .
docker run -p 8890:8888 -p 8501:8501 -v $(pwd):/app -d seaborn-masterpro
```

You can now open JupyterLab in your browser at:
🔗 [http://localhost:8890](http://localhost:8890)

> The container disables Jupyter token/password prompts for local ease.

---

## 📊 Launch Streamlit Dashboard

```bash
streamlit run streamlit_app.py
```

Then visit:
🔗 [http://localhost:8501](http://localhost:8501)

---

## 🔁 Extend This Repo

Want to take this further?

- [ ] Add Plotly/Altair interactive options
- [ ] Create animated visualizations
- [ ] Add unit tests for `plot_utils.py`
- [ ] Create `seaborn_themes.py` presets
- [ ] Integrate other dashboards into Streamlit

---

## 🧠 Learn by Doing

Each notebook is carefully structured with:

- ✅ Concepts grouped by theme
- ✅ Code + plots + comments inline
- ✅ Modular reusability via `plot_utils.py`
- ✅ Dataset links and exports
- ✅ Time-based, categorical, and real-world examples

---

## 📌 Topics Covered

- Setup and Seaborn basics
- Distributions and pairwise relationships
- Categorical plots and matrix visualizations
- Multi-panel layouts and custom dashboards
- Real-world EDA with Titanic & Marketing Campaign
- Time series line plots with date formatting

---

## 🎯 Who Is This For?

| Level           | Use Case                        |
| --------------- | ------------------------------- |
| ✅ Beginner     | Learn Seaborn from scratch      |
| ✅ Intermediate | Build reusable pipelines        |
| ✅ Advanced     | Automate dashboards with Docker |

---

## 🔗 Related Projects

- 🧠 [NumPyMasterPro](https://github.com/SatvikPraveen/NumPyMasterPro) — Deep dive into NumPy fundamentals
- 🐼 [PandasPlayground](https://github.com/SatvikPraveen/PandasPlayground) — Data cleaning and EDA workflows

---

## 📄 License

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0). See the [LICENSE](./LICENSE) file for more details.

---

## 🙌 Acknowledgements

- [Seaborn](https://seaborn.pydata.org/)
- [Matplotlib](https://matplotlib.org/)
- [Streamlit](https://streamlit.io/)
- [Python](https://www.python.org/)

---

## ✨ Author

Made with 💙 by [Satvik Praveen](https://github.com/SatvikPraveen)

---
