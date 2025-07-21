"""
User Clustering Module
Clustering des utilisateurs basé sur leurs comportements et profils.

Version MOCK pour développement - à remplacer par les vrais modèles de l'équipe
Généré par IA pour simuler le comportement d'un classifieur de users en attendant l'intégration de modèles réels.
A utiliser uniquement pour les tests et la démonstration de l'interface utilisateur.
Ne pas utiliser en production.
"""

import pandas as pd
import numpy as np
import random
from typing import Dict, List, Optional, Tuple
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


class UserClustering:
    """Clustering utilisateurs (VERSION MOCK)"""

    def __init__(self, n_clusters: int = 8):
        self.n_clusters = min(n_clusters, 8)  # Max 8 clusters comme spécifié
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.cluster_profiles = {}

        # Noms de clusters prédéfinis pour la démo
        self.cluster_names = [
            "Les Innovateurs Numériques",
            "Les Pédagogues Traditionnels",
            "Les Spécialistes Inclusifs",
            "Les Gestionnaires Pragmatiques",
            "Les Experts Évaluation",
            "Les Mentors Bienveillants",
            "Les Novices Motivés",
            "Les Vétérans Expérimentés"
        ][:self.n_clusters]

    def _prepare_features(self, users_df: pd.DataFrame) -> pd.DataFrame:
        """
        Prépare les features pour le clustering (VERSION MOCK)
        """
        # Features basiques pour la démo
        feature_cols = []

        # Features numériques disponibles
        numeric_features = [
            'anciennete', 'degre', 'maternelle', 'elementaire', 'college', 'lycee',
            'lycee_pro', 'autre'
        ]

        # Ajouter les features qui existent dans le DataFrame
        for col in numeric_features:
            if col in users_df.columns:
                feature_cols.append(col)

        # Ajouter les features de niveaux si elles existent
        niveau_cols = [col for col in users_df.columns if col.startswith('niveau_')]
        feature_cols.extend(niveau_cols)

        # Si on a peu de features, on en crée des mock
        if len(feature_cols) < 5:
            # Créer des features mock basées sur l'ancienneté et le degré
            users_df['mock_engagement'] = np.random.uniform(0, 1, len(users_df))
            users_df['mock_diversity'] = np.random.uniform(0, 1, len(users_df))
            users_df['mock_activity'] = np.random.uniform(0, 1, len(users_df))
            feature_cols.extend(['mock_engagement', 'mock_diversity', 'mock_activity'])

        self.feature_columns = feature_cols

        # Retourner le DataFrame avec les features sélectionnées
        features_df = users_df[['id'] + feature_cols].copy()

        # Gérer les valeurs manquantes
        for col in feature_cols:
            if col in features_df.columns:
                features_df[col] = features_df[col].fillna(0)

        return features_df

    def fit(self, users_df: pd.DataFrame) -> 'UserClustering':
        """
        Entraîne le modèle de clustering
        """
        print(f"🔄 Entraînement du clustering avec {len(users_df)} utilisateurs...")

        # Préparer les features
        features_df = self._prepare_features(users_df)

        # Features pour le clustering (sans l'ID)
        X = features_df.drop(['id'], axis=1)

        # Normalisation
        X_scaled = self.scaler.fit_transform(X)

        # Clustering K-means (MOCK)
        self.model = KMeans(n_clusters=self.n_clusters, random_state=42)
        clusters = self.model.fit_predict(X_scaled)

        # Sauvegarder les prédictions
        features_df['cluster'] = clusters

        # Générer les profils de clusters
        self._generate_cluster_profiles(features_df)

        print(f"✅ Clustering terminé - {self.n_clusters} clusters créés")

        return self

    def _generate_cluster_profiles(self, features_df: pd.DataFrame):
        """
        Génère les profils descriptifs des clusters
        """
        profiles = {}

        for i in range(self.n_clusters):
            cluster_data = features_df[features_df['cluster'] == i]

            if len(cluster_data) == 0:
                continue

            # Calculer les moyennes des features
            feature_means = {}
            for col in self.feature_columns:
                if col in cluster_data.columns:
                    feature_means[col] = cluster_data[col].mean()

            # Profil mock avec des caractéristiques générées
            profiles[i] = {
                "nom": self.cluster_names[i],
                "taille": len(cluster_data),
                "pourcentage": round(len(cluster_data) / len(features_df) * 100, 1),
                "features_moyennes": feature_means,
                "description": self._generate_cluster_description(i),
                "themes_preferes": self._generate_preferred_themes(i),
                "niveau_engagement": random.choice(["Faible", "Moyen", "Élevé"]),
                "anciennete_moyenne": feature_means.get('anciennete', 0)
            }

        self.cluster_profiles = profiles

    def _generate_cluster_description(self, cluster_id: int) -> str:
        """Génère une description mock pour chaque cluster"""
        descriptions = [
            "Enseignants technophiles qui intègrent activement le numérique dans leur pédagogie",
            "Enseignants expérimentés privilégiant les méthodes éprouvées et la transmission directe",
            "Enseignants spécialisés dans l'adaptation aux besoins particuliers des élèves",
            "Enseignants focalisés sur l'organisation et la gestion efficace de classe",
            "Enseignants experts dans l'évaluation et le suivi des apprentissages",
            "Enseignants bienveillants privilégiant la relation et le bien-être des élèves",
            "Nouveaux enseignants en recherche active de ressources et formations",
            "Enseignants seniors avec une forte expertise disciplinaire"
        ]

        return descriptions[cluster_id] if cluster_id < len(descriptions) else "Profil mixte"

    def _generate_preferred_themes(self, cluster_id: int) -> List[str]:
        """Génère les thèmes préférés mock pour chaque cluster"""
        all_themes = [
            "Pédagogie différenciée", "Évaluation des apprentissages",
            "Gestion de classe", "Numérique éducatif", "Bien-être enseignant",
            "Relations parents-école", "Orientation scolaire", "Éducation inclusive"
        ]

        # Chaque cluster a une préférence pour 2-3 thèmes
        np.random.seed(cluster_id)  # Pour la reproductibilité
        n_themes = random.randint(2, 4)
        preferred = np.random.choice(all_themes, n_themes, replace=False).tolist()

        return preferred

    def predict(self, users_df: pd.DataFrame) -> pd.DataFrame:
        """
        Prédit les clusters pour de nouveaux utilisateurs
        """
        if self.model is None:
            raise ValueError("Le modèle doit être entraîné avant la prédiction (appeler .fit() d'abord)")

        print(f"🔄 Prédiction pour {len(users_df)} nouveaux utilisateurs...")

        # Préparer les features
        features_df = self._prepare_features(users_df)

        # Features pour la prédiction (sans l'ID)
        X = features_df.drop(['id'], axis=1)

        # Normalisation avec le scaler déjà entraîné
        X_scaled = self.scaler.transform(X)

        # Prédiction
        predicted_clusters = self.model.predict(X_scaled)

        # Calculer les scores de confiance (mock)
        confidence_scores = np.random.uniform(0.6, 0.95, len(predicted_clusters))

        # Préparer le résultat
        result_df = pd.DataFrame({
            'user_id': features_df['id'],
            'cluster_predicted': predicted_clusters,
            'cluster_name': [self.cluster_names[c] for c in predicted_clusters],
            'confidence_score': np.round(confidence_scores, 3)
        })

        print("✅ Prédiction terminée")

        return result_df

    def get_cluster_info(self, cluster_id: Optional[int] = None) -> Dict:
        """
        Retourne les informations sur un cluster spécifique ou tous les clusters
        """
        if cluster_id is not None:
            return self.cluster_profiles.get(cluster_id, {})

        return self.cluster_profiles

    def get_cluster_summary(self) -> pd.DataFrame:
        """
        Retourne un résumé de tous les clusters sous forme de DataFrame
        """
        summary_data = []

        for cluster_id, profile in self.cluster_profiles.items():
            summary_data.append({
                'cluster_id': cluster_id,
                'nom': profile['nom'],
                'taille': profile['taille'],
                'pourcentage': profile['pourcentage'],
                'niveau_engagement': profile['niveau_engagement'],
                'anciennete_moyenne': round(profile['anciennete_moyenne'], 1),
                'themes_preferes': ', '.join(profile['themes_preferes'][:2]) + '...'
            })

        return pd.DataFrame(summary_data)


# Fonction utilitaire pour tester
def demo_clustering():
    """Démonstration du clustering"""
    # Données mock pour la démo
    np.random.seed(42)
    mock_users = pd.DataFrame({
        'id': range(1000, 1100),
        'anciennete': np.random.randint(1, 30, 100),
        'degre': np.random.choice([1, 2], 100),
        'maternelle': np.random.choice([0, 1], 100, p=[0.8, 0.2]),
        'elementaire': np.random.choice([0, 1], 100, p=[0.6, 0.4]),
        'college': np.random.choice([0, 1], 100, p=[0.7, 0.3]),
        'lycee': np.random.choice([0, 1], 100, p=[0.8, 0.2])
    })

    # Clustering
    clusterer = UserClustering(n_clusters=5)
    clusterer.fit(mock_users)

    # Afficher les résultats
    print("=== DÉMONSTRATION CLUSTERING ===")
    summary = clusterer.get_cluster_summary()
    print(summary)

    # Test de prédiction sur de nouveaux utilisateurs
    new_users = mock_users.sample(10).copy()
    predictions = clusterer.predict(new_users)
    print("\n=== PRÉDICTIONS ===")
    print(predictions.head())

    return clusterer


if __name__ == "__main__":
    demo_clustering()
