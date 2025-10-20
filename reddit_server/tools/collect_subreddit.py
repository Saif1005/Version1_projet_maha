"""
Outil MCP: Collecte des posts d'un subreddit
Fichier: mcp_servers/reddit_server/tools/collect_subreddit.py
"""

import json
from typing import Any, Dict, List
from mcp.types import Tool, TextContent
from utils.validators import RedditValidator, ValidationError


class CollectSubredditTool:
    """Outil pour collecter les posts d'un subreddit"""
    
    def __init__(self, api_client, file_manager):
        self.api = api_client
        self.storage = file_manager
    
    @staticmethod
    def get_definition() -> Tool:
        """Retourne la définition de l'outil pour MCP"""
        return Tool(
            name="collect_subreddit_posts",
            description="Collecte les posts d'un subreddit spécifique. "
                       "Permet de récupérer les posts hot, new, top ou rising.",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit": {
                        "type": "string",
                        "description": "Nom du subreddit (sans le 'r/', ex: 'python')"
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["hot", "new", "top", "rising"],
                        "default": "hot",
                        "description": "Méthode de tri"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 25,
                        "minimum": 1,
                        "maximum": 100,
                        "description": "Nombre de posts à collecter"
                    },
                    "time_filter": {
                        "type": "string",
                        "enum": ["hour", "day", "week", "month", "year", "all"],
                        "default": "day",
                        "description": "Filtre temporel (seulement pour sort='top')"
                    }
                },
                "required": ["subreddit"]
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Exécute la collecte du subreddit
        
        Args:
            arguments: Arguments de l'outil
            
        Returns:
            Résultat de la collecte
        """
        try:
            # Valider les paramètres
            params = RedditValidator.validate_subreddit_params(arguments)
            
            subreddit = params["subreddit"]
            print(f"📂 Collecte: r/{subreddit} (tri: {params['sort']})")
            
            # Collecter les posts
            posts = self.api.get_subreddit_posts(
                subreddit=subreddit,
                sort=params["sort"],
                limit=params["limit"],
                time_filter=params["time_filter"]
            )
            
            # Sauvegarder chaque post
            for post in posts:
                self.storage.save_post(post)
            
            # Sauvegarder la collection complète
            collection_file = self.storage.save_subreddit_collection(subreddit, posts)
            
            result = {
                "status": "success",
                "subreddit": subreddit,
                "sort": params["sort"],
                "time_filter": params["time_filter"],
                "posts_collected": len(posts),
                "collection_file": collection_file,
                "posts": posts
            }
            
            print(f"✅ {len(posts)} posts collectés de r/{subreddit}")
            
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