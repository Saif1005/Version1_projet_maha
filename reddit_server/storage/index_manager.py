"""
Gestion de l'index des données Reddit
Fichier: mcp_servers/reddit_server/storage/index_manager.py
"""

import json
from datetime import datetime
from typing import Dict, List
from pathlib import Path


class IndexManager:
    """Gestionnaire de l'index centralisé"""
    
    def __init__(self, index_file: Path):
        self.index_file = index_file
        self.index = self._load_or_create()
    
    def _load_or_create(self) -> Dict:
        """Charge l'index ou le crée s'il n'existe pas"""
        if self.index_file.exists():
            return self._load()
        else:
            return self._create_new()
    
    def _load(self) -> Dict:
        """Charge l'index depuis le fichier"""
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self._create_new()
    
    def _create_new(self) -> Dict:
        """Crée un nouvel index"""
        index = {
            "posts": {},
            "comments": {},
            "users": {},
            "subreddits": {},
            "searches": [],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        self._save(index)
        return index
    
    def _save(self, index: Dict = None):
        """Sauvegarde l'index"""
        if index is None:
            index = self.index
        
        index["last_updated"] = datetime.now().isoformat()
        
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
    
    def add_post(self, post_id: str, file_path: str, subreddit: str):
        """Ajoute un post à l'index"""
        self.index["posts"][post_id] = {
            "file": file_path,
            "subreddit": subreddit,
            "stored_at": datetime.now().isoformat()
        }
        self._save()
    
    def add_comment(self, comment_id: str, file_path: str, post_id: str):
        """Ajoute un commentaire à l'index"""
        self.index["comments"][comment_id] = {
            "file": file_path,
            "post_id": post_id,
            "stored_at": datetime.now().isoformat()
        }
        self._save()
    
    def add_user(self, username: str, file_path: str):
        """Ajoute un utilisateur à l'index"""
        self.index["users"][username] = {
            "file": file_path,
            "stored_at": datetime.now().isoformat()
        }
        self._save()
    
    def add_search(self, search_id: str, query: str, file_path: str, count: int):
        """Ajoute une recherche à l'index"""
        self.index["searches"].append({
            "search_id": search_id,
            "query": query,
            "file": file_path,
            "count": count,
            "timestamp": datetime.now().isoformat()
        })
        self._save()
    
    def get_post(self, post_id: str) -> Dict:
        """Récupère les infos d'un post depuis l'index"""
        return self.index["posts"].get(post_id)
    
    def get_user(self, username: str) -> Dict:
        """Récupère les infos d'un utilisateur depuis l'index"""
        return self.index["users"].get(username)
    
    def get_recent_searches(self, limit: int = 10) -> List[Dict]:
        """Récupère les recherches récentes"""
        return self.index["searches"][-limit:]
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques de l'index"""
        return {
            "total_posts": len(self.index["posts"]),
            "total_comments": len(self.index["comments"]),
            "total_users": len(self.index["users"]),
            "total_searches": len(self.index["searches"]),
            "created_at": self.index["created_at"],
            "last_updated": self.index["last_updated"]
        }