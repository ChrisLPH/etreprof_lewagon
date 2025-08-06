import os
import pickle
import pandas as pd
from typing import Dict
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import json
from .recommender import generate_simple_recommendations

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

# Content classification function
def classify_content(content: str) -> Dict:
    """
    Classify content using BERTopic model trained by Guillaume
    Returns top 3 topics with confidence scores.
    Parameters
    ----------
    content : str
        The content to classify.
    Returns
    -------
    Dict
        A dictionary with the main topic ID, label, and confidence score.
    """
    bertopic_path = os.path.join(ROOT_PATH, 'pickles/bertopic')
    topics_json_path = os.path.join(bertopic_path, 'topics.json')

    # Load topics.json to get topic labels
    with open(topics_json_path, 'r', encoding='utf-8') as f:
        topics_data = json.load(f)

    topic_labels = topics_data['topic_labels']

    # Load the model
    embedding_model = SentenceTransformer('intfloat/multilingual-e5-large-instruct', device='cpu')
    topic_model = BERTopic.load(bertopic_path, embedding_model=embedding_model)

    # Prediction
    topics, scores = topic_model.transform([content])

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
    """
    Load clustering models and metadata.
    Returns
    -------
    Tuple
        A tuple containing the KMeans model, scaler, metadata, cluster profiles, and personas.
    """
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
    """
    Get information about all 5 clusters with real data
    Returns
    -------
    Dict
        A dictionary containing cluster information including name, count, percentage, description, and profile.
    """
    _, _, _, profiles, personas = load_clustering_models()

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
    """
    Predict user clusters based on features used in clustering.
    Parameters
    ----------
    df_users : pandas.DataFrame
        DataFrame containing user features.
    Returns
    -------
    numpy.ndarray
        Array of predicted cluster labels for each user."""
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

# Get user profile by ID
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
