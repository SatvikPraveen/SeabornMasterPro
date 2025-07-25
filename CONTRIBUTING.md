# 🤝 Contributing to SeabornMasterPro

Thank you for your interest in contributing to **SeabornMasterPro**! 🎨📊  
We welcome contributions that improve documentation, add new notebooks, suggest utilities, enhance the Streamlit dashboard, or fix bugs.

Whether you're a beginner or a seasoned data scientist — there’s a place for you here.

---

## 📌 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [How to Contribute](#-how-to-contribute)
- [Ideas to Get Started](#-ideas-to-get-started)
- [Style Guidelines](#-style-guidelines)
- [Pull Request Process](#-pull-request-process)
- [Project Setup](#-project-setup)

---

## 📜 Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/) Code of Conduct.  
Please be respectful and inclusive in all your interactions.

---

## 🚀 How to Contribute

1. **Fork the repo**
2. **Clone your fork**
   ```bash
   git clone https://github.com/SatvikPraveen/SeabornMasterPro.git
   ```

3. **Create a branch**

   ```bash
   git checkout -b your-feature-branch
   ```
4. **Make your changes** (edit notebooks, utilities, datasets, etc.)
5. **Commit and push**

   ```bash
   git add .
   git commit -m "Add: meaningful commit message"
   git push origin your-feature-branch
   ```
6. **Open a Pull Request (PR)** — explain your changes clearly.

---

## 💡 Ideas to Get Started

* 📘 Improve or add new **tutorial notebooks**
* 🧪 Add test datasets or **new dataset generators** to `/scripts`
* 🎨 Propose new reusable functions in `plot_utils.py`
* 🌐 Enhance the **Streamlit dashboard**
* 📝 Fix typos or improve formatting in README/cheatsheets
* 🐞 Report or fix bugs in visual output or exports

---

## 🎯 Style Guidelines

* Use consistent naming: `XX_topicname.ipynb`
* Add comments & markdown cells in notebooks
* Prefer `.pipe()` and modular functions when possible
* Save plots using `save_fig()` and export to the appropriate `/exports/` folder
* Keep utilities clean, documented, and reusable
* Follow PEP8 for `.py` files

---

## 📦 Project Setup

Install requirements:

```bash
pip install -r requirements.txt
```

Or use Conda:

```bash
conda create -n seabornpro python=3.10
conda activate seabornpro
pip install -r requirements.txt
```

Run in Docker:

```bash
docker build -t seaborn-masterpro .
docker run -p 8890:8888 -v $(pwd):/app -d seaborn-masterpro
```

---

## ✅ Pull Request Process

* Keep PRs **focused and minimal**
* Mention related issues using `Closes #issue_number` if applicable
* Ensure that the project still runs (check notebook outputs or Streamlit)
* Add relevant screenshots, exports, or samples if helpful

---

Thank you again for helping improve **SeabornMasterPro** 💙
Let’s build beautiful, shareable, and professional plots together!

— [Satvik Praveen](https://github.com/SatvikPraveen)
