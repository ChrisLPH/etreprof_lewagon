"""
ML Package - ÊtrePROF Machine Learning Models

Ce package contient tous les modèles de machine learning pour:
- Classification automatique de contenu (thèmes + défis prioritaires)
- Clustering d'utilisateurs basé sur les comportements
- Système de recommandations hybride

Version MOCK pour développement - à remplacer par les vrais modèles de l'équipe
Généré par IA pour simuler le comportement en attendant l'intégration de modèles réels.
A utiliser uniquement pour les tests et la démonstration de l'interface utilisateur.
Ne pas utiliser en production.
"""

from .content_classifier import ContentClassifier
from .user_clustering import UserClustering
from .recommender import ContentRecommender

__version__ = "0.1.0-mock"
__author__ = "ÊtrePROF Team"

__all__ = [
    "ContentClassifier",
    "UserClustering",
    "ContentRecommender"
]

# Configuration par défaut
DEFAULT_N_CLUSTERS = 8
DEFAULT_N_RECOMMENDATIONS = 5

def get_version():
    """Retourne la version du package"""
    return __version__

def create_full_pipeline():
    """
    Crée une instance complète du pipeline ML

    Returns:
        Dict avec les 3 composants principaux
    """
    return {
        'content_classifier': ContentClassifier(),
        'user_clustering': UserClustering(n_clusters=DEFAULT_N_CLUSTERS),
        'recommender': ContentRecommender()
    }
