"""
Outil MCP: Informations d'un subreddit
Fichier: mcp_servers/reddit_server/tools/subreddit_info.py
"""

import json
from typing import Any, Dict, List
from mcp.types import Tool, TextContent
from utils.validators import RedditValidator, ValidationError


class SubredditInfoTool:
    """Outil pour obtenir les informations d'un subreddit"""
    
    def __init__(self, api_client, file_manager):
        self.api = api_client
        self.storage = file_manager
    
    @staticmethod
    def get_definition() -> Tool:
        """Retourne la définition de l'outil pour MCP"""
        return Tool(
            name="collect_subreddit_info",
            description="Collecte les informations et statistiques d'un subreddit: "
                       "description, nombre d'abonnés, date de création, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit": {
                        "type": "string",
                        "description": "Nom du subreddit (sans le 'r/', ex: 'python')"
                    }
                },
                "required": ["subreddit"]
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Exécute la collecte des informations du subreddit
        
        Args:
            arguments: Arguments de l'outil
            
        Returns:
            Informations du subreddit
        """
        try:
            # Valider les paramètres
            params = RedditValidator.validate_subreddit_name(arguments)
            
            subreddit = params["subreddit"]
            print(f"  Info subreddit: r/{subreddit}")
            
            # Collecter les informations
            info = self.api.get_subreddit_info(subreddit)
            
            result = {
                "status": "success",
                "subreddit": subreddit,
                "info": info
            }
            
            print(f" Info r/{subreddit} collectée")
            print(f"   Abonnés: {info.get('subscribers'):,}")
            
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
            print(f" Erreur: {e}")
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": "execution_error",
                    "message": str(e)
                }, indent=2)
            )]