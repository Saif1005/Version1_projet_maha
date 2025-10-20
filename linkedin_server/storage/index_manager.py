"""
Gestion de l'index des données LinkedIn
Fichier: mcp_servers/linkedin_server/storage/index_manager.py
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
            "profiles": {},
            "posts": {},
            "connections": {},
            "companies": {},
            "searches": [],
            "my_profile": None,
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
    
    def add_profile(self, profile_id: str, file_path: str):
        """Ajoute un profil à l'index"""
        self.index["profiles"][profile_id] = {
            "file": file_path,
            "stored_at": datetime.now().isoformat()
        }
        self._save()
    
    def add_post(self, post_id: str, file_path: str, author_id: str):
        """Ajoute un post à l'index"""
        self.index["posts"][post_id] = {
            "file": file_path,
            "author_id": author_id,
            "stored_at": datetime.now().isoformat()
        }
        self._save()
    
    def add_company(self, company_id: str, file_path: str):
        """Ajoute une entreprise à l'index"""
        self.index["companies"][company_id] = {
            "file": file_path,
            "stored_at": datetime.now().isoformat()
        }
        self._save()
    
    def add_search(self, search_id: str, keywords: str, file_path: str, count: int):
        """Ajoute une recherche à l'index"""
        self.index["searches"].append({
            "search_id": search_id,
            "keywords": keywords,
            "file": file_path,
            "count": count,
            "timestamp": datetime.now().isoformat()
        })
        self._save()
    
    def set_my_profile(self, file_path: str):
        """Définit le fichier du profil de l'utilisateur"""
        self.index["my_profile"] = {
            "file": file_path,
            "updated_at": datetime.now().isoformat()
        }
        self._save()
    
    def get_profile(self, profile_id: str) -> Dict:
        """Récupère les infos d'un profil depuis l'index"""
        return self.index["profiles"].get(profile_id)
    
    def get_company(self, company_id: str) -> Dict:
        """Récupère les infos d'une entreprise depuis l'index"""
        return self.index["companies"].get(company_id)
    
    def get_recent_searches(self, limit: int = 10) -> List[Dict]:
        """Récupère les recherches récentes"""
        return self.index["searches"][-limit:]
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques de l'index"""
        return {
            "total_profiles": len(self.index["profiles"]),
            "total_posts": len(self.index["posts"]),
            "total_companies": len(self.index["companies"]),
            "total_searches": len(self.index["searches"]),
            "has_my_profile": self.index["my_profile"] is not None,
            "created_at": self.index["created_at"],
            "last_updated": self.index["last_updated"]
        }