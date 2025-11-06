"""
Outils pour interagir avec le MCP Server Reddit
Fichier: fl_crew_reddit/tools/mcp_tools.py
"""

from typing import Dict, Any, List
try:
    from crewai_tools import tool
except ImportError:
    # Fallback si crewai_tools n'est pas disponible
    def tool(name):
        def decorator(func):
            func.tool_name = name
            return func
        return decorator
from ..mcp_client import RedditMCPClient


class MCPRedditTools:
    """Outils pour interagir avec le MCP Server Reddit"""
    
    def __init__(self, mcp_client: RedditMCPClient):
        self.mcp_client = mcp_client
    
    @tool("Collecter les posts d'un subreddit")
    def collect_subreddit_posts(self, subreddit: str, sort: str = "hot", limit: int = 25, time_filter: str = "day") -> str:
        """
        Collecte les posts d'un subreddit spécifique via le MCP Server Reddit.
        
        Args:
            subreddit: Nom du subreddit (sans le 'r/')
            sort: Méthode de tri (hot, new, top, rising)
            limit: Nombre de posts à collecter
            time_filter: Filtre temporel (hour, day, week, month, year, all)
            
        Returns:
            Résultat de la collecte au format JSON
        """
        import asyncio
        import json
        
        result = asyncio.run(self.mcp_client.call_tool(
            "collect_subreddit_posts",
            {
                "subreddit": subreddit,
                "sort": sort,
                "limit": limit,
                "time_filter": time_filter
            }
        ))
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    @tool("Rechercher des posts Reddit")
    def search_reddit_posts(self, query: str, subreddit: str = None, sort: str = "relevance", limit: int = 10) -> str:
        """
        Recherche des posts Reddit via le MCP Server.
        
        Args:
            query: Terme de recherche
            subreddit: Subreddit spécifique (optionnel)
            sort: Méthode de tri
            limit: Nombre de résultats
            
        Returns:
            Résultats de la recherche au format JSON
        """
        import asyncio
        import json
        
        args = {"query": query, "sort": sort, "limit": limit}
        if subreddit:
            args["subreddit"] = subreddit
        
        result = asyncio.run(self.mcp_client.call_tool("search_reddit_posts", args))
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    @tool("Collecter les commentaires d'un post")
    def collect_post_comments(self, post_id: str, limit: int = 100) -> str:
        """
        Collecte les commentaires d'un post Reddit.
        
        Args:
            post_id: ID du post Reddit
            limit: Nombre de commentaires à collecter
            
        Returns:
            Commentaires collectés au format JSON
        """
        import asyncio
        import json
        
        result = asyncio.run(self.mcp_client.call_tool(
            "collect_post_comments",
            {"post_id": post_id, "limit": limit}
        ))
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    @tool("Collecter les données d'un utilisateur")
    def collect_user_data(self, username: str, limit: int = 100) -> str:
        """
        Collecte les données d'un utilisateur Reddit.
        
        Args:
            username: Nom d'utilisateur Reddit
            limit: Nombre de posts à collecter
            
        Returns:
            Données utilisateur au format JSON
        """
        import asyncio
        import json
        
        result = asyncio.run(self.mcp_client.call_tool(
            "collect_user_data",
            {"username": username, "limit": limit}
        ))
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    @tool("Collecter les informations d'un subreddit")
    def collect_subreddit_info(self, subreddit: str) -> str:
        """
        Collecte les informations générales d'un subreddit.
        
        Args:
            subreddit: Nom du subreddit
            
        Returns:
            Informations du subreddit au format JSON
        """
        import asyncio
        import json
        
        result = asyncio.run(self.mcp_client.call_tool(
            "collect_subreddit_info",
            {"subreddit": subreddit}
        ))
        
        return json.dumps(result, indent=2, ensure_ascii=False)

