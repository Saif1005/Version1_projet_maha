#!/bin/bash
# run_linkedin_server.sh — version corrigée pour WSL + Claude

set -e
cd /mnt/c/Users/saifa/version_finala_maha_project

# --- Active le bon environnement virtuel ---
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
  source .venv/Scripts/activate
else
  echo "[MCP] Création d'un nouvel environnement virtuel..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install mcp flask
fi

echo "============================================================"
echo " MCP SERVER LINKEDIN — démarrage pour Claude Desktop"
echo "============================================================"

# --- Démarre le serveur MCP ---
python3 /mnt/c/Users/saifa/version_finala_maha_project/linkedin_server/server.py
