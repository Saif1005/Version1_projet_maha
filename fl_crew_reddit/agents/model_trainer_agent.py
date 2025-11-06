"""
Agent 3: Model Trainer - Entraîne les modèles locaux
Fichier: fl_crew_reddit/agents/model_trainer_agent.py
"""

from crewai import Agent
from ..tools.model_tools import ModelTrainingTools
from ..config import FLCrewRedditConfig


class ModelTrainerAgent:
    """Agent spécialisé dans l'entraînement de modèles locaux"""
    
    def __init__(self, model_tools: ModelTrainingTools, agent_id: int, llm_model: str = None):
        """
        Initialise l'agent Model Trainer
        
        Args:
            model_tools: Outils d'entraînement de modèles
            agent_id: ID de l'agent (1-5)
            llm_model: Modèle LLM à utiliser
        """
        self.model_tools = model_tools
        self.agent_id = agent_id
        self.llm_model = llm_model or FLCrewRedditConfig.AGENT_LLM_MODEL
        
        self.agent = Agent(
            role=f"Model Trainer Agent {agent_id}",
            goal=f"Entraîner un modèle LLM local avec fine-tuning LoRA pour l'agent {agent_id} en utilisant les données multimodales préparées",
            backstory=f"""Tu es un expert en entraînement de modèles LLM avec fine-tuning. 
            Tu es l'agent {agent_id} du FL Crew Reddit et tu es responsable d'entraîner 
            un modèle LLM local avec fine-tuning LoRA sur les données multimodales (texte, images) 
            qui t'ont été assignées. Tu dois optimiser les hyperparamètres LoRA (lora_r, learning_rate), 
            surveiller l'entraînement (perplexity, loss) et produire un modèle LoRA performant 
            qui sera ensuite agrégé avec les modèles des autres agents dans le processus 
            de Federated Learning. Les données sont multimodales, assure-toi de bien les traiter.""",
            verbose=True,
            allow_delegation=False,
            tools=[
                model_tools.train_local_model,
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

