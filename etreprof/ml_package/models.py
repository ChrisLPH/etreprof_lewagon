import os
import pickle
import pandas as pd
from typing import Dict
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import json
import numpy as np
# from .recommender import generate_recommendations_for_cluster, get_user_recommendations
from .recommender import generate_simple_recommendations


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

# Content classification function
# Old version commented out for reference - Mockup before real models were implemented
# def classify_content(content: str) -> Dict:
#     theme_path = os.path.join(ROOT_PATH, 'pickles/theme_model.pkl')
#     with open(theme_path, 'rb') as f:
#         theme_model = pickle.load(f)

#     defi_path = os.path.join(ROOT_PATH, 'pickles/defi_model.pkl')
#     with open(defi_path, 'rb') as f:
#         defi_model = pickle.load(f)

#     theme_pred = theme_model.predict([content])[0]
#     defi_pred = defi_model.predict([content])[0]

#     return {
#         "theme": theme_pred,
#         "defi": defi_pred
#     }

def classify_content(content: str) -> Dict:
    """
    Classify content using BERTopic model trained by Guillaume
    Returns top 3 topics with confidence scores.
    """
    bertopic_path = os.path.join(ROOT_PATH, 'pickles/bertopic')
    topics_json_path = os.path.join(bertopic_path, 'topics.json')

    # Load topics.json to get topic labels
    with open(topics_json_path, 'r', encoding='utf-8') as f:
        topics_data = json.load(f)

    topic_labels = topics_data['topic_labels']

    # Load the model
    embedding_model = SentenceTransformer('intfloat/multilingual-e5-large-instruct')
    topic_model = BERTopic.load(bertopic_path, embedding_model=embedding_model)

    # Prediction
    topics, scores = topic_model.transform([content])
    topic_id = topics[0]
    confidence = scores[0] if len(scores) > 0 else 0.0

    # Topic principal (le seul assigné par BERTopic)
    main_topic_id = topics[0]
    main_confidence = float(scores[0][main_topic_id])  # Similarité du topic assigné

    # Label du topic principal
    main_topic_label = topic_labels.get(str(main_topic_id), f"Topic {main_topic_id}")
    if "_" in main_topic_label:
        main_topic_label = main_topic_label.split("_", 1)[1]


    return {
        "topic_principal": {
            "id": int(main_topic_id),
            "label": main_topic_label,
            "confidence": round(main_confidence * 100, 1)
        }
    }

# User clustering functions
def load_clustering_models():
    kmeans_path = os.path.join(ROOT_PATH, 'pickles/kmeans_model.pkl')
    scaler_path = os.path.join(ROOT_PATH, 'pickles/scaler_model.pkl')
    metadata_path = os.path.join(ROOT_PATH, 'pickles/metadata.json')
    profiles_path = os.path.join(os.path.dirname(os.path.dirname(ROOT_PATH)), 'data/cluster_profiles.csv')
    personas_path = os.path.join(os.path.dirname(os.path.dirname(ROOT_PATH)), 'data/cluster_personas_lisibles.json')

    # Load models
    with open(kmeans_path, 'rb') as f:
        kmeans = pickle.load(f)

    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)

    # Load metadata
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    # Load cluster profiles (statistical data)
    profiles = pd.read_csv(profiles_path, index_col=0)

    # Load personas (business-friendly descriptions)
    with open(personas_path, 'r', encoding='utf-8') as f:
        personas = json.load(f)

    return kmeans, scaler, metadata, profiles, personas

def get_cluster_info():
    """Get information about all 5 clusters with real data"""
    _, _, metadata, profiles, personas = load_clustering_models()

    # Combine statistical profiles with business personas
    cluster_info = {}

    for cluster_id in range(5):  # 5 clusters: 0, 1, 2, 3, 4
        cluster_info[cluster_id] = {
            "name": personas[str(cluster_id)]["nom"],
            "count": int(personas[str(cluster_id)]["taille"].split()[0].replace(",", "")),
            "percentage": float(personas[str(cluster_id)]["taille"].split("(")[1].replace("%)", "")),
            "description": {
                "anciennete_moyenne": personas[str(cluster_id)]["anciennete_moyenne"],
                "activite_generale": personas[str(cluster_id)]["activite_generale"],
                "engagement_email": personas[str(cluster_id)]["engagement_email"],
                "usage_contenu": personas[str(cluster_id)]["usage_contenu"],
                "diversite_thematique": personas[str(cluster_id)]["diversite_thematique"],
                "niveau_principal": personas[str(cluster_id)]["niveau_principal"],
                "repartition_niveaux": personas[str(cluster_id)]["repartition_niveaux"]
            },
            "profile": profiles.loc[cluster_id].to_dict() if cluster_id in profiles.index else {}
        }

    return cluster_info

