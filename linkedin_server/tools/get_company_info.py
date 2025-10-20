"""
Outil MCP: Informations d'une entreprise
Fichier: mcp_servers/linkedin_server/tools/get_company_info.py
"""

import json
from typing import Any, Dict, List
from mcp.types import Tool, TextContent
from utils.validators import LinkedInValidator, ValidationError


class GetCompanyInfoTool:
    """Outil pour récupérer les informations d'une entreprise"""
    
    def __init__(self, api_client, file_manager):
        self.api = api_client
        self.storage = file_manager
    
    @staticmethod
    def get_definition() -> Tool:
        """Retourne la définition de l'outil pour MCP"""
        return Tool(
            name="get_linkedin_company_info",
            description="Récupère les informations et statistiques d'une entreprise LinkedIn.",
            inputSchema={
                "type": "object",
                "properties": {
                    "company_id": {
                        "type": "string",
                        "description": "ID de l'entreprise LinkedIn"
                    }
                },
                "required": ["company_id"]
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Exécute la récupération des informations"""
        try:
            params = LinkedInValidator.validate_company_id(arguments)
            
            company_id = params["company_id"]
            print(f"🏢 Récupération des informations de l'entreprise {company_id}...")
            
            company_info = self.api.get_company_info(company_id)
            
            company_file = self.storage.save_company(company_info)
            
            result = {
                "status": "success",
                "company_id": company_id,
                "company_file": company_file,
                "company_info": company_info
            }
            
            print(f"✅ Informations de {company_info.get('name')} récupérées")
            
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