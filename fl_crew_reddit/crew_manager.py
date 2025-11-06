"""
Manager/Orchestrateur du FL Crew Reddit
Coordonne les 5 agents pour le Federated Learning
Fichier: fl_crew_reddit/crew_manager.py
"""

import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from crewai import Crew, Process, Task
from crewai.agent import Agent

from .config import FLCrewRedditConfig
from .mcp_client import RedditMCPClient
from .tools.mcp_tools import MCPRedditTools
from .tools.data_tools import DataProcessingTools
from .tools.model_tools import ModelTrainingTools
from .agents import (
    DataCollectorAgent,
    DataPreprocessorAgent,
    ModelTrainerAgent,
    AggregatorAgent,
    EvaluatorAgent,
    ProfileGeneratorAgent
)


class FLCrewRedditManager:
    """Manager pour orchestrer le FL Crew Reddit avec 5 agents"""
    
    def __init__(self, config: FLCrewRedditConfig = None):
        """
        Initialise le manager du FL Crew
        
        Args:
            config: Configuration du FL Crew (optionnel)
        """
        self.config = config or FLCrewRedditConfig()
        self.config.validate()
        
        # Initialiser les clients et outils
        self.mcp_client = RedditMCPClient()
        self.mcp_tools = MCPRedditTools(self.mcp_client)
        self.data_tools = DataProcessingTools(self.config.PREPROCESSED_DATA_DIR)
        self.model_tools = ModelTrainingTools(
            self.config.MODELS_DIR,
            base_model=self.config.BASE_LLM_MODEL
        )
        
        # Initialiser les agents
        self.data_collector = DataCollectorAgent(self.mcp_tools)
        self.data_preprocessor = DataPreprocessorAgent(self.data_tools)
        
        # Créer 3 agents Model Trainer (on peut en avoir plus si besoin)
        self.model_trainers = [
            ModelTrainerAgent(self.model_tools, agent_id=i+1)
            for i in range(3)  # 3 agents trainers pour avoir 5 agents au total
        ]
        
        self.aggregator = AggregatorAgent(self.model_tools)
        self.evaluator = EvaluatorAgent(self.model_tools)
        self.profile_generator = ProfileGeneratorAgent(self.model_tools)
        
        # Liste de tous les agents
        self.all_agents = [
            self.data_collector.get_agent(),
            self.data_preprocessor.get_agent(),
            *[trainer.get_agent() for trainer in self.model_trainers],
            self.aggregator.get_agent(),
            self.evaluator.get_agent()
        ]
        
        print(f" FL Crew Reddit Manager initialisé avec {len(self.all_agents)} agents")
    
    def create_collection_task(self) -> Task:
        """Crée la tâche de collecte de données"""
        return Task(
            description="""
            Collecte des données Reddit depuis le MCP Server pour le Federated Learning.
            
            Tu dois:
            1. Collecter des posts depuis plusieurs subreddits pertinents
            2. Collecter des commentaires associés
            3. Collecter des informations sur les utilisateurs
            4. Sauvegarder toutes les données collectées
            
            Subreddits suggérés: python, machinelearning, datascience, artificial, technology
            Limite par subreddit: 50-100 posts
            """,
            agent=self.data_collector.get_agent(),
            expected_output="Rapport JSON avec les données collectées: nombre de posts, commentaires, utilisateurs collectés"
        )
    
    def create_preprocessing_task(self) -> Task:
        """Crée la tâche de prétraitement"""
        return Task(
            description="""
            Prépare les données collectées pour l'entraînement.
            
            Tu dois:
            1. Nettoyer et normaliser les données
            2. Extraire les features pertinentes
            3. Diviser les données en ensembles d'entraînement et de test
            4. Préparer les données pour chaque agent trainer
            
            Assure-toi que les données sont bien structurées et prêtes pour l'entraînement.
            """,
            agent=self.data_preprocessor.get_agent(),
            expected_output="Rapport JSON avec les données préparées: nombre d'échantillons, features extraites, division train/test"
        )
    
    def create_training_task(self, agent_id: int) -> Task:
        """Crée une tâche d'entraînement LLM pour un agent"""
        trainer = self.model_trainers[agent_id - 1]
        return Task(
            description=f"""
            Entraîne un modèle LLM local avec fine-tuning (LoRA) pour l'agent {agent_id}.
            
            Tu dois:
            1. Charger les données d'entraînement multimodales préparées (texte, images)
            2. Entraîner un modèle LLM local avec fine-tuning LoRA sur {self.config.LOCAL_EPOCHS} époques
            3. Utiliser le modèle de base: {self.config.BASE_LLM_MODEL}
            4. Sauvegarder le modèle LoRA entraîné
            5. Fournir des métriques d'entraînement (perplexity, loss, etc.)
            
            Les données sont multimodales (texte + images), assure-toi de bien les traiter.
            Optimise les hyperparamètres LoRA si nécessaire (lora_r, learning_rate).
            """,
            agent=trainer.get_agent(),
            expected_output=f"Rapport JSON avec le modèle LLM entraîné de l'agent {agent_id}: chemin du modèle LoRA, métriques d'entraînement (perplexity, loss)"
        )
    
    def create_aggregation_task(self, round_number: int) -> Task:
        """Crée la tâche d'agrégation LLM"""
        return Task(
            description=f"""
            Agrège les modèles LLM locaux (LoRA) des agents en un modèle global pour le round {round_number}.
            
            Tu dois:
            1. Récupérer tous les modèles LoRA locaux entraînés par les agents
            2. Appliquer Federated Averaging sur les poids LoRA pour créer un modèle agrégé
            3. Méthode d'agrégation: {self.config.AGGREGATION_METHOD}
            4. Sauvegarder le modèle LoRA agrégé
            5. Préparer le modèle agrégé pour la distribution aux agents (pour le prochain round)
            
            Assure-toi que l'agrégation des poids LoRA est correcte et équitable.
            Le modèle de base reste: {self.config.BASE_LLM_MODEL}
            """,
            agent=self.aggregator.get_agent(),
            expected_output=f"Rapport JSON avec le modèle LLM agrégé du round {round_number}: chemin du modèle LoRA agrégé, nombre de modèles agrégés, métriques d'agrégation"
        )
    
    def create_evaluation_task(self, model_type: str = "aggregated") -> Task:
        """Crée la tâche d'évaluation LLM"""
        return Task(
            description=f"""
            Évalue les performances du modèle LLM {model_type}.
            
            Tu dois:
            1. Charger le modèle LLM à évaluer (LoRA ou agrégé)
            2. Charger les données de test multimodales
            3. Calculer les métriques LLM appropriées:
               - Perplexity (pour génération de texte)
               - BLEU/ROUGE scores (qualité de génération)
               - Accuracy/F1 (si classification)
               - Métriques multimodales (image-text alignment si applicable)
            4. Générer un rapport d'évaluation détaillé
            
            Les données sont multimodales, évalue aussi la performance cross-modale si applicable.
            Fournis des recommandations d'amélioration si nécessaire.
            """,
            agent=self.evaluator.get_agent(),
            expected_output="Rapport JSON avec les métriques d'évaluation LLM: perplexity, BLEU, ROUGE, accuracy, métriques multimodales, recommandations"
        )
    
    def run_federated_learning_round(self, round_number: int) -> Dict[str, Any]:
        """
        Exécute un round complet de Federated Learning
        
        Args:
            round_number: Numéro du round
            
        Returns:
            Résultats du round
        """
        print(f"\n{'='*60}")
        print(f" Round {round_number} de Federated Learning")
        print(f"{'='*60}\n")
        
        results = {
            "round": round_number,
            "timestamp": datetime.now().isoformat(),
            "status": "in_progress"
        }
        
        try:
            # 1. Collecte de données (seulement au premier round)
            if round_number == 1:
                print(" Étape 1: Collecte de données...")
                collection_task = self.create_collection_task()
                collection_crew = Crew(
                    agents=[self.data_collector.get_agent()],
                    tasks=[collection_task],
                    process=Process.sequential,
                    verbose=True
                )
                collection_result = collection_crew.kickoff()
                results["collection"] = str(collection_result)
            
            # 2. Prétraitement (seulement au premier round)
            if round_number == 1:
                print("\n Étape 2: Prétraitement des données...")
                preprocessing_task = self.create_preprocessing_task()
                preprocessing_crew = Crew(
                    agents=[self.data_preprocessor.get_agent()],
                    tasks=[preprocessing_task],
                    process=Process.sequential,
                    verbose=True
                )
                preprocessing_result = preprocessing_crew.kickoff()
                results["preprocessing"] = str(preprocessing_result)
            
            # 3. Entraînement local (chaque round)
            print(f"\n Étape 3: Entraînement local des agents...")
            training_tasks = [
                self.create_training_task(agent_id=i+1)
                for i in range(len(self.model_trainers))
            ]
            
            training_crew = Crew(
                agents=[trainer.get_agent() for trainer in self.model_trainers],
                tasks=training_tasks,
                process=Process.sequential,
                verbose=True
            )
            training_result = training_crew.kickoff()
            results["training"] = str(training_result)
            
            # 4. Agrégation (chaque round)
            print(f"\n Étape 4: Agrégation des modèles...")
            aggregation_task = self.create_aggregation_task(round_number)
            aggregation_crew = Crew(
                agents=[self.aggregator.get_agent()],
                tasks=[aggregation_task],
                process=Process.sequential,
                verbose=True
            )
            aggregation_result = aggregation_crew.kickoff()
            results["aggregation"] = str(aggregation_result)
            
            # 5. Évaluation (chaque round)
            print(f"\n Étape 5: Évaluation du modèle...")
            evaluation_task = self.create_evaluation_task("aggregated")
            evaluation_crew = Crew(
                agents=[self.evaluator.get_agent()],
                tasks=[evaluation_task],
                process=Process.sequential,
                verbose=True
            )
            evaluation_result = evaluation_crew.kickoff()
            results["evaluation"] = str(evaluation_result)
            
            results["status"] = "completed"
            print(f"\n Round {round_number} terminé avec succès!")
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            print(f"\n Erreur lors du round {round_number}: {e}")
        
        return results
    
    def run_federated_learning(self, num_rounds: int = None) -> Dict[str, Any]:
        """
        Exécute le processus complet de Federated Learning
        
        Args:
            num_rounds: Nombre de rounds (par défaut depuis la config)
            
        Returns:
            Résultats complets du processus
        """
        num_rounds = num_rounds or self.config.FEDERATION_ROUNDS
        
        print("\n" + "="*60)
        print(" DÉMARRAGE DU FEDERATED LEARNING - FL CREW REDDIT")
        print("="*60)
        print(f" Configuration:")
        print(f"   - Nombre d'agents: {len(self.all_agents)}")
        print(f"   - Nombre de rounds: {num_rounds}")
        print(f"   - Modèle de base LLM: {self.config.BASE_LLM_MODEL}")
        print(f"   - Fine-tuning: LoRA (r={self.config.LORA_R})")
        print(f"   - Époques locales: {self.config.LOCAL_EPOCHS}")
        print(f"   - Batch size: {self.config.BATCH_SIZE}")
        print(f"   - Learning rate: {self.config.LEARNING_RATE}")
        print(f"   - Données multimodales: {self.config.SUPPORT_MULTIMODAL}")
        print(f"   - Méthode d'agrégation: {self.config.AGGREGATION_METHOD}")
        print("="*60 + "\n")
        
        all_results = {
            "start_time": datetime.now().isoformat(),
            "config": {
                "num_agents": len(self.all_agents),
                "num_rounds": num_rounds,
                "base_llm_model": self.config.BASE_LLM_MODEL,
                "use_lora": self.config.USE_LORA,
                "lora_r": self.config.LORA_R,
                "local_epochs": self.config.LOCAL_EPOCHS,
                "batch_size": self.config.BATCH_SIZE,
                "learning_rate": self.config.LEARNING_RATE,
                "support_multimodal": self.config.SUPPORT_MULTIMODAL,
                "aggregation_method": self.config.AGGREGATION_METHOD
            },
            "rounds": []
        }
        
        for round_num in range(1, num_rounds + 1):
            round_results = self.run_federated_learning_round(round_num)
            all_results["rounds"].append(round_results)
            
            # Sauvegarder les résultats après chaque round
            self._save_results(all_results, round_num)
        
        all_results["end_time"] = datetime.now().isoformat()
        all_results["status"] = "completed"
        
        # Sauvegarder les résultats finaux
        self._save_results(all_results, "final")
        
        print("\n" + "="*60)
        print(" FEDERATED LEARNING TERMINÉ!")
        print("="*60)
        print(f"{num_rounds} rounds complétés")
        print(f" Résultats sauvegardés dans: {self.config.RESULTS_DIR}")
        print("="*60 + "\n")
        
        return all_results
    
    def _save_results(self, results: Dict[str, Any], identifier: str):
        """Sauvegarde les résultats dans un fichier JSON"""
        results_file = self.config.RESULTS_DIR / f"fl_results_{identifier}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f" Résultats sauvegardés: {results_file}")
    
    def generate_profiles_from_model(self, round_number: int = None, 
                                    num_profiles: int = 1,
                                    num_fragments: int = 5,
                                    fragment_type: str = "mixed") -> Dict[str, Any]:
        """
        Génère des profils Reddit à partir du modèle entraîné
        
        Args:
            round_number: Numéro du round (utilise le dernier round si None)
            num_profiles: Nombre de profils à générer
            num_fragments: Nombre de fragments par profil (pour profils fragmentés)
            fragment_type: Type de fragments ("posts", "comments", "mixed")
            
        Returns:
            Résultats de la génération de profils
        """
        print("\n" + "="*60)
        print(" GÉNÉRATION DE PROFILS REDDIT")
        print("="*60)
        
        # Trouver le dernier round si non spécifié
        if round_number is None:
            aggregated_dir = self.config.AGGREGATED_MODELS_DIR
            rounds = []
            for path in aggregated_dir.glob("aggregated_lora_model_round_*"):
                try:
                    round_num = int(path.name.split("_")[-1])
                    rounds.append(round_num)
                except:
                    pass
            round_number = max(rounds) if rounds else 1
            print(f" Utilisation du modèle du round {round_number}")
        
        model_path = self.config.AGGREGATED_MODELS_DIR / f"aggregated_lora_model_round_{round_number}"
        
        if not model_path.exists():
            print(f" Modèle du round {round_number} non trouvé: {model_path}")
            return {"status": "error", "message": f"Modèle non trouvé: {model_path}"}
        
        print(f" Modèle utilisé: {model_path}")
        print(f" Génération de {num_profiles} profil(s)")
        print("="*60 + "\n")
        
        from crewai import Crew, Process, Task
        
        all_generated_profiles = []
        
        for i in range(num_profiles):
            print(f" Génération du profil {i+1}/{num_profiles}...")
            
            # Créer la tâche de génération
            generation_task = Task(
                description=f"""
                Génère un profil Reddit complet et fragmenté à partir du modèle entraîné.
                
                Tu dois:
                1. Charger le modèle agrégé du round {round_number}
                2. Générer un profil Reddit complet avec posts et commentaires
                3. Fragmenter le profil en {num_fragments} fragments pour distribution
                4. Sauvegarder le profil complet et les fragments
                
                Le profil doit être réaliste et cohérent avec les données d'entraînement Reddit.
                Type de fragments: {fragment_type}
                """,
                agent=self.profile_generator.get_agent(),
                expected_output=f"Profil Reddit généré et fragmenté en {num_fragments} fragments, sauvegardé avec succès"
            )
            
            # Exécuter la génération
            generation_crew = Crew(
                agents=[self.profile_generator.get_agent()],
                tasks=[generation_task],
                process=Process.sequential,
                verbose=True
            )
            
            try:
                result = generation_crew.kickoff()
                all_generated_profiles.append({
                    "profile_number": i + 1,
                    "result": str(result),
                    "status": "success"
                })
                print(f" Profil {i+1} généré avec succès\n")
            except Exception as e:
                all_generated_profiles.append({
                    "profile_number": i + 1,
                    "status": "error",
                    "error": str(e)
                })
                print(f" Erreur lors de la génération du profil {i+1}: {e}\n")
        
        results = {
            "round_number": round_number,
            "model_path": str(model_path),
            "num_profiles": num_profiles,
            "num_fragments": num_fragments,
            "fragment_type": fragment_type,
            "generated_profiles": all_generated_profiles,
            "timestamp": datetime.now().isoformat()
        }
        
        # Sauvegarder les résultats
        results_file = self.config.RESULTS_DIR / f"generated_profiles_round_{round_number}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("="*60)
        print(" GÉNÉRATION DE PROFILS TERMINÉE")
        print("="*60)
        print(f" Profils sauvegardés dans: {self.config.DATA_DIR / 'generated_profiles'}")
        print(f" Fragments sauvegardés dans: {self.config.DATA_DIR / 'fragmented_profiles'}")
        print(f" Résultats: {results_file}")
        print("="*60 + "\n")
        
        return results

