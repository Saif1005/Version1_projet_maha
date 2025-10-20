"""
Outil MCP: Recherche de personnes sur LinkedIn
Fichier: mcp_servers/linkedin_server/tools/search_people.py
"""

import json
from typing import Any, Dict, List
from mcp.types import Tool, TextContent
from utils.validators import LinkedInValidator, ValidationError


class SearchPeopleTool:
    """Outil pour rechercher des personnes sur LinkedIn"""
    
    def __init__(self, api_client, file_manager):
        self.api = api_client
        self.storage = file_manager
    
    @staticmethod
    def get_definition() -> Tool:
        """Retourne la définition de l'outil pour MCP"""
        return Tool(
            name="search_linkedin_people",
            description="Recherche des personnes sur LinkedIn par mots-clés. "
                       "Note: Nécessite un accès LinkedIn Partner ou Premium pour les résultats complets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "string",
                        "description": "Mots-clés de recherche (nom, titre, compétences...)"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100,
                        "description": "Nombre maximum de résultats"
                    }
                },
                "required": ["keywords"]
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Exécute la recherche de personnes"""
        try:
            params = LinkedInValidator.validate_search_params(arguments)
            
            keywords = params["keywords"]
            print(f"🔍 Recherche: '{keywords}'")
            
            people = self.api.search_people(
                keywords=keywords,
                limit=params["limit"]
            )
            
            search_file = self.storage.save_search_results(keywords, people)
            
            result = {
                "status": "success",
                "keywords": keywords,
                "people_found": len(people),
                "search_file": search_file,
                "people": people
            }
            
            print(f"✅ {len(people)} personnes trouvées")
            
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