# Update clustering of users
def predict_user_clusters(df_users):
    kmeans, scaler, metadata, _, _ = load_clustering_models()

    # Get the features used for clustering from metadata
    features_used = metadata['features_used']

    # Verify that required features are present
    missing_features = [f for f in features_used if f not in df_users.columns]
    if missing_features:
        raise ValueError(f"Missing required features for clustering: {missing_features}")

    # Extract features in the correct order
    X = df_users[features_used].copy()

    # Handle any missing values
    X = X.fillna(0)

    # Apply the same preprocessing as during training
    X_scaled = scaler.transform(X)

    # Predict clusters
    clusters = kmeans.predict(X_scaled)

    return clusters

def get_user_profile(user_id: int):
    assignments_path = os.path.join(os.path.dirname(os.path.dirname(ROOT_PATH)), 'data/user_cluster_assignments.csv')
    df_assignments = pd.read_csv(assignments_path)

    user_data = df_assignments[df_assignments['id'] == user_id]

    if user_data.empty:
        return {"error": f"User {user_id} not found"}

    user_row = user_data.iloc[0]
    cluster_id = int(user_row['cluster'])

    cluster_info = get_cluster_info()[cluster_id]

    recommendations = generate_simple_recommendations(cluster_id)

    niveaux = []
    if user_row.get('maternelle', 0) == 1:
        niveaux.append('maternelle')
    if user_row.get('elementaire', 0) == 1:
        niveaux.append('elementaire')
    if user_row.get('college', 0) == 1:
        niveaux.append('college')
    if user_row.get('lycee', 0) == 1:
        niveaux.append('lycee')
    if user_row.get('lycee_pro', 0) == 1:
        niveaux.append('lycee_pro')

    return {
        "user_id": user_id,
        "profile": {
            "anciennete": int(user_row.get('anciennete', 0)) if pd.notna(user_row.get('anciennete')) else None,
            "degre": int(user_row.get('degre', 0)) if pd.notna(user_row.get('degre')) else None,
            "academie": user_row.get('academie') if pd.notna(user_row.get('academie')) else "Non renseignée",
            "niveaux_enseignes": niveaux
        },
        "cluster": {
            "id": cluster_id,
            "name": cluster_info["name"],
            "description": cluster_info["description"]
        },
        "recommendations": recommendations
    }

# Recommendations based on clusters
# def get_recommendations_for_cluster(cluster_id: int):
#     """
#     Get recommendation strategy for each of the 5 real clusters
#     Based on the business personas and behavioral patterns identified
#     """

#     if cluster_id not in range(5):
#         return {
#             "error": "Invalid cluster ID",
#             "available_clusters": [0, 1, 2, 3, 4]
#         }

#     # Load personas for detailed recommendations
#     _, _, _, _, personas = load_clustering_models()
#     persona = personas[str(cluster_id)]

#     recommendations = {
#         0: {  # Peu Engagés Primaire
#             "cluster_name": "Peu Engagés Primaire",
#             "strategy": "Réactivation douce avec contenu très accessible",
#             "recommended_content_types": [
#                 "Infographies visuelles",
#                 "Vidéos courtes",
#                 "Fiches outils simples",
#                 "Contenus maternelle/élémentaire spécialisés"
#             ],
#             "engagement_approach": "low_barrier_reengagement",
#             "priority_challenges": ["Réussite de tous les élèves", "Santé mentale"],
#             "communication_style": "Encourageant et non-intimidant",
#             "next_steps": "Contenu d'entrée de gamme pour recréer l'habitude de consultation"
#         },

#         1: {  # Actifs Polyvalents
#             "cluster_name": "Actifs Polyvalents",
#             "strategy": "Maintenir l'engagement avec contenu varié et évolutif",
#             "recommended_content_types": [
#                 "Guides pratiques multi-niveaux",
#                 "Ateliers webinaires",
#                 "Contenus collaboratifs",
#                 "Parcours de formation courts"
#             ],
#             "engagement_approach": "diversified_continuous_engagement",
#             "priority_challenges": ["École inclusive", "Compétences psychosociales", "Réussite de tous les élèves"],
#             "communication_style": "Informatif et structuré",
#             "next_steps": "Contenu personnalisé selon leurs 3 topics de prédilection"
#         },

