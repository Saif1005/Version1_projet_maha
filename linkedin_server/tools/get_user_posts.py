"""
Outil MCP: Récupération des posts d'un utilisateur
Fichier: mcp_servers/linkedin_server/tools/get_user_posts.py
"""

import json
from typing import Any, Dict, List
from mcp.types import Tool, TextContent
from utils.validators import LinkedInValidator, ValidationError


class GetUserPostsTool:
    """Outil pour récupérer les posts d'un utilisateur"""
    
    def __init__(self, api_client, file_manager):
        self.api = api_client
        self.storage = file_manager
    
    @staticmethod
    def get_definition() -> Tool:
        """Retourne la définition de l'outil pour MCP"""
        return Tool(
            name="get_linkedin_user_posts",
            description="Récupère les posts publiés par un utilisateur LinkedIn.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID de l'utilisateur LinkedIn (URN format)"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 50,
                        "minimum": 1,
                        "description": "Nombre de posts à récupérer"
                    }
                },
                "required": ["user_id"]
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Exécute la récupération des posts"""
        try:
            params = LinkedInValidator.validate_user_posts_params(arguments)
            
            user_id = params["user_id"]
            print(f"📝 Récupération des posts de l'utilisateur {user_id}...")
            
            posts = self.api.get_user_posts(
                user_urn=user_id,
                limit=params["limit"]
            )
            
            posts_file = self.storage.save_user_posts(user_id, posts)
            
            result = {
                "status": "success",
                "user_id": user_id,
                "posts_count": len(posts),
                "posts_file": posts_file,
                "posts": posts
            }
            
            print(f"✅ {len(posts)} posts récupérés")
            
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