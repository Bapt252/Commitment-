FROM jupyter/scipy-notebook:latest

USER root

# Installation des outils système
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

USER $NB_UID

# Installation des packages Python pour ML/AI
RUN pip install --no-cache-dir \
    fastapi \
    pandas \
    numpy \
    scikit-learn \
    matplotlib \
    seaborn \
    plotly \
    jupyterlab-git \
    black \
    flake8 \
    pytest \
    openai \
    redis \
    psycopg2-binary \
    mlflow \
    prometheus-client \
    structlog \
    requests \
    httpx \
    asyncio \
    aiofiles

# Extensions JupyterLab
RUN jupyter labextension install \
    @jupyter-widgets/jupyterlab-manager \
    @jupyterlab/git

# Configuration JupyterLab
RUN jupyter lab build

# Création des répertoires de travail
RUN mkdir -p /home/jovyan/work/{notebooks,data,scripts,experiments}

WORKDIR /home/jovyan/work

# Configuration par défaut
CMD ["start-notebook.sh", "--NotebookApp.token='development'", "--NotebookApp.password=''"]