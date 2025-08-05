#!/usr/bin/env python3
"""
Script de test simple pour le système de recommandations
"""

import sys
import os
sys.path.append('.')

from etreprof.ml_package.recommender import (
    load_recommendation_data,
    get_top_topics_for_cluster,
    generate_recommendations_for_cluster
)

def test_data_loading():
    """Test du chargement des données"""
    print("🔍 Test du chargement des données...")

    try:
        df_users, df_contents, df_content_with_topics = load_recommendation_data()

        print(f"✅ Users chargés: {len(df_users)} lignes")
        print(f"✅ Contents chargés: {len(df_contents)} lignes")
        print(f"✅ Content with topics chargés: {len(df_content_with_topics) if df_content_with_topics is not None else 0} lignes")

        # Vérifier les colonnes importantes
        print(f"\n📊 Colonnes users (échantillon): {list(df_users.columns)[:10]}")
        print(f"📊 Colonnes content_with_topics: {list(df_content_with_topics.columns) if df_content_with_topics is not None else 'None'}")

        # Vérifier les clusters
        if 'cluster' in df_users.columns:
            cluster_counts = df_users['cluster'].value_counts().sort_index()
            print(f"📊 Distribution clusters: {dict(cluster_counts)}")

        return df_users, df_contents, df_content_with_topics

    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")
        return None, None, None

def test_topics_by_cluster(df_users):
    """Test de l'analyse des topics par cluster"""
    print("\n🎯 Test des topics par cluster...")

    try:
        for cluster_id in range(5):
            top_topics = get_top_topics_for_cluster(df_users, cluster_id, top_n=3)
            cluster_size = len(df_users[df_users['cluster'] == cluster_id])
            print(f"Cluster {cluster_id} ({cluster_size} users): Topics {top_topics}")

    except Exception as e:
        print(f"❌ Erreur topics par cluster: {e}")

def test_recommendations():
    """Test de génération de recommandations"""
    print("\n🚀 Test des recommandations...")

    # Tester pour le cluster 2 (Super Users)
    cluster_id = 2

    try:
        recommendations = generate_recommendations_for_cluster(cluster_id, num_recommendations=4)

        print(f"\n🎯 Recommandations pour Cluster {cluster_id}:")
        print(f"Cluster: {recommendations.get('cluster_name', 'N/A')}")
        print(f"Topics populaires: {recommendations.get('reasoning', {}).get('top_topics', [])}")
        print(f"Nombre de recommandations: {len(recommendations.get('recommendations', []))}")

        print("\n📚 Détail des recommandations:")
        for i, rec in enumerate(recommendations.get('recommendations', []), 1):
            print(f"{i}. {rec.get('title', 'N/A')} ({rec.get('type', 'N/A')})")
            print(f"   Raison: {rec.get('reason', 'N/A')}")
            print(f"   Priority challenge: {rec.get('is_priority_challenge', False)}")
            print()

        return recommendations

    except Exception as e:
        print(f"❌ Erreur génération recommandations: {e}")
        return None

def main():
    """Fonction principale de test"""
    print("🧪 TESTS DU SYSTÈME DE RECOMMANDATIONS ÊtrePROF")
    print("=" * 50)

    # Test 1: Chargement des données
    df_users, df_contents, df_content_with_topics = test_data_loading()

    if df_users is None:
        print("❌ Impossible de continuer sans données")
        return

    # Test 2: Topics par cluster
    test_topics_by_cluster(df_users)

    # Test 3: Génération de recommandations
    recommendations = test_recommendations()

    print("\n✅ Tests terminés!")

    if recommendations and not recommendations.get('error'):
        print("🎉 Le système de recommandations fonctionne!")
    else:
        print("⚠️  Il y a des problèmes à corriger")

if __name__ == "__main__":
    main()
