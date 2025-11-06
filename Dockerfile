# Dockerfile pour FL Crew Reddit - Federated Learning avec LLMs
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Variables d'environnement
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    curl \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Créer un lien symbolique pour python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Installer AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY fl_crew_reddit/requirements.txt /app/fl_crew_reddit/requirements.txt
COPY reddit_server/requirements.txt /app/reddit_server/requirements.txt
COPY linkedin_server/requirements.txt /app/linkedin_server/requirements.txt

# Installer les dépendances Python
RUN pip3 install --upgrade pip setuptools wheel && \
    pip3 install -r fl_crew_reddit/requirements.txt && \
    pip3 install -r reddit_server/requirements.txt && \
    pip3 install boto3 awscli

# Copier tout le code de l'application
COPY . /app

# Créer les répertoires nécessaires
RUN mkdir -p /app/fl_crew_reddit/data \
    /app/fl_crew_reddit/models \
    /app/fl_crew_reddit/logs \
    /app/fl_crew_reddit/results \
    /app/data/reddit_data \
    /app/data/linkedin_data

# Variables d'environnement par défaut
ENV FL_CREW_REDDIT_DIR=/app/fl_crew_reddit
ENV AWS_DEFAULT_REGION=us-east-1

# Exposer le port pour les services (si nécessaire)
EXPOSE 8000

# Commande par défaut
CMD ["python", "-m", "fl_crew_reddit.main"]

