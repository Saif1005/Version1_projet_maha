"""
Agent: Profile Generator - Génère des profils Reddit à partir du modèle entraîné
Fichier: fl_crew_reddit/agents/profile_generator_agent.py
"""

from crewai import Agent
from ..tools.model_tools import ModelTrainingTools
from ..config import FLCrewRedditConfig


class ProfileGeneratorAgent:
    """Agent spécialisé dans la génération de profils Reddit à partir du modèle LLM entraîné"""
    
    def __init__(self, model_tools: ModelTrainingTools, llm_model: str = None):
        """
        Initialise l'agent Profile Generator
        
        Args:
            model_tools: Outils de génération de modèles
            llm_model: Modèle LLM à utiliser pour l'orchestration
        """
        self.model_tools = model_tools
        self.llm_model = llm_model or FLCrewRedditConfig.AGENT_LLM_MODEL
        
        self.agent = Agent(
            role="Profile Generator Agent",
            goal="Générer des profils Reddit complets et fragmentés à partir du modèle LLM entraîné",
            backstory="""Tu es un expert en génération de contenu avec des modèles LLM. 
            Tu utilises le modèle LLM entraîné sur les données Reddit pour générer des profils 
            Reddit réalistes et cohérents. Tu peux générer des profils complets (username, posts, 
            commentaires) ou des profils fragmentés pour le Federated Learning. Les profils générés 
            doivent être cohérents avec les données d'entraînement et réalistes. Tu es responsable 
            de créer des profils de qualité qui peuvent être utilisés pour tester ou compléter 
            le système de Federated Learning.""",
            verbose=True,
            allow_delegation=False,
            tools=[
                model_tools.generate_reddit_profile,
                model_tools.generate_fragmented_profile,
                model_tools.load_aggregated_model
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

