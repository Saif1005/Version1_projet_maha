"""
Outil MCP: Posts d'une entreprise
Fichier: mcp_servers/linkedin_server/tools/get_company_posts.py
"""

import json
from typing import Any, Dict, List
from mcp.types import Tool, TextContent
from utils.validators import LinkedInValidator, ValidationError


class GetCompanyPostsTool:
    """Outil pour récupérer les posts d'une entreprise"""
    
    def __init__(self, api_client, file_manager):
        self.api = api_client
        self.storage = file_manager
    
    @staticmethod
    def get_definition() -> Tool:
        """Retourne la définition de l'outil pour MCP"""
        return Tool(
            name="get_linkedin_company_posts",
            description="Récupère les posts publiés par une entreprise LinkedIn.",
            inputSchema={
                "type": "object",
                "properties": {
                    "company_id": {
                        "type": "string",
                        "description": "ID de l'entreprise LinkedIn"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 50,
                        "minimum": 1,
                        "description": "Nombre de posts à récupérer"
                    }
                },
                "required": ["company_id"]
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Exécute la récupération des posts"""
        try:
            params = LinkedInValidator.validate_company_posts_params(arguments)
            
            company_id = params["company_id"]
            print(f"📰 Récupération des posts de l'entreprise {company_id}...")
            
            posts = self.api.get_company_posts(
                company_id=company_id,
                limit=params["limit"]
            )
            
            posts_file = self.storage.save_company_posts(company_id, posts)
            
            result = {
                "status": "success",
                "company_id": company_id,
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