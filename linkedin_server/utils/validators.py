"""
Validateurs pour les paramètres du serveur LinkedIn
Fichier: mcp_servers/linkedin_server/utils/validators.py
"""

from typing import Any, Dict
from config import LinkedInConfig


class ValidationError(Exception):
    """Exception pour les erreurs de validation"""
    pass


class LinkedInValidator:
    """Validateur pour les paramètres des outils LinkedIn"""
    
    @staticmethod
    def validate_search_params(args: Dict[str, Any]) -> Dict[str, Any]:
        """Valide les paramètres de recherche"""
        keywords = args.get("keywords")
        if not keywords or not keywords.strip():
            raise ValidationError("Le paramètre 'keywords' est requis et ne peut pas être vide")
        
        search_type = args.get("search_type", "people")
        if search_type not in LinkedInConfig.VALID_SEARCH_TYPES:
            raise ValidationError(
                f"Type de recherche invalide: {search_type}. "
                f"Options valides: {LinkedInConfig.VALID_SEARCH_TYPES}"
            )
        
        limit = args.get("limit", LinkedInConfig.DEFAULT_SEARCH_LIMIT)
        if not isinstance(limit, int) or limit < 1 or limit > 100:
            raise ValidationError("Limit doit être entre 1 et 100")
        
        return {
            "keywords": keywords.strip(),
            "search_type": search_type,
            "limit": limit
        }
    
    @staticmethod
    def validate_user_posts_params(args: Dict[str, Any]) -> Dict[str, Any]:
        """Valide les paramètres pour récupérer les posts d'un utilisateur"""
        user_id = args.get("user_id")
        if not user_id or not user_id.strip():
            raise ValidationError("Le paramètre 'user_id' est requis")
        
        limit = args.get("limit", LinkedInConfig.DEFAULT_POST_LIMIT)
        if not isinstance(limit, int) or limit < 1:
            raise ValidationError("Limit doit être supérieur à 0")
        
        return {
            "user_id": user_id.strip(),
            "limit": limit
        }
    
    @staticmethod
    def validate_connections_params(args: Dict[str, Any]) -> Dict[str, Any]:
        """Valide les paramètres pour récupérer les connexions"""
        limit = args.get("limit", LinkedInConfig.DEFAULT_CONNECTION_LIMIT)
        if not isinstance(limit, int) or limit < 1:
            raise ValidationError("Limit doit être supérieur à 0")
        
        start = args.get("start", 0)
        if not isinstance(start, int) or start < 0:
            raise ValidationError("Start doit être supérieur ou égal à 0")
        
        return {
            "limit": limit,
            "start": start
        }
    
    @staticmethod
    def validate_company_id(args: Dict[str, Any]) -> Dict[str, Any]:
        """Valide l'ID d'une entreprise"""
        company_id = args.get("company_id")
        if not company_id or not company_id.strip():
            raise ValidationError("Le paramètre 'company_id' est requis")
        
        return {
            "company_id": company_id.strip()
        }
    
    @staticmethod
    def validate_company_posts_params(args: Dict[str, Any]) -> Dict[str, Any]:
        """Valide les paramètres pour les posts d'entreprise"""
        company_id = args.get("company_id")
        if not company_id or not company_id.strip():
            raise ValidationError("Le paramètre 'company_id' est requis")
        
        limit = args.get("limit", LinkedInConfig.DEFAULT_POST_LIMIT)
        if not isinstance(limit, int) or limit < 1:
            raise ValidationError("Limit doit être supérieur à 0")
        
        return {
            "company_id": company_id.strip(),
            "limit": limit
        }
    
    @staticmethod
    def validate_share_post_params(args: Dict[str, Any]) -> Dict[str, Any]:
        """Valide les paramètres pour partager un post"""
        text = args.get("text")
        if not text or not text.strip():
            raise ValidationError("Le paramètre 'text' est requis et ne peut pas être vide")
        
        if len(text) > 3000:
            raise ValidationError("Le texte ne peut pas dépasser 3000 caractères")
        
        visibility = args.get("visibility", "PUBLIC")
        valid_visibility = ["PUBLIC", "CONNECTIONS"]
        if visibility not in valid_visibility:
            raise ValidationError(
                f"Visibilité invalide: {visibility}. Options: {valid_visibility}"
            )
        
        return {
            "text": text.strip(),
            "visibility": visibility
        }