"""
Serveur MCP Reddit - Point d'entrée principal
Fichier: mcp_servers/reddit_server/server.py
"""

import asyncio
from typing import Any, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

from config import RedditConfig
from utils.api_client import RedditAPIClient
from storage.index_manager import IndexManager
from storage.file_manager import FileManager

# Import des outils
from tools.search_posts import SearchPostsTool
from tools.collect_subreddit import CollectSubredditTool
from tools.collect_comments import CollectCommentsTool
from tools.user_data import UserDataTool
from tools.subreddit_info import SubredditInfoTool


class RedditMCPServer:
    """Serveur MCP pour Reddit"""
    
    def __init__(self):
        # Valider et créer les dossiers
        RedditConfig.validate()
        RedditConfig.create_directories()
        
        # Initialiser les composants
        self.config = RedditConfig
        self.api_client = RedditAPIClient(
            RedditConfig.CLIENT_ID,
            RedditConfig.CLIENT_SECRET,
            RedditConfig.USER_AGENT
        )
        
        self.index_manager = IndexManager(RedditConfig.INDEX_FILE)
        self.file_manager = FileManager(RedditConfig, self.index_manager)
        
        # Initialiser les outils
        self.tools = {
            "search_reddit_posts": SearchPostsTool(self.api_client, self.file_manager),
            "collect_subreddit_posts": CollectSubredditTool(self.api_client, self.file_manager),
            "collect_post_comments": CollectCommentsTool(self.api_client, self.file_manager),
            "collect_user_data": UserDataTool(self.api_client, self.file_manager),
            "collect_subreddit_info": SubredditInfoTool(self.api_client, self.file_manager)
        }
        
        # Créer le serveur MCP
        self.server = Server("reddit-mcp-server")
        self._setup_handlers()
        
        print(" Serveur MCP Reddit initialisé")
        print(f"   Data directory: {self.config.DATA_DIR}")
        print(f"   Outils disponibles: {len(self.tools)}")
    
    def _setup_handlers(self):
        """Configure les handlers MCP"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """Liste les ressources disponibles"""
            return [
                Resource(
                    uri="reddit://index",
                    name="Reddit Index",
                    mimeType="application/json",
                    description="Index des données Reddit collectées"
                ),
                Resource(
                    uri="reddit://stats",
                    name="Reddit Stats",
                    mimeType="application/json",
                    description="Statistiques du serveur"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Lit une ressource"""
            if uri == "reddit://stats":
                stats = self.index_manager.get_stats()
                return f"Statistiques Reddit:\n{stats}"
            return "Ressource non trouvée"
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """Liste tous les outils disponibles"""
            return [tool.get_definition() for tool in self.tools.values()]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> List[TextContent]:
            """Exécute un outil"""
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
    print(" MCP SERVER REDDIT")
    print("="*60 + "\n")
    
    server = RedditMCPServer()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n Arrêt du serveur Reddit")
    except Exception as e:
        print(f"\n Erreur fatale: {e}")
        raise