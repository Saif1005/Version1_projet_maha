"""
Gestion des fichiers de données LinkedIn
Fichier: mcp_servers/linkedin_server/storage/file_manager.py
"""

import json
from datetime import datetime
from typing import Dict, List
from pathlib import Path
from .index_manager import IndexManager


class FileManager:
    """Gestionnaire des fichiers de stockage"""
    
    def __init__(self, config, index_manager: IndexManager):
        self.config = config
        self.index = index_manager
    
    def _write_json(self, file_path: Path, data: Dict):
        """Écrit des données JSON dans un fichier"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _read_json(self, file_path: Path) -> Dict:
        """Lit des données JSON depuis un fichier"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_profile(self, profile_data: Dict) -> str:
        """Sauvegarde un profil LinkedIn"""
        profile_id = profile_data.get("id", "unknown")
        file_path = self.config.PROFILES_DIR / f"{profile_id}.json"
        
        self._write_json(file_path, profile_data)
        self.index.add_profile(profile_id, str(file_path))
        
        return str(file_path)
    
    def save_my_profile(self, profile_data: Dict) -> str:
        """Sauvegarde le profil de l'utilisateur authentifié"""
        file_path = self.config.PROFILES_DIR / "my_profile.json"
        
        self._write_json(file_path, profile_data)
        self.index.set_my_profile(str(file_path))
        
        return str(file_path)
    
    def save_post(self, post_data: Dict) -> str:
        """Sauvegarde un post LinkedIn"""
        post_id = post_data.get("id", "unknown")
        file_path = self.config.POSTS_DIR / f"{post_id}.json"
        
        self._write_json(file_path, post_data)
        self.index.add_post(post_id, str(file_path), post_data.get("author", ""))
        
        return str(file_path)
    
    def save_connections(self, connections: List[Dict]) -> str:
        """Sauvegarde la liste des connexions"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = self.config.CONNECTIONS_DIR / f"connections_{timestamp}.json"
        
        collection_data = {
            "collected_at": datetime.now().isoformat(),
            "count": len(connections),
            "connections": connections
        }
        
        self._write_json(file_path, collection_data)
        
        return str(file_path)
    
    def save_company(self, company_data: Dict) -> str:
        """Sauvegarde une entreprise"""
        company_id = company_data.get("id", "unknown")
        file_path = self.config.COMPANIES_DIR / f"{company_id}.json"
        
        self._write_json(file_path, company_data)
        self.index.add_company(company_id, str(file_path))
        
        return str(file_path)
    
    def save_search_results(self, keywords: str, results: List[Dict]) -> str:
        """Sauvegarde les résultats d'une recherche"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_keywords = keywords.replace(' ', '_')[:50]
        search_id = f"search_{timestamp}_{safe_keywords}"
        file_path = self.config.SEARCHES_DIR / f"{search_id}.json"
        
        search_data = {
            "search_id": search_id,
            "keywords": keywords,
            "retrieved_at": datetime.now().isoformat(),
            "count": len(results),
            "results": results
        }
        
        self._write_json(file_path, search_data)
        self.index.add_search(search_id, keywords, str(file_path), len(results))
        
        return str(file_path)
    
    def save_user_posts(self, user_id: str, posts: List[Dict]) -> str:
        """Sauvegarde les posts d'un utilisateur"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = self.config.POSTS_DIR / f"{user_id}_posts_{timestamp}.json"
        
        collection_data = {
            "user_id": user_id,
            "collected_at": datetime.now().isoformat(),
            "count": len(posts),
            "posts": posts
        }
        
        self._write_json(file_path, collection_data)
        
        return str(file_path)
    
    def save_company_posts(self, company_id: str, posts: List[Dict]) -> str:
        """Sauvegarde les posts d'une entreprise"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = self.config.POSTS_DIR / f"company_{company_id}_posts_{timestamp}.json"
        
        collection_data = {
            "company_id": company_id,
            "collected_at": datetime.now().isoformat(),
            "count": len(posts),
            "posts": posts
        }
        
        self._write_json(file_path, collection_data)
        
        return str(file_path)
    
    def get_profile(self, profile_id: str) -> Dict:
        """Récupère un profil par son ID"""
        profile_info = self.index.get_profile(profile_id)
        if profile_info:
            return self._read_json(Path(profile_info["file"]))
        return None
    
    def get_company(self, company_id: str) -> Dict:
        """Récupère une entreprise par son ID"""
        company_info = self.index.get_company(company_id)
        if company_info:
            return self._read_json(Path(company_info["file"]))
        return None