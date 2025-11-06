"""
Agent 5: Evaluator - Évalue les performances des modèles
Fichier: fl_crew_reddit/agents/evaluator_agent.py
"""

from crewai import Agent
from ..tools.model_tools import ModelTrainingTools
from ..config import FLCrewRedditConfig


class EvaluatorAgent:
    """Agent spécialisé dans l'évaluation des modèles"""
    
    def __init__(self, model_tools: ModelTrainingTools, llm_model: str = None):
        """
        Initialise l'agent Evaluator
        
        Args:
            model_tools: Outils d'évaluation de modèles
            llm_model: Modèle LLM à utiliser
        """
        self.model_tools = model_tools
        self.llm_model = llm_model or FLCrewRedditConfig.AGENT_LLM_MODEL
        
        self.agent = Agent(
            role="Evaluator Agent",
            goal="Évaluer les performances des modèles LLM locaux et agrégés pour mesurer la qualité du Federated Learning",
            backstory="""Tu es un expert en évaluation de modèles LLM. 
            Tu es responsable d'évaluer les performances des modèles LLM entraînés par les 
            agents et du modèle agrégé. Tu calcules des métriques adaptées aux LLMs comme 
            la perplexity, les scores BLEU/ROUGE pour la génération de texte, l'accuracy/F1 
            pour la classification, et les métriques multimodales (image-text alignment) 
            pour les données cross-modales. Tu fournis des rapports détaillés 
            sur la qualité des modèles et suggères des améliorations si nécessaire.
            Tu es le garant de la qualité dans le processus de Federated Learning avec LLMs.""",
            verbose=True,
            allow_delegation=False,
            tools=[
                model_tools.evaluate_model
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

