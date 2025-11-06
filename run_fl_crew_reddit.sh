#!/bin/bash

# Script pour lancer le FL Crew Reddit
# Fichier: run_fl_crew_reddit.sh

echo "=========================================="
echo " Lancement du FL Crew Reddit"
echo "=========================================="
echo ""

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo " Python 3 n'est pas installé"
    exit 1
fi

# Activer l'environnement virtuel si disponible
if [ -d "venv" ]; then
    echo " Activation de l'environnement virtuel..."
    source venv/bin/activate
fi

# Installer les dépendances si nécessaire
if [ ! -d "fl_crew_reddit" ]; then
    echo " Le dossier fl_crew_reddit n'existe pas"
    exit 1
fi

echo "🔧 Vérification des dépendances..."
pip install -q -r fl_crew_reddit/requirements.txt 2>/dev/null || {
    echo "  Certaines dépendances peuvent manquer"
}

# Lancer le FL Crew
echo ""
echo " Démarrage du FL Crew Reddit..."
echo ""

python3 -m fl_crew_reddit.main

echo ""
echo "=========================================="
echo " FL Crew Reddit terminé"
echo "=========================================="

