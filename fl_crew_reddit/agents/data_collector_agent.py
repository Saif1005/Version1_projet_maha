"""
Agent 1: Data Collector - Collecte les données depuis Reddit
Fichier: fl_crew_reddit/agents/data_collector_agent.py
"""

from crewai import Agent
from typing import List
from ..tools.mcp_tools import MCPRedditTools
from ..config import FLCrewRedditConfig


class DataCollectorAgent:
    """Agent spécialisé dans la collecte de données Reddit"""
    
    def __init__(self, mcp_tools: MCPRedditTools, llm_model: str = None):
        """
        Initialise l'agent Data Collector
        
        Args:
            mcp_tools: Outils MCP pour interagir avec le serveur Reddit
            llm_model: Modèle LLM à utiliser
        """
        self.mcp_tools = mcp_tools
        self.llm_model = llm_model or FLCrewRedditConfig.AGENT_LLM_MODEL
        
        self.agent = Agent(
            role="Data Collector Agent",
            goal="Collecter efficacement les données Reddit depuis le MCP Server pour le Federated Learning",
            backstory="""Tu es un expert en collecte de données Reddit. 
            Tu es responsable de récupérer les données nécessaires depuis le MCP Server Reddit 
            en utilisant les outils disponibles. Tu dois collecter des données variées et 
            représentatives pour permettre un bon entraînement des modèles de Federated Learning.
            Tu travailles en collaboration avec les autres agents du FL Crew.""",
            verbose=True,
            allow_delegation=False,
            tools=[
                mcp_tools.collect_subreddit_posts,
                mcp_tools.search_reddit_posts,
                mcp_tools.collect_post_comments,
                mcp_tools.collect_user_data,
                mcp_tools.collect_subreddit_info
            ],
            llm=self._get_llm()
        )
    
    def _get_llm(self):
        """Retourne le LLM configuré"""
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model_name=self.llm_model,
                temperature=FLCrewRedditConfig.AGENT_TEMPERATURE
            )
        except ImportError:
            # Fallback si langchain_openai n'est pas disponible
            return None
    
    def get_agent(self) -> Agent:
        """Retourne l'agent CrewAI"""
        return self.agent

