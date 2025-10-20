"""
Outil MCP: Récupération du profil utilisateur
Fichier: mcp_servers/linkedin_server/tools/get_my_profile.py
"""

import json
from typing import Any, Dict, List
from mcp.types import Tool, TextContent


class GetMyProfileTool:
    """Outil pour récupérer le profil de l'utilisateur authentifié"""
    
    def __init__(self, api_client, file_manager):
        self.api = api_client
        self.storage = file_manager
    
    @staticmethod
    def get_definition() -> Tool:
        """Retourne la définition de l'outil pour MCP"""
        return Tool(
            name="get_my_linkedin_profile",
            description="Récupère le profil LinkedIn de l'utilisateur authentifié. "
                       "Retourne les informations personnelles, l'email, et les statistiques du profil.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Exécute la récupération du profil"""
        try:
            print("👤 Récupération de votre profil LinkedIn...")
            
            profile = self.api.get_my_profile()
            
            profile_file = self.storage.save_my_profile(profile)
            
            result = {
                "status": "success",
                "profile_file": profile_file,
                "profile": profile
            }
            
            print(f"✅ Profil récupéré: {profile.get('firstName')} {profile.get('lastName')}")
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
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