"""
Script de test pour le pipeline ML complet

Ce script teste l'intégration entre:
- Classification de contenu
- Clustering utilisateurs
- Système de recommandations

Usage: python scripts/test_ml_pipeline.py
"""

import sys
import os
import pandas as pd
import numpy as np

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_package import ContentClassifier, UserClustering, ContentRecommender, create_full_pipeline


def create_mock_data():
    """Crée des données mock pour tester le pipeline"""
    print("📊 Création des données de test...")

    # Mock users data
    np.random.seed(42)
    users_data = pd.DataFrame({
        'id': range(1000, 1200),
        'anciennete': np.random.randint(1, 30, 200),
        'degre': np.random.choice([1, 2], 200),
        'maternelle': np.random.choice([0, 1], 200, p=[0.8, 0.2]),
        'elementaire': np.random.choice([0, 1], 200, p=[0.6, 0.4]),
        'college': np.random.choice([0, 1], 200, p=[0.7, 0.3]),
        'lycee': np.random.choice([0, 1], 200, p=[0.8, 0.2]),
        'lycee_pro': np.random.choice([0, 1], 200, p=[0.9, 0.1])
    })

    # Mock content data
    content_samples = [
        "# Gérer les élèves en difficulté\n\nStrategies pour adapter la pédagogie et favoriser la réussite de tous.",
        "# Utiliser le numérique en classe\n\nIntégrer les outils technologiques pour enrichir les apprentissages.",
        "# Bien-être de l'enseignant\n\nTechniques pour gérer le stress et préserver son équilibre professionnel.",
        "# Évaluation par compétences\n\nMise en place d'une évaluation formative et bienveillante.",
        "# École inclusive\n\nAdapter sa pédagogie aux élèves à besoins éducatifs particuliers."
    ]

    contents_data = pd.DataFrame({
        'id': range(100, 105),
        'content': content_samples,
        'title': [f"Ressource #{i}" for i in range(1, 6)]
    })

    return users_data, contents_data


def test_content_classification():
    """Test de la classification de contenu"""
    print("\n🔍 TEST - Classification de contenu")
    print("=" * 50)

    classifier = ContentClassifier()

    test_text = """
    # Différenciation pédagogique en mathématiques

    Cette ressource présente des stratégies pour adapter l'enseignement
    des mathématiques aux différents niveaux d'élèves. L'objectif est de
    permettre la réussite de tous les élèves en proposant des activités
    adaptées à leurs besoins spécifiques.
    """

    result = classifier.get_top_predictions(test_text)

    print(f"✅ Thème principal: {result['theme_principal']['nom']}")
    print(f"   Confiance: {result['theme_principal']['confidence']}")
    print(f"✅ Défi prioritaire: {result['defi_prioritaire']['nom']}")
    print(f"   Confiance: {result['defi_prioritaire']['confidence']}")
    print(f"✅ Nombre de mots: {result['features_extracted']['word_count']}")

    return classifier


def test_user_clustering():
    """Test du clustering utilisateurs"""
    print("\n👥 TEST - Clustering utilisateurs")
    print("=" * 50)

    users_data, _ = create_mock_data()

    clusterer = UserClustering(n_clusters=6)
    clusterer.fit(users_data)

    # Afficher le résumé des clusters
    summary = clusterer.get_cluster_summary()
    print("✅ Clusters créés:")
    print(summary.to_string(index=False))

    # Test de prédiction
    new_users = users_data.sample(5).copy()
    predictions = clusterer.predict(new_users)
    print(f"\n✅ Prédictions pour 5 nouveaux utilisateurs:")
    print(predictions[['user_id', 'cluster_name', 'confidence_score']].to_string(index=False))

    return clusterer


def test_recommendations():
    """Test du système de recommandations"""
    print("\n🎯 TEST - Système de recommandations")
    print("=" * 50)

    recommender = ContentRecommender()
    mock_clusters = {i: f"Cluster_{i}" for i in range(5)}

    recommender.fit(None, mock_clusters)  # Utilise le catalogue mock

    # Recommandations pour un cluster
    cluster_recs = recommender.get_recommendations_for_cluster(0, 3)
    print("✅ Top 3 recommandations pour le Cluster 0:")
    print(cluster_recs[['title', 'type', 'theme_principal', 'recommendation_score']].to_string(index=False))

    # Recommandations pour un utilisateur
    user_recs = recommender.get_user_recommendations(user_id=12345, user_cluster=1, n_recommendations=3)
    print(f"\n✅ Recommandations personnalisées pour l'utilisateur 12345:")
    print(user_recs[['title', 'type', 'personalized_score']].to_string(index=False))

    return recommender


def test_full_pipeline():
    """Test complet du pipeline intégré"""
    print("\n🚀 TEST - Pipeline complet")
    print("=" * 50)

    # Créer le pipeline
    pipeline = create_full_pipeline()
    users_data, contents_data = create_mock_data()

    print("1️⃣ Classification des contenus...")
    content_results = pipeline['content_classifier'].batch_classify(contents_data)
    print(f"   ✅ {len(content_results)} contenus classifiés")

    print("2️⃣ Clustering des utilisateurs...")
    pipeline['user_clustering'].fit(users_data)
    cluster_info = pipeline['user_clustering'].get_cluster_info()
    print(f"   ✅ {len(cluster_info)} clusters créés")

    print("3️⃣ Génération des recommandations...")
    pipeline['recommender'].fit(None, cluster_info)
    all_recs = pipeline['recommender'].get_all_cluster_recommendations(3)
    print(f"   ✅ Recommandations générées pour {len(all_recs)} clusters")

    # Export des résultats
    print("4️⃣ Export des résultats...")

    # Sauvegarder les résultats
    content_results.to_csv('test_content_classification.csv', index=False)

    cluster_summary = pipeline['user_clustering'].get_cluster_summary()
    cluster_summary.to_csv('test_cluster_summary.csv', index=False)

    recs_summary = pipeline['recommender'].export_recommendations_summary()
    recs_summary.to_csv('test_recommendations.csv', index=False)

    print("   ✅ Résultats sauvegardés dans les fichiers CSV")

    return pipeline


def main():
    """Fonction principale - lance tous les tests"""
    print("🧪 DÉBUT DES TESTS DU PIPELINE ML")
    print("=" * 60)

    try:
        # Tests individuels
        classifier = test_content_classification()
        clusterer = test_user_clustering()
        recommender = test_recommendations()

        # Test intégré
        pipeline = test_full_pipeline()

        print("\n🎉 TOUS LES TESTS SONT PASSÉS !")
        print("✅ Le pipeline ML est fonctionnel")
        print("\n📋 Fichiers générés:")
        print("   - test_content_classification.csv")
        print("   - test_cluster_summary.csv")
        print("   - test_recommendations.csv")

    except Exception as e:
        print(f"\n❌ ERREUR LORS DES TESTS: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
