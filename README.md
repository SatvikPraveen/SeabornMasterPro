# 🎨 SeabornMasterPro

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-darkgreen.svg)](https://www.python.org/)
[![Jupyter Notebooks](https://img.shields.io/badge/Jupyter-Notebook-orange.svg)](https://jupyter.org/)
[![Seaborn Mastery](https://img.shields.io/badge/Seaborn-100%25-brightgreen.svg)](https://seaborn.pydata.org/)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-blueviolet.svg)](https://www.docker.com/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)](https://streamlit.io/)

---

## 📌 Overview

**SeabornMasterPro** is a comprehensive, concept-to-dashboard visualization project designed to help you **master Seaborn** — one of the most powerful Python libraries for statistical data visualization.

Whether you're a beginner aiming to learn Seaborn from scratch or a seasoned data scientist looking for a solid reference project, this repo has everything you need — **notebooks, cheatsheets, custom scripts, and even a Streamlit dashboard**.

---

## 📂 Project Structure

```bash
SeabornMasterPro/
├── notebooks/               # Modular notebooks (merged logically)
│   ├── 01_setup_and_basics.ipynb
│   ├── 02_distributions_relationships.ipynb
│   ├── 03_categorical_matrixplots.ipynb
│   ├── 04_multi_custom_dashboards.ipynb
│   ├── 05_realworld_EDA.ipynb
├── utils/                   # Utility functions (e.g., custom plots)
│   └── plot_utils.py
├── cheatsheets/             # Markdown + PDF visual guides
│   └── seaborn_cheatsheet.md
├── datasets/                # Titanic, Tips, Penguins, Custom CSV
│   ├── tips.csv
│   ├── titanic.csv
│   ├── penguins.csv
│   └── custom_kaggle_data.csv
├── exports/                 # Exported plots and PDFs
│   ├── plots/
│   └── reports/
├── streamlit_app.py         # Streamlit dashboard for EDA visualizations
├── requirements.txt         # Python packages
├── Dockerfile               # JupyterLab environment in a container
├── .dockerignore
├── .gitignore
├── README.md
└── LICENSE
```

---

## 🚀 Features

- ✅ Clean, concept-wise **Jupyter notebooks**
- ✅ Real + built-in **datasets** (Titanic, Tips, Penguins)
- ✅ Full coverage of Seaborn:

  - `histplot`, `kdeplot`, `scatterplot`, `boxplot`, `heatmap`, `pairplot`, etc.

- ✅ `plot_utils.py` for reusable styling & saving
- ✅ **Cheatsheets** for fast review
- ✅ `Streamlit` dashboard for interactive reports
- ✅ Docker support for easy reproducibility
- ✅ PDF exports and presentation-ready visuals

---

## 🧪 Requirements

- Python 3.10+
- Jupyter Notebook or JupyterLab
- Seaborn ≥ 0.12
- Pandas, NumPy, Matplotlib, Streamlit

Install everything at once:

```bash
pip install -r requirements.txt
```

Or, if using Conda:

```bash
conda create -n seabornpro python=3.10
conda activate seabornpro
pip install -r requirements.txt
```

---

## 🐳 Run via Docker

Build and launch the project in a container:

```bash
docker build -t seaborn-master-pro .
docker run -p 8888:8888 seaborn-master-pro
```

---

## 🌐 Launch Streamlit Dashboard

```bash
streamlit run streamlit_app.py
```

---

## 📘 Learn by Doing

Each notebook is written with:

- ✅ Step-by-step code
- ✅ Inline commentary
- ✅ Output screenshots
- ✅ Linked datasets
- ✅ Export options

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 📣 Author

Made with 💙 by [SatvikPraveen](https://github.com/SatvikPraveen)
