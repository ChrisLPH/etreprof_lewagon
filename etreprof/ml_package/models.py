import os
import pickle
import pandas as pd
from typing import Dict
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import json
import numpy as np

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
    profiles_path = os.path.join(os.path.dirname(os.path.dirname(ROOT_PATH)), 'data/cluster_profiles.csv')

    kmeans = pickle.load(open(kmeans_path, 'rb'))
    scaler = pickle.load(open(scaler_path, 'rb'))
    profiles = pd.read_csv(profiles_path, index_col=0)

    return kmeans, scaler, profiles

def get_cluster_info():
    _, _, profiles = load_clustering_models()

    return {
        0: {"name": "Balanced Users", "profile": profiles.loc[0].to_dict()},
        1: {"name": "Email Specialists", "profile": profiles.loc[1].to_dict()},
        2: {"name": "Super Users", "profile": profiles.loc[2].to_dict()},
        3: {"name": "Inactive Users", "profile": profiles.loc[3].to_dict()}
    }

# Update clustering of users
def predict_user_clusters(df_users):
    kmeans, scaler, _ = load_clustering_models()

    behavior_cols = [
        'nb_fiche_outils', 'nb_guide_pratique', 'nb_transition_ecologique',
        'nb_sante_mentale', 'nb_ecole_inclusive', 'nb_cps', 'nb_reussite_tous_eleves',
        'total_interactions_x', 'diversite_contenus', 'nb_vote', 'nb_comments',
        'nb_opened_mail', 'nb_clicked_mail'
    ]

    X_scaled = scaler.transform(df_users[behavior_cols])
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

    recommendations = get_recommendations_for_cluster(cluster_id)

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
            "name": cluster_info["name"]
        },
        "recommendations": recommendations
    }

# Recommendations based on clusters
def get_recommendations_for_cluster(cluster_id: int):
    """
    Get recommendation strategy for a specific cluster based on behavioral patterns.
    Content suggestions will be enhanced once clustering is updated with thematic preferences.
    """

    recommendations = {
        0: {  # Balanced Users
            "cluster_name": "Balanced Users",
            "strategy": "Varied and balanced content approach",
            "recommended_content_types": ["tool_sheets", "practical_guides", "webinars"],
            "engagement_approach": "maintain_steady_engagement",
            "description": "Users with moderate and diversified platform usage",
            "next_steps": "Content suggestions will be personalized once thematic clustering is implemented"
        },
        1: {  # Email Specialists
            "cluster_name": "Email Specialists",
            "strategy": "Gentle transition from email to platform content",
            "recommended_content_types": ["tool-sheets", "infographics", "short-videos"],
            "engagement_approach": "convert_to_content_consumption",
            "description": "Highly active on emails but minimal platform content usage",
            "next_steps": "Email-to-content bridge strategies will be refined with thematic data"
        },
        2: {  # Super Users
            "cluster_name": "Super Users",
            "strategy": "Advanced content and latest innovations",
            "recommended_content_types": ["research_content", "mooc", "join_expert_team"],
            "engagement_approach": "satisfy_high_expertise_needs",
            "description": "Highly engaged users consuming diverse content types intensively",
            "next_steps": "Advanced recommendations will leverage thematic preferences analysis"
        },
        3: {  # Inactive Users
            "cluster_name": "Inactive Users",
            "strategy": "Re-engagement with accessible entry-point content",
            "recommended_content_types": ["quick_videos", "simple_checklists", "visual_infographics"],
            "engagement_approach": "anti_churn_activation",
            "description": "Low engagement across all platform features",
            "next_steps": "Targeted re-engagement content will be optimized with thematic insights"
        }
    }

    return recommendations.get(cluster_id, {
        "error": "Invalid cluster ID",
        "available_clusters": [0, 1, 2, 3]
    })
