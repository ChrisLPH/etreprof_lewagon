"""
Recommendation System Module
Système de recommandations hybride basé sur le clustering et le contenu.

Version MOCK pour développement - à remplacer par les vrais modèles de l'équipe
Généré par IA pour simuler le comportement d'un recommender de contenus en attendant l'intégration de modèles réels.
A utiliser uniquement pour les tests et la démonstration de l'interface utilisateur.
Ne pas utiliser en production.
"""

import pandas as pd
import numpy as np
import random
from typing import Dict, List, Optional, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


class ContentRecommender:
    """Système de recommandations (VERSION MOCK)"""

    def __init__(self):
        self.content_features = None
        self.user_clusters = None
        self.content_catalog = None
        self.cluster_preferences = {}

        # Types de contenu disponibles
        self.content_types = [
            "Fiche outil", "Guide pratique", "Vidéo", "Webinaire",
            "Article", "Infographie", "Checklist", "Formation"
        ]

        # Défis prioritaires
        self.defis_prioritaires = [
            "transition_ecologique", "sante_mentale", "ecole_inclusive",
            "competences_psychosociales", "reussite_tous_eleves", "aucun"
        ]

        # Thèmes disponibles
        self.themes = [
            "Pédagogie différenciée", "Évaluation des apprentissages",
            "Gestion de classe", "Numérique éducatif", "Bien-être enseignant",
            "Relations parents-école", "Orientation scolaire", "Éducation inclusive"
        ]

    def _create_mock_content_catalog(self, n_contents: int = 500) -> pd.DataFrame:
        """Crée un catalogue de contenu mock pour la démo"""
        np.random.seed(42)

        contents = []
        for i in range(n_contents):
            content = {
                'content_id': f'content_{i:04d}',
                'title': f'Ressource pédagogique #{i+1}',
                'type': random.choice(self.content_types),
                'theme_principal': random.choice(self.themes),
                'defi_prioritaire': random.choice(self.defis_prioritaires),
                'popularity_score': np.random.uniform(0.1, 1.0),
                'quality_score': np.random.uniform(0.3, 1.0),
                'engagement_rate': np.random.uniform(0.05, 0.8),
                'word_count': np.random.randint(200, 3000),
                'creation_date': f'2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}'
            }
            contents.append(content)

        return pd.DataFrame(contents)

    def _create_cluster_preferences(self, n_clusters: int = 8):
        """Crée les préférences mock par cluster"""
        np.random.seed(42)

        preferences = {}
        for cluster_id in range(n_clusters):
            # Chaque cluster a des préférences différentes
            theme_prefs = {}
            for theme in self.themes:
                theme_prefs[theme] = np.random.uniform(0.1, 1.0)

            defi_prefs = {}
            for defi in self.defis_prioritaires:
                defi_prefs[defi] = np.random.uniform(0.1, 1.0)

            type_prefs = {}
            for content_type in self.content_types:
                type_prefs[content_type] = np.random.uniform(0.2, 1.0)

            preferences[cluster_id] = {
                'themes': theme_prefs,
                'defis': defi_prefs,
                'types': type_prefs,
                'engagement_preference': np.random.uniform(0.3, 0.9),
                'novelty_preference': np.random.uniform(0.1, 0.8)
            }

        self.cluster_preferences = preferences

    def fit(self, content_catalog: pd.DataFrame, user_clusters: Dict):
        """
        Initialise le système de recommandations

        Args:
            content_catalog: DataFrame avec les contenus disponibles
            user_clusters: Informations sur les clusters d'utilisateurs
        """
        print("🔄 Initialisation du système de recommandations...")

        # Si pas de catalogue fourni, on crée un mock
        if content_catalog is None or len(content_catalog) == 0:
            self.content_catalog = self._create_mock_content_catalog()
            print(f"📚 Catalogue mock créé avec {len(self.content_catalog)} contenus")
        else:
            self.content_catalog = content_catalog.copy()

        # Initialiser les préférences par cluster
        n_clusters = len(user_clusters) if user_clusters else 8
        self._create_cluster_preferences(n_clusters)

        print("✅ Système de recommandations initialisé")

        return self

    def _calculate_content_score(self, content: pd.Series, cluster_id: int) -> float:
        """Calcule le score de recommandation d'un contenu pour un cluster"""
        if cluster_id not in self.cluster_preferences:
            return random.uniform(0.1, 0.7)

        prefs = self.cluster_preferences[cluster_id]
        score = 0.0

        # Score basé sur le thème (40% du score)
        theme_score = prefs['themes'].get(content['theme_principal'], 0.5)
        score += theme_score * 0.4

        # Score basé sur le défi prioritaire (30% du score)
        defi_score = prefs['defis'].get(content['defi_prioritaire'], 0.5)
        score += defi_score * 0.3

        # Score basé sur le type de contenu (20% du score)
        type_score = prefs['types'].get(content['type'], 0.5)
        score += type_score * 0.2

        # Score de qualité/popularité (10% du score)
        quality_score = (content['quality_score'] + content['popularity_score']) / 2
        score += quality_score * 0.1

        # Ajout d'un peu de randomness pour la diversité
        score += np.random.uniform(-0.1, 0.1)

        return max(0.0, min(1.0, score))

    def get_recommendations_for_cluster(self, cluster_id: int, n_recommendations: int = 5) -> pd.DataFrame:
        """
        Génère des recommandations pour un cluster spécifique
        """
        if self.content_catalog is None:
            raise ValueError("Le système doit être initialisé avec fit() avant de générer des recommandations")

        print(f"🎯 Génération de {n_recommendations} recommandations pour le cluster {cluster_id}")

        # Calculer les scores pour tous les contenus
        content_scores = []
        for idx, content in self.content_catalog.iterrows():
            score = self._calculate_content_score(content, cluster_id)
            content_scores.append({
                'content_id': content['content_id'],
                'title': content['title'],
                'type': content['type'],
                'theme_principal': content['theme_principal'],
                'defi_prioritaire': content['defi_prioritaire'],
                'recommendation_score': round(score, 3),
                'popularity_score': round(content['popularity_score'], 3),
                'quality_score': round(content['quality_score'], 3)
            })

        # Trier par score et prendre le top N
        content_scores_df = pd.DataFrame(content_scores)
        top_recommendations = content_scores_df.nlargest(n_recommendations, 'recommendation_score')

        # Ajouter des justifications
        top_recommendations['justification'] = top_recommendations.apply(
            lambda row: self._generate_justification(row, cluster_id), axis=1
        )

        return top_recommendations.reset_index(drop=True)

    def _generate_justification(self, content_row: pd.Series, cluster_id: int) -> str:
        """Génère une justification pour la recommandation"""
        justifications = [
            f"Populaire dans votre profil ({content_row['theme_principal']})",
            f"Correspond à vos préférences ({content_row['type']})",
            f"Défi prioritaire pertinent ({content_row['defi_prioritaire']})",
            "Ressource hautement évaluée par la communauté",
            f"Format adapté à votre cluster",
            "Contenu récent et actualisé"
        ]

        return random.choice(justifications)

    def get_all_cluster_recommendations(self, n_recommendations: int = 5) -> Dict[int, pd.DataFrame]:
        """
        Génère des recommandations pour tous les clusters
        """
        all_recommendations = {}

        for cluster_id in self.cluster_preferences.keys():
            recommendations = self.get_recommendations_for_cluster(cluster_id, n_recommendations)
            all_recommendations[cluster_id] = recommendations

        return all_recommendations

    def get_user_recommendations(self, user_id: int, user_cluster: int, n_recommendations: int = 5) -> pd.DataFrame:
        """
        Génère des recommandations pour un utilisateur spécifique
        """
        # Recommandations basées sur le cluster
        cluster_recs = self.get_recommendations_for_cluster(user_cluster, n_recommendations * 2)

        # Ajouter un peu de personnalisation (mock)
        # Dans la vraie version, on utiliserait l'historique de l'utilisateur
        personalization_boost = np.random.uniform(0.9, 1.1, len(cluster_recs))
        cluster_recs['personalized_score'] = cluster_recs['recommendation_score'] * personalization_boost

        # Prendre le top N après personnalisation
        final_recs = cluster_recs.nlargest(n_recommendations, 'personalized_score')

        # Ajouter l'ID utilisateur
        final_recs['user_id'] = user_id

        return final_recs.reset_index(drop=True)

    def get_content_similarity(self, content_id: str, n_similar: int = 5) -> pd.DataFrame:
        """
        Trouve des contenus similaires à un contenu donné (content-based)
        """
        if self.content_catalog is None:
            return pd.DataFrame()

        # Trouver le contenu de référence
        ref_content = self.content_catalog[self.content_catalog['content_id'] == content_id]
        if len(ref_content) == 0:
            return pd.DataFrame()

        ref_content = ref_content.iloc[0]

        # Calculer la similarité basique (mock)
        similarities = []
        for idx, content in self.content_catalog.iterrows():
            if content['content_id'] == content_id:
                continue

            # Similarité basée sur le thème et le type
            theme_match = 1.0 if content['theme_principal'] == ref_content['theme_principal'] else 0.3
            type_match = 1.0 if content['type'] == ref_content['type'] else 0.5
            defi_match = 1.0 if content['defi_prioritaire'] == ref_content['defi_prioritaire'] else 0.4

            similarity = (theme_match + type_match + defi_match) / 3
            similarity += np.random.uniform(-0.1, 0.1)  # Ajouter du bruit

            similarities.append({
                'content_id': content['content_id'],
                'title': content['title'],
                'type': content['type'],
                'theme_principal': content['theme_principal'],
                'similarity_score': round(max(0, min(1, similarity)), 3)
            })

        # Trier et retourner le top N
        similarities_df = pd.DataFrame(similarities)
        return similarities_df.nlargest(n_similar, 'similarity_score').reset_index(drop=True)

    def export_recommendations_summary(self) -> pd.DataFrame:
        """
        Exporte un résumé de toutes les recommandations par cluster
        """
        all_recs = self.get_all_cluster_recommendations(5)

        summary_data = []
        for cluster_id, recommendations in all_recs.items():
            for idx, rec in recommendations.iterrows():
                summary_data.append({
                    'cluster_id': cluster_id,
                    'rank': idx + 1,
                    'content_id': rec['content_id'],
                    'title': rec['title'],
                    'type': rec['type'],
                    'theme_principal': rec['theme_principal'],
                    'defi_prioritaire': rec['defi_prioritaire'],
                    'score': rec['recommendation_score'],
                    'justification': rec['justification']
                })

        return pd.DataFrame(summary_data)


