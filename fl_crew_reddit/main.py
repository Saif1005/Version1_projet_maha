"""
Point d'entrée principal du FL Crew Reddit
Fichier: fl_crew_reddit/main.py
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fl_crew_reddit.config import FLCrewRedditConfig
from fl_crew_reddit.crew_manager import FLCrewRedditManager


def main():
    """Point d'entrée principal"""
    print("\n" + "="*60)
    print("🤖 FL CREW REDDIT - FEDERATED LEARNING SYSTEM")
    print("="*60)
    print("Système de Federated Learning avec 5 agents spécialisés")
    print("="*60 + "\n")
    
    try:
        # Initialiser la configuration
        config = FLCrewRedditConfig()
        config.validate()
        
        # Créer le manager
        manager = FLCrewRedditManager(config)
        
        # Lancer le Federated Learning
        results = manager.run_federated_learning(num_rounds=config.FEDERATION_ROUNDS)
        
        print("\n✅ Processus terminé avec succès!")
        print(f"📊 Résultats disponibles dans: {config.RESULTS_DIR}")
        
        return results
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Processus interrompu par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

