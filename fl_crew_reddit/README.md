# FL Crew Reddit - Système de Federated Learning avec LLMs

Système de Federated Learning avec 5 agents spécialisés pour l'analyse de données Reddit multimodales (texte, images, vidéos) utilisant des modèles LLM avec fine-tuning LoRA/QLoRA.

## Architecture

Le FL Crew Reddit est composé de 5 agents spécialisés :

1. **Data Collector Agent** : Collecte les données multimodales depuis le MCP Server Reddit
2. **Data Preprocessor Agent** : Prépare et nettoie les données multimodales (texte, images, vidéos) pour l'entraînement LLM
3. **Model Trainer Agents** (3 agents) : Entraînent des modèles LLM locaux avec fine-tuning LoRA sur leurs données assignées
4. **Aggregator Agent** : Agrège les modèles LLM locaux (poids LoRA) en un modèle global (Federated Averaging)
5. **Evaluator Agent** : Évalue les performances des modèles LLM avec métriques adaptées (perplexity, BLEU, ROUGE, etc.)

## Installation

```bash
# Installer les dépendances
pip install -r fl_crew_reddit/requirements.txt

# Note: bitsandbytes nécessite CUDA pour la quantization (QLoRA)
# Pour CPU uniquement, commentez bitsandbytes dans requirements.txt

# Configurer les variables d'environnement
# Créer un fichier .env avec:
# - OPENAI_API_KEY (pour orchestration des agents)
# - AGENT_LLM_MODEL=gpt-4 (pour orchestration)
# - BASE_LLM_MODEL=mistralai/Mistral-7B-v0.1 (modèle de base pour FL)
# - REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET (pour MCP Server Reddit)
```

## Configuration

Les paramètres peuvent être configurés dans `fl_crew_reddit/config.py` ou via des variables d'environnement :

### Configuration LLM pour Federated Learning
- `BASE_LLM_MODEL` : Modèle de base LLM pour le fine-tuning (défaut: "mistralai/Mistral-7B-v0.1")
- `USE_LORA` : Utiliser LoRA pour le fine-tuning (défaut: true)
- `LORA_R` : Rang LoRA (défaut: 8)
- `LORA_ALPHA` : Alpha LoRA (défaut: 16)
- `USE_QUANTIZATION` : Utiliser QLoRA avec quantization (défaut: false)
- `QUANTIZATION_BITS` : Bits de quantization (défaut: 4)

### Configuration Federated Learning
- `FEDERATION_ROUNDS` : Nombre de rounds de fédération (défaut: 10)
- `LOCAL_EPOCHS` : Nombre d'époques d'entraînement local (défaut: 3)
- `BATCH_SIZE` : Taille de batch (défaut: 4, adapté pour LLMs)
- `LEARNING_RATE` : Taux d'apprentissage (défaut: 2e-4, adapté pour fine-tuning LLM)
- `AGGREGATION_METHOD` : Méthode d'agrégation (weighted_average, fedavg, fedprox)

### Configuration Données Multimodales
- `SUPPORT_MULTIMODAL` : Activer le support multimodale (défaut: true)
- `IMAGE_PROCESSOR` : Processeur d'images (défaut: "clip-vit-base-patch32")
- `MAX_IMAGE_SIZE` : Taille maximale des images (défaut: 224)

### Configuration Agents
- `AGENT_LLM_MODEL` : Modèle LLM pour orchestration (défaut: gpt-4)
- `FL_CREW_REDDIT_DIR` : Répertoire de base pour les données et modèles

## Utilisation

### Lancer le FL Crew

```bash
python -m fl_crew_reddit.main
```

### Utilisation programmatique

```python
from fl_crew_reddit.config import FLCrewRedditConfig
from fl_crew_reddit.crew_manager import FLCrewRedditManager

# Initialiser
config = FLCrewRedditConfig()
manager = FLCrewRedditManager(config)

# Lancer le Federated Learning
results = manager.run_federated_learning(num_rounds=10)
```

## Structure des dossiers

```
fl_crew_reddit/
├── agents/              # Les 5 agents spécialisés
├── tools/               # Outils pour MCP, données et modèles
├── data/                # Données collectées et préparées
│   ├── collected/
│   ├── preprocessed/
│   └── training/
├── models/              # Modèles locaux et agrégés
│   ├── local/
│   └── aggregated/
├── logs/                # Logs du système
└── results/             # Résultats des rounds de FL
```

## Processus de Federated Learning avec LLMs

1. **Collecte** : Les données multimodales (texte, images, vidéos) sont collectées depuis Reddit via le MCP Server
2. **Prétraitement** : Les données sont nettoyées, normalisées et formatées en JSONL pour le fine-tuning LLM
   - Extraction de texte depuis posts/comments
   - Traitement d'images (redimensionnement, encodage)
   - Création de paires texte-image pour modèles vision-language
3. **Entraînement local** : Chaque agent trainer entraîne un modèle LLM avec fine-tuning LoRA sur ses données
   - Utilisation du modèle de base configuré
   - Fine-tuning avec LoRA (paramètres adaptatifs légers)
   - Support des données multimodales
4. **Agrégation** : Les poids LoRA des modèles locaux sont agrégés en un modèle global (Federated Averaging)
   - Agrégation des poids LoRA (pas du modèle complet)
   - Méthode configurable (weighted_average, fedavg, fedprox)
5. **Évaluation** : Le modèle agrégé est évalué avec métriques LLM adaptées
   - Perplexity, BLEU, ROUGE pour génération de texte
   - Métriques multimodales (image-text alignment)
6. **Répétition** : Les étapes 3-5 sont répétées pour plusieurs rounds
   - Le modèle agrégé est distribué aux agents pour le round suivant

## Intégration avec MCP Server Reddit

Le FL Crew communique avec le MCP Server Reddit via le `RedditMCPClient` qui utilise les outils MCP disponibles :
- `collect_subreddit_posts`
- `search_reddit_posts`
- `collect_post_comments`
- `collect_user_data`
- `collect_subreddit_info`

## Technologies Utilisées

- **CrewAI** : Orchestration des agents
- **Transformers (Hugging Face)** : Modèles LLM de base
- **PEFT (LoRA/QLoRA)** : Fine-tuning efficace avec paramètres adaptatifs
- **PyTorch** : Framework d'entraînement
- **bitsandbytes** : Quantization pour QLoRA (optionnel)
- **CLIP/Vision-Language Models** : Support des données multimodales

## Notes Importantes

- **Modèles LLM** : Le système utilise des LLMs avec fine-tuning LoRA pour le Federated Learning
- **Données Multimodales** : Supporte texte, images et vidéos depuis Reddit
- **Efficacité** : LoRA permet un fine-tuning efficace avec moins de paramètres à entraîner
- **Quantization** : QLoRA peut être activé pour réduire l'utilisation mémoire
- **Stockage** : Les modèles LoRA sont beaucoup plus petits que les modèles complets
- **MCP Server** : Communication avec le MCP Server Reddit pour collecter les données

## Exemple d'Utilisation avec Modèle Personnalisé

```python
import os
os.environ["BASE_LLM_MODEL"] = "meta-llama/Llama-2-7b-hf"
os.environ["USE_QUANTIZATION"] = "true"  # Activer QLoRA
os.environ["LORA_R"] = "16"  # Augmenter le rang LoRA

from fl_crew_reddit.config import FLCrewRedditConfig
from fl_crew_reddit.crew_manager import FLCrewRedditManager

config = FLCrewRedditConfig()
manager = FLCrewRedditManager(config)
results = manager.run_federated_learning(num_rounds=5)
```

## Auteur

RAMMAH MAHA

