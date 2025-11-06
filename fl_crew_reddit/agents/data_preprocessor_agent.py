"""
Agent 2: Data Preprocessor - Prépare et nettoie les données
Fichier: fl_crew_reddit/agents/data_preprocessor_agent.py
"""

from crewai import Agent
from ..tools.data_tools import DataProcessingTools
from ..config import FLCrewRedditConfig


class DataPreprocessorAgent:
    """Agent spécialisé dans le prétraitement des données"""
    
    def __init__(self, data_tools: DataProcessingTools, llm_model: str = None):
        """
        Initialise l'agent Data Preprocessor
        
        Args:
            data_tools: Outils de traitement de données
            llm_model: Modèle LLM à utiliser
        """
        self.data_tools = data_tools
        self.llm_model = llm_model or FLCrewRedditConfig.AGENT_LLM_MODEL
        
        self.agent = Agent(
            role="Data Preprocessor Agent",
            goal="Préparer et nettoyer les données collectées pour l'entraînement des modèles",
            backstory="""Tu es un expert en prétraitement de données. 
            Tu reçois les données brutes collectées par le Data Collector Agent et tu les 
            prépares pour l'entraînement. Tu nettoies, normalises, extrais les features 
            et structures les données de manière optimale pour le Federated Learning.
            Tu dois t'assurer que les données sont de qualité et prêtes pour l'entraînement.""",
            verbose=True,
            allow_delegation=False,
            tools=[
                data_tools.prepare_training_data,
                data_tools.split_data,
                data_tools.extract_features
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

