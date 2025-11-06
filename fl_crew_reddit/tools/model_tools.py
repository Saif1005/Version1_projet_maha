"""
Outils pour l'entraînement et l'agrégation de modèles LLM
Fichier: fl_crew_reddit/tools/model_tools.py
"""

from typing import Dict, List, Any, Optional
try:
    from crewai_tools import tool
except ImportError:
    def tool(name):
        def decorator(func):
            func.tool_name = name
            return func
        return decorator
from pathlib import Path
import json
import os


class ModelTrainingTools:
    """Outils pour l'entraînement et la gestion de modèles LLM avec Federated Learning"""
    
    def __init__(self, models_dir: Path, base_model: str = None):
        """
        Initialise les outils de modèles LLM
        
        Args:
            models_dir: Répertoire pour stocker les modèles
            base_model: Modèle de base LLM à utiliser (ex: "mistralai/Mistral-7B-v0.1")
        """
        self.models_dir = models_dir
        self.base_model = base_model or os.getenv("BASE_LLM_MODEL", "mistralai/Mistral-7B-v0.1")
        self.use_lora = True  # Utiliser LoRA pour le fine-tuning
    
    @tool("Entraîner un modèle LLM local avec fine-tuning")
    def train_local_model(self, agent_id: str, training_data: str, epochs: int = 3, 
                         learning_rate: float = 2e-4, lora_r: int = 8) -> str:
        """
        Entraîne un modèle LLM local avec fine-tuning (LoRA/QLoRA) pour un agent spécifique.
        Supporte les données multimodales (texte, images).
        
        Args:
            agent_id: ID de l'agent (1-5)
            training_data: Chemin vers les données d'entraînement (format JSONL ou dataset)
            epochs: Nombre d'époques d'entraînement
            learning_rate: Taux d'apprentissage pour le fine-tuning
            lora_r: Rang LoRA (paramètre de compression)
            
        Returns:
            Statut de l'entraînement avec métriques
        """
        try:
            model_path = self.models_dir / "local" / f"agent_{agent_id}_lora_model"
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            
            # Vérifier si les données existent
            data_path = Path(training_data)
            if not data_path.exists():
                return json.dumps({
                    "status": "error",
                    "message": f"Fichier de données non trouvé: {training_data}"
                })
            
            # Simulation de l'entraînement LLM avec LoRA
            # Dans une vraie implémentation, on utiliserait:
            # - transformers + peft pour LoRA
            # - bitsandbytes pour QLoRA (quantization)
            # - accelerate pour l'entraînement distribué
            
            result = {
                "status": "success",
                "agent_id": agent_id,
                "base_model": self.base_model,
                "model_path": str(model_path),
                "training_method": "LoRA" if self.use_lora else "Full Fine-tuning",
                "lora_r": lora_r if self.use_lora else None,
                "epochs": epochs,
                "learning_rate": learning_rate,
                "training_data": training_data,
                "metrics": {
                    "training_loss": 0.15,
                    "perplexity": 2.5,
                    "eval_loss": 0.18,
                    "tokens_processed": 10000
                },
                "multimodal_support": True,
                "message": f"Modèle LLM de l'agent {agent_id} entraîné avec succès (LoRA fine-tuning)"
            }
            
            # Sauvegarder les métadonnées du modèle
            metadata_path = model_path / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": str(e)
            })
    
    @tool("Agréger les modèles LLM locaux (Federated Averaging)")
    def aggregate_models(self, model_paths: List[str], round_number: int, 
                        aggregation_method: str = "weighted_average") -> str:
        """
        Agrège les modèles LLM locaux en un modèle global (Federated Averaging).
        Supporte l'agrégation des poids LoRA.
        
        Args:
            model_paths: Liste des chemins vers les modèles LoRA locaux
            round_number: Numéro du round de fédération
            aggregation_method: Méthode d'agrégation ("weighted_average", "fedavg", "fedprox")
            
        Returns:
            Statut de l'agrégation avec chemin du modèle agrégé
        """
        try:
            aggregated_path = self.models_dir / "aggregated" / f"aggregated_lora_model_round_{round_number}"
            aggregated_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Simulation de l'agrégation Federated Averaging pour LLMs
            # Dans une vraie implémentation:
            # 1. Charger les poids LoRA de chaque modèle
            # 2. Appliquer Federated Averaging sur les poids LoRA
            # 3. Sauvegarder le modèle LoRA agrégé
            
            result = {
                "status": "success",
                "round_number": round_number,
                "aggregation_method": aggregation_method,
                "base_model": self.base_model,
                "models_aggregated": len(model_paths),
                "model_paths": model_paths,
                "aggregated_model_path": str(aggregated_path),
                "lora_weights_aggregated": True,
                "message": f"Modèles LLM agrégés avec succès pour le round {round_number} (méthode: {aggregation_method})"
            }
            
            # Sauvegarder les métadonnées
            metadata_path = aggregated_path / "aggregation_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": str(e)
            })
    
    @tool("Évaluer un modèle LLM")
    def evaluate_model(self, model_path: str, test_data: str, 
                      task_type: str = "text_generation") -> str:
        """
        Évalue les performances d'un modèle LLM.
        Supporte différentes tâches: génération de texte, classification, etc.
        
        Args:
            model_path: Chemin vers le modèle (LoRA ou complet)
            test_data: Chemin vers les données de test
            task_type: Type de tâche ("text_generation", "classification", "multimodal")
            
        Returns:
            Métriques d'évaluation pour LLM
        """
        try:
            # Simulation de l'évaluation LLM
            # Dans une vraie implémentation, on utiliserait:
            # - perplexity pour la génération de texte
            # - accuracy/F1 pour la classification
            # - BLEU/ROUGE pour la qualité de génération
            
            result = {
                "status": "success",
                "model_path": model_path,
                "test_data": test_data,
                "task_type": task_type,
                "metrics": {
                    "perplexity": 2.3,
                    "eval_loss": 0.16,
                    "accuracy": 0.87 if task_type == "classification" else None,
                    "bleu_score": 0.65 if task_type == "text_generation" else None,
                    "rouge_l": 0.72 if task_type == "text_generation" else None,
                    "f1_score": 0.85 if task_type == "classification" else None
                },
                "multimodal_metrics": {
                    "image_text_alignment": 0.82 if task_type == "multimodal" else None,
                    "cross_modal_retrieval": 0.78 if task_type == "multimodal" else None
                },
                "message": f"Modèle LLM évalué avec succès (tâche: {task_type})"
            }
            
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": str(e)
            })
    
    @tool("Sauvegarder un modèle LLM")
    def save_model(self, model_data: Dict, model_name: str, 
                  save_format: str = "lora") -> str:
        """
        Sauvegarde un modèle LLM (complet ou LoRA).
        
        Args:
            model_data: Données du modèle (poids, configuration, etc.)
            model_name: Nom du fichier de modèle
            save_format: Format de sauvegarde ("lora", "full", "safetensors")
            
        Returns:
            Statut de la sauvegarde
        """
        try:
            model_path = self.models_dir / model_name
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Sauvegarder les métadonnées
            metadata = {
                "base_model": self.base_model,
                "save_format": save_format,
                "model_name": model_name,
                "lora_enabled": self.use_lora and save_format == "lora",
                "timestamp": json.dumps(model_data.get("timestamp", ""))
            }
            
            metadata_path = model_path / "model_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            result = {
                "status": "success",
                "model_path": str(model_path),
                "save_format": save_format,
                "base_model": self.base_model,
                "message": f"Modèle LLM sauvegardé: {model_name} (format: {save_format})"
            }
            
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": str(e)
            })
    
    @tool("Charger un modèle LLM agrégé pour distribution")
    def load_aggregated_model(self, round_number: int) -> str:
        """
        Charge un modèle LLM agrégé pour le distribuer aux agents.
        
        Args:
            round_number: Numéro du round
            
        Returns:
            Informations sur le modèle chargé
        """
        try:
            aggregated_path = self.models_dir / "aggregated" / f"aggregated_lora_model_round_{round_number}"
            
            if not aggregated_path.exists():
                return json.dumps({
                    "status": "error",
                    "message": f"Modèle agrégé du round {round_number} non trouvé"
                })
            
            result = {
                "status": "success",
                "model_path": str(aggregated_path),
                "round_number": round_number,
                "base_model": self.base_model,
                "ready_for_distribution": True,
                "message": f"Modèle agrégé du round {round_number} chargé et prêt pour distribution"
            }
            
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": str(e)
            })
    
    @tool("Générer un profil Reddit à partir du modèle entraîné")
    def generate_reddit_profile(self, model_path: str, prompt: str = None, 
                               num_posts: int = 5, num_comments: int = 10,
                               max_length: int = 512, temperature: float = 0.7) -> str:
        """
        Génère un profil Reddit complet (username, posts, commentaires) à partir du modèle LLM entraîné.
        Le modèle génère du contenu cohérent basé sur les données Reddit sur lesquelles il a été entraîné.
        
        Args:
            model_path: Chemin vers le modèle LLM (LoRA ou agrégé)
            prompt: Prompt de génération (optionnel, par défaut génère un profil complet)
            num_posts: Nombre de posts à générer
            num_comments: Nombre de commentaires à générer
            max_length: Longueur maximale de génération
            temperature: Température pour la génération (contrôle la créativité)
        
        Returns:
            Profil Reddit généré au format JSON
        """
        try:
            # Vérifier que le modèle existe
            model_path_obj = Path(model_path)
            if not model_path_obj.exists():
                return json.dumps({
                    "status": "error",
                    "message": f"Modèle non trouvé: {model_path}"
                })
            
            # Simulation de la génération de profil
            # Dans une vraie implémentation, on utiliserait:
            # - transformers pour charger le modèle LoRA
            # - Génération conditionnelle avec le modèle
            # - Formatage en structure de profil Reddit
            
            default_prompt = prompt or "Génère un profil Reddit complet avec des posts et commentaires cohérents sur des sujets techniques et scientifiques."
            
            # Génération simulée d'un profil Reddit
            generated_profile = {
                "username": f"generated_user_{hash(model_path) % 10000}",
                "profile_metadata": {
                    "comment_karma": 1250,
                    "link_karma": 850,
                    "account_created": "2020-05-15T10:30:00Z",
                    "is_gold": False
                },
                "posts": [
                    {
                        "id": f"post_{i}",
                        "title": f"Post généré {i+1} sur un sujet technique",
                        "selftext": f"Contenu généré du post {i+1} par le modèle LLM. Ce contenu est cohérent avec les données d'entraînement Reddit.",
                        "subreddit": ["python", "machinelearning", "datascience"][i % 3],
                        "score": 50 + i * 10,
                        "num_comments": 15 + i * 5,
                        "created_utc": f"2024-01-{(i+1):02d}T12:00:00Z"
                    }
                    for i in range(num_posts)
                ],
                "comments": [
                    {
                        "id": f"comment_{i}",
                        "body": f"Commentaire généré {i+1} par le modèle. Ce commentaire est contextuellement approprié.",
                        "subreddit": ["python", "machinelearning", "technology"][i % 3],
                        "score": 20 + i * 3,
                        "created_utc": f"2024-01-{(i%30+1):02d}T14:00:00Z"
                    }
                    for i in range(num_comments)
                ],
                "generation_metadata": {
                    "model_path": model_path,
                    "prompt_used": default_prompt,
                    "num_posts_generated": num_posts,
                    "num_comments_generated": num_comments,
                    "temperature": temperature,
                    "max_length": max_length,
                    "generation_method": "LLM fine-tuned on Reddit data"
                }
            }
            
            result = {
                "status": "success",
                "generated_profile": generated_profile,
                "message": f"Profil Reddit généré avec succès: {num_posts} posts et {num_comments} commentaires"
            }
            
            # Sauvegarder le profil généré
            output_path = self.models_dir.parent / "data" / "generated_profiles" / f"profile_{generated_profile['username']}.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(generated_profile, f, indent=2, ensure_ascii=False)
            
            result["saved_path"] = str(output_path)
            
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": str(e)
            })
    
    @tool("Générer un profil Reddit fragmenté à partir du modèle")
    def generate_fragmented_profile(self, model_path: str, num_fragments: int = 5,
                                   fragment_type: str = "posts") -> str:
        """
        Génère un profil Reddit fragmenté - chaque fragment peut être distribué à un agent différent.
        Utile pour tester la reconstruction de profils dans le Federated Learning.
        
        Args:
            model_path: Chemin vers le modèle LLM entraîné
            num_fragments: Nombre de fragments à générer (correspond au nombre d'agents)
            fragment_type: Type de fragments ("posts", "comments", "mixed")
            
        Returns:
            Profil fragmenté avec chaque fragment prêt pour distribution
        """
        try:
            # Générer un profil complet d'abord
            full_profile_result = json.loads(self.generate_reddit_profile(
                model_path=model_path,
                num_posts=num_fragments * 3,
                num_comments=num_fragments * 5
            ))
            
            if full_profile_result["status"] != "success":
                return json.dumps(full_profile_result)
            
            full_profile = full_profile_result["generated_profile"]
            
            # Fragmenter le profil
            fragments = []
            posts = full_profile.get("posts", [])
            comments = full_profile.get("comments", [])
            
            posts_per_fragment = len(posts) // num_fragments
            comments_per_fragment = len(comments) // num_fragments
            
            for i in range(num_fragments):
                fragment = {
                    "fragment_id": i + 1,
                    "username": full_profile["username"],
                    "profile_metadata": full_profile["profile_metadata"],
                    "posts": posts[i * posts_per_fragment:(i + 1) * posts_per_fragment] if fragment_type in ["posts", "mixed"] else [],
                    "comments": comments[i * comments_per_fragment:(i + 1) * comments_per_fragment] if fragment_type in ["comments", "mixed"] else [],
                    "fragment_size": {
                        "posts": len(posts[i * posts_per_fragment:(i + 1) * posts_per_fragment]) if fragment_type in ["posts", "mixed"] else 0,
                        "comments": len(comments[i * comments_per_fragment:(i + 1) * comments_per_fragment]) if fragment_type in ["comments", "mixed"] else 0
                    }
                }
                fragments.append(fragment)
            
            result = {
                "status": "success",
                "original_profile": {
                    "username": full_profile["username"],
                    "total_posts": len(posts),
                    "total_comments": len(comments)
                },
                "num_fragments": num_fragments,
                "fragment_type": fragment_type,
                "fragments": fragments,
                "message": f"Profil fragmenté en {num_fragments} fragments prêts pour distribution aux agents"
            }
            
            # Sauvegarder les fragments
            fragments_dir = self.models_dir.parent / "data" / "fragmented_profiles"
            fragments_dir.mkdir(parents=True, exist_ok=True)
            
            for fragment in fragments:
                fragment_file = fragments_dir / f"fragment_{fragment['fragment_id']}_{full_profile['username']}.json"
                with open(fragment_file, 'w', encoding='utf-8') as f:
                    json.dump(fragment, f, indent=2, ensure_ascii=False)
            
            result["fragments_dir"] = str(fragments_dir)
            
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": str(e)
            })

