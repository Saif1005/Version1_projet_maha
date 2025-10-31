"""
Outil MCP: Récupération des connexions
Fichier: mcp_servers/linkedin_server/tools/get_connections.py
"""

import json
from typing import Any, Dict, List
from mcp.types import Tool, TextContent
from utils.validators import LinkedInValidator, ValidationError


class GetConnectionsTool:
    """Outil pour récupérer les connexions LinkedIn"""
    
    def __init__(self, api_client, file_manager):
        self.api = api_client
        self.storage = file_manager
    
    @staticmethod
    def get_definition() -> Tool:
        """Retourne la définition de l'outil pour MCP"""
        return Tool(
            name="get_linkedin_connections",
            description="Récupère la liste de vos connexions LinkedIn.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "default": 100,
                        "minimum": 1,
                        "description": "Nombre de connexions à récupérer"
                    },
                    "start": {
                        "type": "integer",
                        "default": 0,
                        "minimum": 0,
                        "description": "Index de départ (pour pagination)"
                    }
                },
                "required": []
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Exécute la récupération des connexions"""
        try:
            params = LinkedInValidator.validate_connections_params(arguments)
            
            print(f"🤝 Récupération des connexions...")
            
            connections = self.api.get_connections(
                start=params["start"],
                count=params["limit"]
            )
            
            connections_file = self.storage.save_connections(connections)
            
            result = {
                "status": "success",
                "connections_count": len(connections),
                "connections_file": connections_file,
                "connections": connections
            }
            
            print(f" {len(connections)} connexions récupérées")
            
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
            print(f"Erreur: {e}")
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": "execution_error",
                    "message": str(e)
                }, indent=2)
            )]