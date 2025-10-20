"""
Outil MCP: Collecte des commentaires d'un post
Fichier: mcp_servers/reddit_server/tools/collect_comments.py
"""

import json
from typing import Any, Dict, List
from mcp.types import Tool, TextContent
from utils.validators import RedditValidator, ValidationError


class CollectCommentsTool:
    """Outil pour collecter les commentaires d'un post"""
    
    def __init__(self, api_client, file_manager):
        self.api = api_client
        self.storage = file_manager
    
    @staticmethod
    def get_definition() -> Tool:
        """Retourne la définition de l'outil pour MCP"""
        return Tool(
            name="collect_post_comments",
            description="Collecte un post Reddit avec tous ses commentaires. "
                       "Utile pour analyser les discussions sur un post spécifique.",
            inputSchema={
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "ID du post Reddit (ex: '1a2b3c4d')"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 100,
                        "minimum": 1,
                        "description": "Nombre maximum de commentaires à collecter"
                    }
                },
                "required": ["post_id"]
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Exécute la collecte des commentaires
        
        Args:
            arguments: Arguments de l'outil
            
        Returns:
            Résultat de la collecte
        """
        try:
            # Valider les paramètres
            params = RedditValidator.validate_post_id(arguments)
            
            post_id = params["post_id"]
            print(f"💬 Collecte commentaires: {post_id}")
            
            # Collecter le post et ses commentaires
            post, comments = self.api.get_post_with_comments(
                post_id=post_id,
                limit=params["limit"]
            )
            
            # Sauvegarder le post
            self.storage.save_post(post)
            
            # Sauvegarder chaque commentaire
            for comment in comments:
                self.storage.save_comment(comment)
            
            result = {
                "status": "success",
                "post_id": post_id,
                "post_title": post.get("title"),
                "post_author": post.get("author"),
                "subreddit": post.get("subreddit"),
                "comments_collected": len(comments),
                "post": post,
                "comments": comments
            }
            
            print(f"✅ {len(comments)} commentaires collectés pour {post_id}")
            
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