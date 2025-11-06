"""
Script utilitaire pour générer des profils Reddit à partir du modèle entraîné
Fichier: fl_crew_reddit/generate_profiles.py
"""

import sys
import argparse
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fl_crew_reddit.config import FLCrewRedditConfig
from fl_crew_reddit.crew_manager import FLCrewRedditManager


def main():
    """Point d'entrée principal pour la génération de profils"""
    parser = argparse.ArgumentParser(
        description="Génère des profils Reddit à partir du modèle LLM entraîné"
    )
    parser.add_argument(
        "--round",
        type=int,
        default=None,
        help="Numéro du round à utiliser (utilise le dernier si non spécifié)"
    )
    parser.add_argument(
        "--num-profiles",
        type=int,
        default=1,
        help="Nombre de profils à générer (défaut: 1)"
    )
    parser.add_argument(
        "--num-fragments",
        type=int,
        default=5,
        help="Nombre de fragments par profil (défaut: 5)"
    )
    parser.add_argument(
        "--fragment-type",
        type=str,
        default="mixed",
        choices=["posts", "comments", "mixed"],
        help="Type de fragments (défaut: mixed)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print(" GÉNÉRATION DE PROFILS REDDIT")
    print("="*60)
    print(f" Paramètres:")
    print(f"   - Round: {args.round or 'Dernier disponible'}")
    print(f"   - Nombre de profils: {args.num_profiles}")
    print(f"   - Fragments par profil: {args.num_fragments}")
    print(f"   - Type de fragments: {args.fragment_type}")
    print("="*60 + "\n")
    
    try:
        # Initialiser la configuration
        config = FLCrewRedditConfig()
        config.validate()
        
        # Créer le manager
        manager = FLCrewRedditManager(config)
        
        # Générer les profils
        results = manager.generate_profiles_from_model(
            round_number=args.round,
            num_profiles=args.num_profiles,
            num_fragments=args.num_fragments,
            fragment_type=args.fragment_type
        )
    
        print("\n Génération terminée avec succès!")
        return results
        
    except KeyboardInterrupt:
        print("\n\n  Génération interrompue par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

