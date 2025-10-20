#!/bin/bash

# Variables d'environnement Reddit
export REDDIT_CLIENT_ID="iBl_tHzeyvDnZLSrGvbQpg"
export REDDIT_CLIENT_SECRET="4BVduORPc2IJtO6T9_zXmPMmjoKW0A"
export REDDIT_USER_AGENT="MCP Reddit Server v1.0"
export REDDIT_DATA_DIR="./data/reddit_data"

# Lancer le serveur
cd /mnt/c/Users/saifa/version_finala_maha_project/reddit_server
source venv/bin/activate
python server.py