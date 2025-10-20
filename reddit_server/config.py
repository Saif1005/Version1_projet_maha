"""
Configuration du serveur MCP Reddit
Fichier: mcp_servers/reddit_server/config.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class RedditConfig:
    """Configuration centralisée du serveur Reddit"""
    
    # Credentials Reddit API
    CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    USER_AGENT = os.getenv("REDDIT_USER_AGENT", "MCP Reddit Server v1.0")
    
    # Chemins de stockage
    DATA_DIR = Path(os.getenv("REDDIT_DATA_DIR", "./data/reddit_data"))
    POSTS_DIR = DATA_DIR / "posts"
    COMMENTS_DIR = DATA_DIR / "comments"
    USERS_DIR = DATA_DIR / "users"
    SUBREDDITS_DIR = DATA_DIR / "subreddits"
    SEARCHES_DIR = DATA_DIR / "searches"
    INDEX_FILE = DATA_DIR / "index.json"
    
    # Limites par défaut
    DEFAULT_POST_LIMIT = 25
    DEFAULT_COMMENT_LIMIT = 100
    DEFAULT_USER_LIMIT = 100
    DEFAULT_SEARCH_LIMIT = 10
    
    # Options de recherche
    VALID_SORT_OPTIONS = ["relevance", "hot", "top", "new", "comments"]
    VALID_SUBREDDIT_SORT = ["hot", "new", "top", "rising"]
    VALID_TIME_FILTERS = ["hour", "day", "week", "month", "year", "all"]
    
    @classmethod
    def validate(cls):
        """Valide la configuration"""
        if not cls.CLIENT_ID or not cls.CLIENT_SECRET:
            raise ValueError(
                "REDDIT_CLIENT_ID et REDDIT_CLIENT_SECRET sont requis. "
                "Configurez-les dans votre fichier .env"
            )
        return True
    
    @classmethod
    def create_directories(cls):
        """Crée tous les dossiers nécessaires"""
        for dir_path in [cls.POSTS_DIR, cls.COMMENTS_DIR, cls.USERS_DIR, 
                        cls.SUBREDDITS_DIR, cls.SEARCHES_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)