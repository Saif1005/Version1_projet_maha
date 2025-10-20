"""
Outil MCP: Recherche de posts Reddit
Fichier: mcp_servers/reddit_server/tools/search_posts.py
"""

import json
from typing import Any, Dict, List
from mcp.types import Tool, TextContent
from utils.validators import RedditValidator, ValidationError


class SearchPostsTool:
    """Outil pour rechercher des posts sur Reddit"""
    
    def __init__(self, api_client, file_manager):
        self.api = api_client
        self.storage = file_manager
    
    @staticmethod
    def get_definition() -> Tool:
        """Retourne la définition de l'outil pour MCP"""
        return Tool(
            name="search_reddit_posts",
            description="Recherche des posts sur Reddit par mots-clés. "
                       "Permet de rechercher dans tous les subreddits ou dans un subreddit spécifique.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Terme de recherche ou mots-clés"
                    },
                    "subreddit": {
                        "type": "string",
                        "description": "Subreddit spécifique (optionnel, ex: 'python')"
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["relevance", "hot", "top", "new", "comments"],
                        "default": "relevance",
                        "description": "Méthode de tri des résultats"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100,
                        "description": "Nombre maximum de résultats"
                    }
                },
                "required": ["query"]
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Exécute la recherche de posts
        
        Args:
            arguments: Arguments de l'outil
            
        Returns:
            Résultat de la recherche
        """
        try:
            # Valider les paramètres
            params = RedditValidator.validate_search_params(arguments)
            
            query = params["query"]
            subreddit = params.get("subreddit")
            
            print(f"🔍 Recherche: '{query}'" + 
                  (f" dans r/{subreddit}" if subreddit else " (global)"))
            
            # Effectuer la recherche
            posts = self.api.search_posts(
                query=query,
                subreddit=subreddit,
                sort=params["sort"],
                limit=params["limit"]
            )
            
            # Sauvegarder les posts
            for post in posts:
                self.storage.save_post(post)
            
            # Sauvegarder les résultats de recherche
            search_file = self.storage.save_search_results(query, posts)
            
            result = {
                "status": "success",
                "query": query,
                "subreddit": subreddit or "all",
                "sort": params["sort"],
                "posts_found": len(posts),
                "search_file": search_file,
                "posts": posts
            }
            
            print(f"✅ {len(posts)} posts trouvés")
            
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