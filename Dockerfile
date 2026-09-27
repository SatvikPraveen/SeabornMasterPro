# syntax=docker/dockerfile:1
# Reproducible environment for the SeabornMasterPro curriculum, package and app.
#
#   docker build -t seaborn-masterpro .
#   docker run -p 8888:8888 -p 8501:8501 seaborn-masterpro                # JupyterLab
#   docker run -p 8501:8501 seaborn-masterpro streamlit run streamlit_app.py --server.address 0.0.0.0
#   docker run seaborn-masterpro pytest -q                                  # test suite

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MPLBACKEND=Agg \
    PYTHONHASHSEED=0

WORKDIR /app

# Fonts give matplotlib a sans-serif family for the journal presets; git lets
# provenance records capture the revision when the repo is mounted.
RUN apt-get update && apt-get install -y --no-install-recommends \
        fonts-dejavu-core fonts-liberation git \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first so source edits do not invalidate the layer.
COPY pyproject.toml README.md LICENSE ./
COPY seabornmasterpro ./seabornmasterpro
COPY utils ./utils
RUN pip install --upgrade pip && pip install -e ".[all,dev]"

COPY . .

# Non-root user for JupyterLab / Streamlit.
RUN useradd --create-home --uid 1000 smp && chown -R smp:smp /app
USER smp

EXPOSE 8888 8501

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import seabornmasterpro" || exit 1

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", \
     "--ServerApp.token=", "--ServerApp.password="]