# Fonction utilitaire pour tester
def demo_recommendations():
    """Démonstration du système de recommandations"""
    # Initialiser le recommender
    recommender = ContentRecommender()

    # Mock cluster info
    mock_clusters = {i: f"Cluster_{i}" for i in range(5)}

    # Fit avec des données mock
    recommender.fit(None, mock_clusters)

    print("=== DÉMONSTRATION RECOMMANDATIONS ===")

    # Recommandations pour un cluster spécifique
    cluster_recs = recommender.get_recommendations_for_cluster(0, 5)
    print(f"\n🎯 Top 5 recommandations pour le Cluster 0:")
    print(cluster_recs[['title', 'type', 'theme_principal', 'recommendation_score', 'justification']])

    # Recommandations pour un utilisateur
    user_recs = recommender.get_user_recommendations(user_id=12345, user_cluster=1, n_recommendations=3)
    print(f"\n👤 Recommandations pour l'utilisateur 12345:")
    print(user_recs[['title', 'type', 'personalized_score']])

    # Contenus similaires
    sample_content_id = recommender.content_catalog['content_id'].iloc[0]
    similar_content = recommender.get_content_similarity(sample_content_id, 3)
    print(f"\n🔗 Contenus similaires à {sample_content_id}:")
    print(similar_content[['title', 'type', 'similarity_score']])

    return recommender


if __name__ == "__main__":
    demo_recommendations()
