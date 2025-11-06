"""
Agent 4: Aggregator - Agrège les modèles locaux
Fichier: fl_crew_reddit/agents/aggregator_agent.py
"""

from crewai import Agent
from ..tools.model_tools import ModelTrainingTools
from ..config import FLCrewRedditConfig


class AggregatorAgent:
    """Agent spécialisé dans l'agrégation des modèles (Federated Averaging)"""
    
    def __init__(self, model_tools: ModelTrainingTools, llm_model: str = None):
        """
        Initialise l'agent Aggregator
        
        Args:
            model_tools: Outils d'agrégation de modèles
            llm_model: Modèle LLM à utiliser
        """
        self.model_tools = model_tools
        self.llm_model = llm_model or FLCrewRedditConfig.AGENT_LLM_MODEL
        
        self.agent = Agent(
            role="Aggregator Agent",
            goal="Agréger les modèles LLM locaux (poids LoRA) des différents agents en un modèle global optimisé",
            backstory="""Tu es un expert en Federated Learning et en agrégation de modèles LLM. 
            Tu reçois les modèles LoRA locaux entraînés par les différents agents du FL Crew 
            et tu agrèges les poids LoRA en utilisant des techniques comme Federated Averaging. 
            Tu es responsable de créer un modèle LoRA global qui combine les connaissances 
            de tous les agents tout en préservant la confidentialité des données locales.
            Tu coordonnes le processus de fédération à chaque round en agrégeant uniquement 
            les poids LoRA (beaucoup plus légers que le modèle complet).""",
            verbose=True,
            allow_delegation=False,
            tools=[
                model_tools.aggregate_models,
                model_tools.save_model
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
            return None
    
    def get_agent(self) -> Agent:
        """Retourne l'agent CrewAI"""
        return self.agent

