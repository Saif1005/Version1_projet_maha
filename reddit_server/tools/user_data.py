"""
Outil MCP: Collecte des données d'un utilisateur
Fichier: mcp_servers/reddit_server/tools/user_data.py
"""

import json
from typing import Any, Dict, List
from mcp.types import Tool, TextContent
from utils.validators import RedditValidator, ValidationError


class UserDataTool:
    """Outil pour collecter les données d'un utilisateur"""
    
    def __init__(self, api_client, file_manager):
        self.api = api_client
        self.storage = file_manager
    
    @staticmethod
    def get_definition() -> Tool:
        """Retourne la définition de l'outil pour MCP"""
        return Tool(
            name="collect_user_data",
            description="Collecte les données d'un utilisateur Reddit: profil, posts, commentaires. "
                       "Utile pour analyser l'activité et l'historique d'un utilisateur.",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Nom d'utilisateur Reddit (sans le 'u/', ex: 'spez')"
                    },
                    "include_posts": {
                        "type": "boolean",
                        "default": True,
                        "description": "Inclure les posts de l'utilisateur"
                    },
                    "include_comments": {
                        "type": "boolean",
                        "default": True,
                        "description": "Inclure les commentaires de l'utilisateur"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 100,
                        "minimum": 1,
                        "description": "Nombre maximum d'éléments par catégorie"
                    }
                },
                "required": ["username"]
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Exécute la collecte des données utilisateur
        
        Args:
            arguments: Arguments de l'outil
            
        Returns:
            Résultat de la collecte
        """
        try:
            # Valider les paramètres
            params = RedditValidator.validate_username(arguments)
            
            username = params["username"]
            print(f" Collecte données: u/{username}")
            
            # Collecter les données utilisateur
            user_data = self.api.get_user_data(
                username=username,
                include_posts=params["include_posts"],
                include_comments=params["include_comments"],
                limit=params["limit"]
            )
            
            # Sauvegarder les données
            user_file = self.storage.save_user_data(username, user_data)
            
            result = {
                "status": "success",
                "username": username,
                "comment_karma": user_data.get("comment_karma"),
                "link_karma": user_data.get("link_karma"),
                "account_created": user_data.get("created_utc"),
                "is_gold": user_data.get("is_gold"),
                "posts_collected": len(user_data.get("posts", [])),
                "comments_collected": len(user_data.get("comments", [])),
                "user_file": user_file,
                "user_data": user_data
            }
            
            print(f"Données collectées pour u/{username}")
            print(f"   Posts: {result['posts_collected']}, Commentaires: {result['comments_collected']}")
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
            
        except ValidationError as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": "validation_error",
                    "message": str(e)
                }, indent=2)
            )]
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": "execution_error",
                    "message": str(e)
                }, indent=2)
            )]