#         2: {  # Super Users
#             "cluster_name": "Super Users",
#             "strategy": "Contenu expert et avant-gardiste, opportunités de contribution",
#             "recommended_content_types": [
#                 "Recherches pédagogiques récentes",
#                 "Contenus expérimentaux",
#                 "Formations expertes",
#                 "Opportunités de mentorat/création",
#                 "Beta-testing nouveaux outils"
#             ],
#             "engagement_approach": "expert_community_involvement",
#             "priority_challenges": ["Tous les 5 défis", "Innovation pédagogique"],
#             "communication_style": "Technique et approfondi",
#             "next_steps": "Proposer de rejoindre l'équipe des créateurs de contenu"
#         },

#         3: {  # Email-Heavy
#             "cluster_name": "Email-Heavy",
#             "strategy": "Transition progressive de l'email vers la plateforme",
#             "recommended_content_types": [
#                 "Liens directs depuis emails vers contenus similaires",
#                 "Fiches outils téléchargeables",
#                 "Contenus courts et actionables",
#                 "Formats familiers (PDF, infographies)"
#             ],
#             "engagement_approach": "email_to_platform_conversion",
#             "priority_challenges": ["Efficacité pédagogique", "Gestion de classe"],
#             "communication_style": "Pratique et immédiatement utilisable",
#             "next_steps": "Gamification douce de la transition vers la plateforme"
#         },

#         4: {  # Peu Engagés Secondaire
#             "cluster_name": "Peu Engagés Secondaire",
#             "strategy": "Réactivation avec contenu spécialisé secondaire",
#             "recommended_content_types": [
#                 "Contenus spécifiques collège/lycée",
#                 "Gestion de classe adolescents",
#                 "Outils disciplinaires",
#                 "Contenus courts et percutants"
#             ],
#             "engagement_approach": "secondary_specialized_reengagement",
#             "priority_challenges": ["Motivation des élèves", "Orientation", "Compétences psychosociales"],
#             "communication_style": "Pragmatique et orienté résultats",
#             "next_steps": "Contenu hyper-ciblé sur leurs défis spécifiques du secondaire"
#         }
#     }

#     # Enrich with persona data
#     recommendation = recommendations[cluster_id]
#     recommendation.update({
#         "cluster_size": persona["taille"],
#         "main_teaching_level": persona["niveau_principal"],
#         "activity_profile": {
#             "activite_generale": persona["activite_generale"],
#             "engagement_email": persona["engagement_email"],
#             "usage_contenu": persona["usage_contenu"],
#             "diversite_thematique": persona["diversite_thematique"]
#         }
#     })

#     return recommendation

# def get_recommendations_for_cluster(cluster_id: int):
#     """
#     Get real recommendation strategy for each of the 5 clusters
#     Now using the actual recommendation engine
#     """

#     if cluster_id not in range(5):
#         return {
#             "error": "Invalid cluster ID",
#             "available_clusters": [0, 1, 2, 3, 4]
#         }

#     recommendations = generate_recommendations_for_cluster(cluster_id, num_recommendations=4)

#     # Load personas for business context
#     _, _, _, _, personas = load_clustering_models()
#     persona = personas[str(cluster_id)]

#     # Format for API response
#     formatted_response = {
#         "cluster_id": cluster_id,
#         "cluster_name": persona["nom"],
#         "cluster_description": {
#             "taille": persona["taille"],
#             "niveau_principal": persona["niveau_principal"],
#             "activite_generale": persona["activite_generale"],
#             "engagement_email": persona["engagement_email"],
#             "usage_contenu": persona["usage_contenu"],
#             "diversite_thematique": persona["diversite_thematique"]
#         },
#         "recommendation_strategy": {
#             "top_topics": recommendations.get("reasoning", {}).get("top_topics", []),
#             "selection_strategy": recommendations.get("reasoning", {}).get("selection_strategy", "")
#         },
#         "recommended_contents": recommendations.get("recommendations", []),
#         "total_recommendations": len(recommendations.get("recommendations", [])),
#         "system_status": "Production - Real recommendation engine with topic-based personalization"
#     }

#     return formatted_response
