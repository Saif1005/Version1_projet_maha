"""
Serveur MCP LinkedIn - Point d'entrée principal
Fichier: mcp_servers/linkedin_server/server.py
"""

import asyncio
from typing import Any, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

from config import LinkedInConfig
from utils.auth import LinkedInAuth
from utils.api_client import LinkedInAPIClient
from storage.index_manager import IndexManager
from storage.file_manager import FileManager

from tools.get_my_profile import GetMyProfileTool
from tools.search_people import SearchPeopleTool
from tools.get_connections import GetConnectionsTool
from tools.get_user_posts import GetUserPostsTool
from tools.get_company_info import GetCompanyInfoTool
from tools.get_company_posts import GetCompanyPostsTool
from tools.share_post import SharePostTool


class LinkedInMCPServer:
    """Serveur MCP pour LinkedIn"""
    
    def __init__(self):
        LinkedInConfig.validate()
        LinkedInConfig.create_directories()
        
        self.config = LinkedInConfig
        
        self.auth = LinkedInAuth(
            LinkedInConfig.CLIENT_ID,
            LinkedInConfig.CLIENT_SECRET,
            LinkedInConfig.REDIRECT_URI
        )
        
        if LinkedInConfig.ACCESS_TOKEN:
            self.auth.set_access_token(LinkedInConfig.ACCESS_TOKEN)
        
        self.api_client = LinkedInAPIClient(self.auth)
        
        self.index_manager = IndexManager(LinkedInConfig.INDEX_FILE)
        self.file_manager = FileManager(LinkedInConfig, self.index_manager)
        
        self.tools = {
            "get_my_linkedin_profile": GetMyProfileTool(self.api_client, self.file_manager),
            "search_linkedin_people": SearchPeopleTool(self.api_client, self.file_manager),
            "get_linkedin_connections": GetConnectionsTool(self.api_client, self.file_manager),
            "get_linkedin_user_posts": GetUserPostsTool(self.api_client, self.file_manager),
            "get_linkedin_company_info": GetCompanyInfoTool(self.api_client, self.file_manager),
            "get_linkedin_company_posts": GetCompanyPostsTool(self.api_client, self.file_manager),
            "share_linkedin_post": SharePostTool(self.api_client, self.file_manager)
        }
        
        self.server = Server("linkedin-mcp-server")
        self._setup_handlers()
        
        print("Serveur MCP LinkedIn initialisé")
        print(f"   Data directory: {self.config.DATA_DIR}")
        print(f"   🔧 Outils disponibles: {len(self.tools)}")
        
        if not LinkedInConfig.ACCESS_TOKEN:
            print("\n  Access token non configuré!")
            print(f"   URL d'autorisation: {self.auth.get_authorization_url()}")
    
    def _setup_handlers(self):
        """Configure les handlers MCP"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            return [
                Resource(
                    uri="linkedin://index",
                    name="LinkedIn Index",
                    mimeType="application/json",
                    description="Index des données LinkedIn collectées"
                ),
                Resource(
                    uri="linkedin://stats",
                    name="LinkedIn Stats",
                    mimeType="application/json",
                    description="Statistiques du serveur"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            if uri == "linkedin://stats":
                stats = self.index_manager.get_stats()
                return f"Statistiques LinkedIn:\n{stats}"
            return "Ressource non trouvée"
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [tool.get_definition() for tool in self.tools.values()]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> List[TextContent]:
            try:
                if name not in self.tools:
                    raise ValueError(f"Outil inconnu: {name}")
                
                tool = self.tools[name]
                return await tool.execute(arguments)
                
            except Exception as e:
                print(f" Erreur outil '{name}': {e}")
                import json
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "tool": name,
                        "error": str(e)
                    }, indent=2)
                )]
    
    async def run(self):
        """Lance le serveur"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Point d'entrée principal"""
    print("\n" + "="*60)
    print(" MCP SERVER LINKEDIN")
    print("="*60 + "\n")
    
    server = LinkedInMCPServer()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n Arrêt du serveur LinkedIn")
    except Exception as e:
        print(f"\n Erreur fatale: {e}")
        raise