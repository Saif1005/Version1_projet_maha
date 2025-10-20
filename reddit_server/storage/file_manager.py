"""
Gestion des fichiers de données Reddit
Fichier: mcp_servers/reddit_server/storage/file_manager.py
"""

import json
from datetime import datetime
from typing import Dict, List
from pathlib import Path
from storage.index_manager import IndexManager


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
    
    def save_post(self, post_data: Dict) -> str:
        """
        Sauvegarde un post Reddit
        
        Args:
            post_data: Données du post
            
        Returns:
            Chemin du fichier créé
        """
        post_id = post_data["id"]
        file_path = self.config.POSTS_DIR / f"{post_id}.json"
        
        self._write_json(file_path, post_data)
        self.index.add_post(post_id, str(file_path), post_data.get("subreddit"))
        
        return str(file_path)
    
    def save_comment(self, comment_data: Dict) -> str:
        """
        Sauvegarde un commentaire
        
        Args:
            comment_data: Données du commentaire
            
        Returns:
            Chemin du fichier créé
        """
        comment_id = comment_data["id"]
        file_path = self.config.COMMENTS_DIR / f"{comment_id}.json"
        
        self._write_json(file_path, comment_data)
        self.index.add_comment(comment_id, str(file_path), comment_data.get("post_id"))
        
        return str(file_path)
    
    def save_user_data(self, username: str, user_data: Dict) -> str:
        """
        Sauvegarde les données d'un utilisateur
        
        Args:
            username: Nom d'utilisateur
            user_data: Données de l'utilisateur
            
        Returns:
            Chemin du fichier créé
        """
        file_path = self.config.USERS_DIR / f"{username}_complete.json"
        
        self._write_json(file_path, user_data)
        self.index.add_user(username, str(file_path))
        
        return str(file_path)
    
    def save_subreddit_collection(self, subreddit: str, posts: List[Dict]) -> str:
        """
        Sauvegarde une collection de posts d'un subreddit
        
        Args:
            subreddit: Nom du subreddit
            posts: Liste des posts
            
        Returns:
            Chemin du fichier créé
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = self.config.SUBREDDITS_DIR / f"{subreddit}_collection_{timestamp}.json"
        
        collection_data = {
            "subreddit": subreddit,
            "collected_at": datetime.now().isoformat(),
            "count": len(posts),
            "posts": posts
        }
        
        self._write_json(file_path, collection_data)
        
        return str(file_path)
    
    def save_search_results(self, query: str, results: List[Dict]) -> str:
        """
        Sauvegarde les résultats d'une recherche
        
        Args:
            query: Requête de recherche
            results: Liste des résultats
            
        Returns:
            Chemin du fichier créé
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_query = query.replace(' ', '_')[:50]  # Limiter la longueur
        search_id = f"search_{timestamp}_{safe_query}"
        file_path = self.config.SEARCHES_DIR / f"{search_id}.json"
        
        search_data = {
            "search_id": search_id,
            "query": query,
            "retrieved_at": datetime.now().isoformat(),
            "count": len(results),
            "results": results
        }
        
        self._write_json(file_path, search_data)
        self.index.add_search(search_id, query, str(file_path), len(results))
        
        return str(file_path)
    
    def get_post(self, post_id: str) -> Dict:
        """Récupère un post par son ID"""
        post_info = self.index.get_post(post_id)
        if post_info:
            return self._read_json(Path(post_info["file"]))
        return None
    
    def get_user_data(self, username: str) -> Dict:
        """Récupère les données d'un utilisateur"""
        user_info = self.index.get_user(username)
        if user_info:
            return self._read_json(Path(user_info["file"]))
        return None