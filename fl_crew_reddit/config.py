"""
Configuration du FL Crew Reddit
Fichier: fl_crew_reddit/config.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class FLCrewRedditConfig:
    """Configuration centralisée du FL Crew Reddit"""
    
    # Configuration AWS
    USE_S3_STORAGE = os.getenv("USE_S3_STORAGE", "false").lower() == "true"
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
    AWS_REGION = os.getenv("AWS_DEFAULT_REGION", os.getenv("AWS_REGION", "us-east-1"))
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # Chemins de stockage (local ou S3)
    BASE_DIR = Path(os.getenv("FL_CREW_REDDIT_DIR", "./fl_crew_reddit"))
    DATA_DIR = BASE_DIR / "data"
    MODELS_DIR = BASE_DIR / "models"
    LOGS_DIR = BASE_DIR / "logs"
    RESULTS_DIR = BASE_DIR / "results"
    
    # Préfixes S3
    S3_DATA_PREFIX = "fl_crew_reddit/data"
    S3_MODELS_PREFIX = "fl_crew_reddit/models"
    S3_LOGS_PREFIX = "fl_crew_reddit/logs"
    S3_RESULTS_PREFIX = "fl_crew_reddit/results"
    
    # Chemins pour les données collectées
    COLLECTED_DATA_DIR = DATA_DIR / "collected"
    PREPROCESSED_DATA_DIR = DATA_DIR / "preprocessed"
    TRAINING_DATA_DIR = DATA_DIR / "training"
    
    # Chemins pour les modèles
    LOCAL_MODELS_DIR = MODELS_DIR / "local"
    AGGREGATED_MODELS_DIR = MODELS_DIR / "aggregated"
    
    # Configuration MCP Server
    MCP_SERVER_PATH = os.getenv("REDDIT_MCP_SERVER_PATH", "./reddit_server")
    MCP_SERVER_COMMAND = os.getenv("REDDIT_MCP_SERVER_COMMAND", "python -m reddit_server.server")
    
    # Configuration Federated Learning pour LLMs
    NUM_AGENTS = 5
    FEDERATION_ROUNDS = 10
    LOCAL_EPOCHS = 3
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "4"))  # Plus petit pour LLMs
    LEARNING_RATE = float(os.getenv("LEARNING_RATE", "2e-4"))  # Taux adapté pour fine-tuning LLM
    GRADIENT_ACCUMULATION_STEPS = int(os.getenv("GRADIENT_ACCUMULATION_STEPS", "4"))
    MAX_SEQ_LENGTH = int(os.getenv("MAX_SEQ_LENGTH", "512"))
    AGGREGATION_METHOD = os.getenv("AGGREGATION_METHOD", "weighted_average")  # weighted_average, fedavg, fedprox
    
    # Configuration des agents (LLM pour orchestration)
    AGENT_LLM_MODEL = os.getenv("AGENT_LLM_MODEL", "gpt-4")
    AGENT_TEMPERATURE = 0.7
    AGENT_MAX_ITER = 15
    
    # Configuration du modèle de base LLM pour Federated Learning
    BASE_LLM_MODEL = os.getenv("BASE_LLM_MODEL", "mistralai/Mistral-7B-v0.1")
    USE_LORA = os.getenv("USE_LORA", "true").lower() == "true"
    LORA_R = int(os.getenv("LORA_R", "8"))
    LORA_ALPHA = int(os.getenv("LORA_ALPHA", "16"))
    USE_QUANTIZATION = os.getenv("USE_QUANTIZATION", "false").lower() == "true"
    QUANTIZATION_BITS = int(os.getenv("QUANTIZATION_BITS", "4"))
    
    # Configuration pour données multimodales
    SUPPORT_MULTIMODAL = True
    MULTIMODAL_MODALITIES = ["text", "image", "video"]  # Types de données supportés
    IMAGE_PROCESSOR = os.getenv("IMAGE_PROCESSOR", "clip-vit-base-patch32")
    MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", "224"))
    
    # Configuration de collecte
    DEFAULT_COLLECTION_LIMIT = 100
    DEFAULT_SUBREDDITS = ["python", "machinelearning", "datascience", "artificial", "technology"]
    
    # Configuration EC2/ECS
    EC2_INSTANCE_TYPE = os.getenv("EC2_INSTANCE_TYPE", "g4dn.xlarge")  # GPU instance
    ECS_CLUSTER_NAME = os.getenv("ECS_CLUSTER_NAME", "fl-crew-reddit-cluster")
    ECS_SERVICE_NAME = os.getenv("ECS_SERVICE_NAME", "fl-crew-reddit-service")
    
    @classmethod
    def create_directories(cls):
        """Crée tous les dossiers nécessaires (même si on utilise S3)"""
        dirs = [
            cls.DATA_DIR,
            cls.MODELS_DIR,
            cls.LOGS_DIR,
            cls.RESULTS_DIR,
            cls.COLLECTED_DATA_DIR,
            cls.PREPROCESSED_DATA_DIR,
            cls.TRAINING_DATA_DIR,
            cls.LOCAL_MODELS_DIR,
            cls.AGGREGATED_MODELS_DIR
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate(cls):
        """Valide la configuration"""
        cls.create_directories()
        
        # Vérifier la configuration AWS si S3 est activé
        if cls.USE_S3_STORAGE:
            if not cls.AWS_S3_BUCKET:
                raise ValueError(
                    "AWS_S3_BUCKET doit être défini si USE_S3_STORAGE=true. "
                    "Configurez-le dans votre fichier .env ou variables d'environnement"
                )
            print(f"✅ Stockage S3 activé: bucket={cls.AWS_S3_BUCKET}, region={cls.AWS_REGION}")
        else:
            print("✅ Stockage local activé")
        
        return True

