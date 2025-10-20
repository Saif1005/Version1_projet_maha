"""
Validateurs pour les paramètres du serveur Reddit
Fichier: mcp_servers/reddit_server/utils/validators.py
"""

from typing import Any, Dict
from config import RedditConfig


class ValidationError(Exception):
    """Exception pour les erreurs de validation"""
    pass


class RedditValidator:
    """Validateur pour les paramètres des outils Reddit"""
    
    @staticmethod
    def validate_search_params(args: Dict[str, Any]) -> Dict[str, Any]:
        """Valide les paramètres de recherche"""
        query = args.get("query")
        if not query or not query.strip():
            raise ValidationError("Le paramètre 'query' est requis et ne peut pas être vide")
        
        sort = args.get("sort", "relevance")
        if sort not in RedditConfig.VALID_SORT_OPTIONS:
            raise ValidationError(
                f"Sort invalide: {sort}. Options valides: {RedditConfig.VALID_SORT_OPTIONS}"
            )
        
        limit = args.get("limit", RedditConfig.DEFAULT_SEARCH_LIMIT)
        if not isinstance(limit, int) or limit < 1 or limit > 100:
            raise ValidationError("Limit doit être entre 1 et 100")
        
        return {
            "query": query.strip(),
            "subreddit": args.get("subreddit"),
            "sort": sort,
            "limit": limit
        }
    
    @staticmethod
    def validate_subreddit_params(args: Dict[str, Any]) -> Dict[str, Any]:
        """Valide les paramètres de collecte de subreddit"""
        subreddit = args.get("subreddit")
        if not subreddit or not subreddit.strip():
            raise ValidationError("Le paramètre 'subreddit' est requis")
        
        sort = args.get("sort", "hot")
        if sort not in RedditConfig.VALID_SUBREDDIT_SORT:
            raise ValidationError(
                f"Sort invalide: {sort}. Options valides: {RedditConfig.VALID_SUBREDDIT_SORT}"
            )
        
        limit = args.get("limit", RedditConfig.DEFAULT_POST_LIMIT)
        if not isinstance(limit, int) or limit < 1 or limit > 100:
            raise ValidationError("Limit doit être entre 1 et 100")
        
        time_filter = args.get("time_filter", "day")
        if time_filter not in RedditConfig.VALID_TIME_FILTERS:
            raise ValidationError(
                f"Time filter invalide: {time_filter}. Options valides: {RedditConfig.VALID_TIME_FILTERS}"
            )
        
        return {
            "subreddit": subreddit.strip(),
            "sort": sort,
            "limit": limit,
            "time_filter": time_filter
        }
    
    @staticmethod
    def validate_post_id(args: Dict[str, Any]) -> Dict[str, Any]:
        """Valide l'ID d'un post"""
        post_id = args.get("post_id")
        if not post_id or not post_id.strip():
            raise ValidationError("Le paramètre 'post_id' est requis")
        
        limit = args.get("limit", RedditConfig.DEFAULT_COMMENT_LIMIT)
        if not isinstance(limit, int) or limit < 1:
            raise ValidationError("Limit doit être supérieur à 0")
        
        return {
            "post_id": post_id.strip(),
            "limit": limit
        }
    
    @staticmethod
    def validate_username(args: Dict[str, Any]) -> Dict[str, Any]:
        """Valide le nom d'utilisateur"""
        username = args.get("username")
        if not username or not username.strip():
            raise ValidationError("Le paramètre 'username' est requis")
        
        limit = args.get("limit", RedditConfig.DEFAULT_USER_LIMIT)
        if not isinstance(limit, int) or limit < 1:
            raise ValidationError("Limit doit être supérieur à 0")
        
        return {
            "username": username.strip(),
            "include_posts": args.get("include_posts", True),
            "include_comments": args.get("include_comments", True),
            "limit": limit
        }
    
    @staticmethod
    def validate_subreddit_name(args: Dict[str, Any]) -> Dict[str, Any]:
        """Valide le nom d'un subreddit"""
        subreddit = args.get("subreddit")
        if not subreddit or not subreddit.strip():
            raise ValidationError("Le paramètre 'subreddit' est requis")
        
        return {
            "subreddit": subreddit.strip()
        }