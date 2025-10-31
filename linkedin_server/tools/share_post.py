"""
Outil MCP: Partager un post sur LinkedIn
Fichier: mcp_servers/linkedin_server/tools/share_post.py
"""

import json
from typing import Any, Dict, List
from mcp.types import Tool, TextContent
from utils.validators import LinkedInValidator, ValidationError


class SharePostTool:
    """Outil pour partager un post sur LinkedIn"""
    
    def __init__(self, api_client, file_manager):
        self.api = api_client
        self.storage = file_manager
    
    @staticmethod
    def get_definition() -> Tool:
        """Retourne la définition de l'outil pour MCP"""
        return Tool(
            name="share_linkedin_post",
            description="Partage un post sur votre profil LinkedIn.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Contenu du post (max 3000 caractères)"
                    },
                    "visibility": {
                        "type": "string",
                        "enum": ["PUBLIC", "CONNECTIONS"],
                        "default": "PUBLIC",
                        "description": "Visibilité du post"
                    }
                },
                "required": ["text"]
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Exécute le partage du post"""
        try:
            params = LinkedInValidator.validate_share_post_params(arguments)
            
            text = params["text"]
            print(f" Partage d'un post sur LinkedIn...")
            
            post_result = self.api.share_post(
                text=text,
                visibility=params["visibility"]
            )
            
            result = {
                "status": "success",
                "post_id": post_result.get("id"),
                "text": text[:100] + "..." if len(text) > 100 else text,
                "visibility": params["visibility"],
                "result": post_result
            }
            
            print(f"Post partagé avec succès")
            
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