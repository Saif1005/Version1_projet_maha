"""
Configuration du serveur MCP LinkedIn
Fichier: mcp_servers/linkedin_server/config.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class LinkedInConfig:
    """Configuration centralisée du serveur LinkedIn"""
    
    # Credentials LinkedIn API
    CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
    CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
    ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
    REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8080/callback")
    
    # Chemins de stockage
    DATA_DIR = Path(os.getenv("LINKEDIN_DATA_DIR", "./data/linkedin_data"))
    PROFILES_DIR = DATA_DIR / "profiles"
    POSTS_DIR = DATA_DIR / "posts"
    CONNECTIONS_DIR = DATA_DIR / "connections"
    COMPANIES_DIR = DATA_DIR / "companies"
    SEARCHES_DIR = DATA_DIR / "searches"
    MESSAGES_DIR = DATA_DIR / "messages"
    INDEX_FILE = DATA_DIR / "index.json"
    
    # Limites par défaut
    DEFAULT_PROFILE_LIMIT = 25
    DEFAULT_POST_LIMIT = 50
    DEFAULT_CONNECTION_LIMIT = 100
    DEFAULT_SEARCH_LIMIT = 10
    
    # Options de recherche
    VALID_SEARCH_TYPES = ["people", "companies", "jobs", "groups", "posts"]
    VALID_SORT_OPTIONS = ["relevance", "date"]
    
    # LinkedIn API URLs
    API_BASE_URL = "https://api.linkedin.com/v2"
    AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    
    # Scopes nécessaires
    SCOPES = [
        "r_liteprofile",
        "r_emailaddress",
        "w_member_social",
        "r_basicprofile",
        "r_organization_social",
        "rw_organization_admin",
        "r_1st_connections_size"
    ]
    
    @classmethod
    def validate(cls):
        """Valide la configuration"""
        if not cls.CLIENT_ID or not cls.CLIENT_SECRET:
            raise ValueError(
                "LINKEDIN_CLIENT_ID et LINKEDIN_CLIENT_SECRET sont requis. "
                "Configurez-les dans votre fichier .env"
            )
        if not cls.ACCESS_TOKEN:
            print("⚠️  LINKEDIN_ACCESS_TOKEN non configuré. Vous devrez vous authentifier.")
        return True
    
    @classmethod
    def create_directories(cls):
        """Crée tous les dossiers nécessaires"""
        for dir_path in [cls.PROFILES_DIR, cls.POSTS_DIR, cls.CONNECTIONS_DIR,
                        cls.COMPANIES_DIR, cls.SEARCHES_DIR, cls.MESSAGES_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)