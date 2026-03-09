import streamlit as st
import os
from pathlib import Path
from PIL import Image

# 🧭 Setup
st.set_page_config(page_title="SeabornMasterPro Dashboard", layout="wide")
st.title("📊 SeabornMasterPro Visualization Explorer")
st.markdown("Easily navigate and view all exported plots from the project notebooks.")

# 📁 Map of folders (Notebook Sections)
NOTEBOOK_FOLDERS = {
    "📘 01 - Setup and Basics": "exports/01_setup",
    "📊 02 - Distributions & Relationships": "exports/02_distributions",
    "📦 03 - Categorical & Matrix Plots": "exports/03_categorical",
    "📐 04 - Dashboards & Facets": "exports/04_dashboards",
    "🧪 05 - Real-World EDA": "exports/05_eda",
    "📈 06 - Time Series & Advanced Lineplots": "exports/06_timeseries",
    "🎯 07 - Figure-Level Functions": "exports/07_figure_level",
    "📊 08 - Advanced Categorical Plots": "exports/08_categorical",
    "🎨 09 - Styling & Customization": "exports/09_styling",
    "📐 10 - Statistical Parameters": "exports/10_statistical"
}

# 📂 Sidebar Navigation
selected_section = st.sidebar.selectbox("📂 Select Notebook Section", list(NOTEBOOK_FOLDERS.keys()))

# 🖼 Load images from the selected folder
image_dir = Path(NOTEBOOK_FOLDERS[selected_section])

if not image_dir.exists():
    st.warning("This section has no exported plots yet.")
else:
    image_files = sorted(image_dir.glob("*.png"))

    if not image_files:
        st.info("No plots found in this section yet.")
    else:
        for img_path in image_files:
            st.subheader(img_path.stem.replace("_", " ").title())
            img = Image.open(img_path)
            st.image(img, use_container_width=True)
