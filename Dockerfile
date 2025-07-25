# 🐍 Base image
FROM python:3.10-slim

# 🛠 Set working directory
WORKDIR /app

# 📄 Copy requirements and install Python deps first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ⚙️ Install system packages for matplotlib/seaborn
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 📦 Copy all files into container
COPY . .

# 📤 Expose ports for Jupyter and Streamlit (if needed later)
EXPOSE 8888
EXPOSE 8501

# ✅ Disable token and password (safe for local/dev use)
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--allow-root", "--no-browser", "--NotebookApp.token=", "--NotebookApp.password="]
