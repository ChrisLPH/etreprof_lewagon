import os
import pandas as pd
import numpy as np
import json
from typing import List, Dict, Any
from collections import Counter

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

def load_recommendation_data():
    """
    Load all necessary data for recommendations

    Returns:
    --------
    tuple: (df_users, df_contents, df_content_with_topics)
    """
    # Load user data with clusters and topics
    users_path = os.path.join(os.path.dirname(os.path.dirname(ROOT_PATH)), 'data/users_final_with_clusters.csv')
    df_users = pd.read_csv(users_path)

    # Load content data
    # Note: Assuming we have access to the processed contents with topics
    # You might need to adjust these paths based on your actual data structure
    try:
        # Try to load content with topics (if available)
        content_topics_path = os.path.join(os.path.dirname(os.path.dirname(ROOT_PATH)), 'data/content_with_topics.csv')
        df_content_with_topics = pd.read_csv(content_topics_path)
    except FileNotFoundError:
        df_content_with_topics = None

    # Load basic content data (from environment or local)
    try:
        from dotenv import load_dotenv
        load_dotenv()

        contents_url = os.getenv("CONTENTS_URL_DB")
        if contents_url:
            df_contents = pd.read_csv(contents_url, low_memory=False)
        else:
            # Fallback to local path
            contents_local_path = os.path.join(os.path.dirname(os.path.dirname(ROOT_PATH)), 'raw_data/contents_v3.csv')
            df_contents = pd.read_csv(contents_local_path, low_memory=False)
    except:
        # Last fallback - empty dataframe with expected structure
        df_contents = pd.DataFrame(columns=['id', 'title', 'type', 'transition_ecologique', 'sante_mentale',
                                          'ecole_inclusive', 'cps', 'reussite_tous_eleves'])

    return df_users, df_contents, df_content_with_topics


def get_top_topics_for_cluster(df_users: pd.DataFrame, cluster_id: int, top_n: int = 3) -> List[int]:
    """
    Get the most popular topics for a specific cluster

    Parameters:
    -----------
    df_users : pd.DataFrame
        User dataframe with cluster assignments and topic columns
    cluster_id : int
        Cluster ID (0-4)
    top_n : int
        Number of top topics to return

    Returns:
    --------
    List[int]: List of topic IDs sorted by popularity in the cluster
    """
    # Filter users by cluster
    cluster_users = df_users[df_users['cluster'] == cluster_id]

    if cluster_users.empty:
        return []

    # Find topic columns (assuming they start with 'topic_')
    topic_columns = [col for col in df_users.columns if col.startswith('topic_') and col != 'topic_count']

    if not topic_columns:
        return []

    # Calculate topic popularity in the cluster
    topic_scores = {}

    for topic_col in topic_columns:
        # Extract topic ID from column name (e.g., 'topic_0' -> 0, 'topic_-1' -> -1)
        try:
            topic_id = int(topic_col.replace('topic_', ''))
            # Sum of interactions for this topic in the cluster
            topic_scores[topic_id] = cluster_users[topic_col].sum()
        except ValueError:
            continue

    # Sort topics by popularity and return top N
    sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
    top_topics = [topic_id for topic_id, score in sorted_topics[:top_n] if score > 0]

    return top_topics


def get_contents_by_topics(df_content_with_topics: pd.DataFrame, df_contents: pd.DataFrame,
                          topic_ids: List[int], content_type: str = None, limit: int = 10) -> pd.DataFrame:
    """
    Get contents that match specific topics

    Parameters:
    -----------
    df_content_with_topics : pd.DataFrame
        Content dataframe with topic assignments
    df_contents : pd.DataFrame
        Content dataframe with full metadata (title, type, url, etc.)
    topic_ids : List[int]
        List of topic IDs to filter by
    content_type : str, optional
        Filter by content type ('article', 'fiche_outils', etc.)
    limit : int
        Maximum number of contents to return

    Returns:
    --------
    pd.DataFrame: Filtered contents with full metadata
    """
    if df_content_with_topics is None or df_content_with_topics.empty:
        return pd.DataFrame()

    # Merge content_with_topics with full content metadata
    df_content_full = df_content_with_topics.merge(
        df_contents[['id', 'title', 'type', 'url']],
        on='id',
        how='inner'
    )
    # Find topic column
    topic_col = None
    if 'reduced topics' in df_content_full.columns:
        topic_col = 'reduced topics'
    elif 'topics' in df_content_full.columns:
        topic_col = 'topics'
    elif 'topic_id' in df_content_full.columns:
        topic_col = 'topic_id'

    if topic_col is None:
        return pd.DataFrame()

    # Filter by topics
    filtered_contents = df_content_full[df_content_full[topic_col].isin(topic_ids)]

    # Filter by content type if specified
    if content_type and 'type' in filtered_contents.columns:
        filtered_contents = filtered_contents[filtered_contents['type'] == content_type]

    # Shuffle and limit
    if not filtered_contents.empty:
        filtered_contents = filtered_contents.sample(n=min(len(filtered_contents), limit),
                                                   random_state=42).reset_index(drop=True)

    return filtered_contents


def get_priority_challenge_content(df_contents: pd.DataFrame, exclude_ids: List[int] = None) -> Dict[str, Any]:
    """
    Get a random content from a priority challenge

    Parameters:
    -----------
    df_contents : pd.DataFrame
        Content dataframe with priority challenge columns
    exclude_ids : List[int], optional
        Content IDs to exclude from selection

    Returns:
    --------
    Dict: Content information with challenge type
    """
    if df_contents.empty:
        return {}

    exclude_ids = exclude_ids or []

    # Priority challenge columns
    challenge_columns = [
        'transition_ecologique', 'sante_mentale', 'ecole_inclusive',
        'cps', 'reussite_tous_eleves'
    ]

    challenge_names = {
        'transition_ecologique': 'Transition écologique',
        'sante_mentale': 'Santé mentale',
        'ecole_inclusive': 'École inclusive',
        'cps': 'Compétences psychosociales',
        'reussite_tous_eleves': 'Réussite de tous les élèves'
    }

    # Find contents that have at least one priority challenge
    challenge_contents = df_contents.copy()

    # Filter out already selected contents
    if exclude_ids:
        challenge_contents = challenge_contents[~challenge_contents['id'].isin(exclude_ids)]

    # Filter contents that have at least one challenge marked as 1
    has_challenge = pd.DataFrame()
    for col in challenge_columns:
        if col in challenge_contents.columns:
            challenge_mask = challenge_contents[col] == 1
            if challenge_mask.any():
                challenge_subset = challenge_contents[challenge_mask].copy()
                challenge_subset['challenge_type'] = challenge_names[col]
                has_challenge = pd.concat([has_challenge, challenge_subset], ignore_index=True)

    if has_challenge.empty:
        return {}

    # Select a random content
    selected_content = has_challenge.sample(n=1, random_state=np.random.randint(0, 10000)).iloc[0]

    return {
        'id': int(selected_content['id']) if pd.notna(selected_content['id']) else None,
        'title': selected_content.get('title', 'Contenu sans titre'),
        'type': selected_content.get('type', 'contenu'),
        'challenge_type': selected_content.get('challenge_type', 'Développement professionnel'),
        'url': selected_content.get('url', ''),
        'is_priority_challenge': True
    }


def generate_recommendations_for_cluster(cluster_id: int, num_recommendations: int = 4) -> Dict[str, Any]:
    """
    Generate personalized recommendations for a specific cluster

    Parameters:
    -----------
    cluster_id : int
        Cluster ID (0-4)
    num_recommendations : int
        Total number of recommendations to generate (default: 4)

    Returns:
    --------
    Dict: Recommendations with content details and reasoning
    """
    if cluster_id not in range(5):
        return {
            "error": "Invalid cluster ID",
            "available_clusters": [0, 1, 2, 3, 4]
        }

    # Load data
    df_users, df_contents, df_content_with_topics = load_recommendation_data()

    recommendations = {
        "cluster_id": cluster_id,
        "cluster_name": f"Cluster {cluster_id}",
        "total_recommendations": num_recommendations,
        "recommendations": [],
        "reasoning": {
            "top_topics": [],
            "selection_strategy": "Topics populaires + défis prioritaires"
        }
    }

    try:
        # Get top topics for this cluster
        top_topics = get_top_topics_for_cluster(df_users, cluster_id, top_n=3)
        recommendations["reasoning"]["top_topics"] = top_topics

        selected_content_ids = []

        # Strategy: 2 articles + 1 fiche outil from popular topics
        if df_content_with_topics is not None and not df_content_with_topics.empty and top_topics:

            # Get 2 articles from popular topics
            articles = get_contents_by_topics(df_content_with_topics, df_contents, top_topics,
                                            content_type='article', limit=2)

            for _, article in articles.iterrows():
                content_info = {
                    'id': int(article['id']) if pd.notna(article['id']) else None,
                    'title': str(article.get('title', 'Article sans titre')),
                    'type': str(article.get('type', 'article')),
                    'topic_match': True,
                    'url': str(article.get('url', '')),
                    'is_priority_challenge': False,
                    'reason': f"Populaire dans votre cluster (Topic {article.get('reduced topics', 'N/A')})"
                }
                recommendations["recommendations"].append(content_info)
                if content_info['id']:
                    selected_content_ids.append(content_info['id'])

            # Get 1 fiche outil from popular topics
            fiches = get_contents_by_topics(df_content_with_topics, df_contents, top_topics,
                                          content_type='fiche-outils', limit=1)

            for _, fiche in fiches.iterrows():
                content_info = {
                    'id': int(fiche['id']) if pd.notna(fiche['id']) else None,
                    'title': str(fiche.get('title', 'Fiche outil sans titre')),
                    'type': str(fiche.get('type', 'fiche-outils')),
                    'topic_match': True,
                    'url': str(fiche.get('url', '')),
                    'is_priority_challenge': False,
                    'reason': f"Outil pratique populaire (Topic {fiche.get('reduced topics', 'N/A')})"
                }
                recommendations["recommendations"].append(content_info)
                if content_info['id']:
                    selected_content_ids.append(content_info['id'])

        # Add 1 priority challenge content
        challenge_content = get_priority_challenge_content(df_contents, exclude_ids=selected_content_ids)
        if challenge_content:
            # Ensure all values are JSON serializable
            challenge_content['id'] = int(challenge_content['id']) if challenge_content.get('id') and pd.notna(challenge_content['id']) else None
            challenge_content['title'] = str(challenge_content.get('title', ''))
            challenge_content['type'] = str(challenge_content.get('type', ''))
            challenge_content['url'] = str(challenge_content.get('url', ''))
            challenge_content['challenge_type'] = str(challenge_content.get('challenge_type', ''))
            challenge_content['reason'] = f"Développement professionnel - {challenge_content.get('challenge_type', 'Défi prioritaire')}"
            recommendations["recommendations"].append(challenge_content)

        # Fill remaining slots with fallback content if needed
        while len(recommendations["recommendations"]) < num_recommendations:
            # Add fallback generic content
            fallback_content = {
                'id': None,
                'title': f'Contenu recommandé #{len(recommendations["recommendations"]) + 1}',
                'type': 'contenu',
                'topic_match': False,
                'url': '',
                'is_priority_challenge': False,
                'reason': 'Contenu général recommandé'
            }
            recommendations["recommendations"].append(fallback_content)

    except Exception as e:
        recommendations["error"] = f"Erreur lors de la génération des recommandations: {str(e)}"
        recommendations["recommendations"] = []

    # Convert numpy types to native Python types for JSON serialization
    def clean_for_json(obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj) if not np.isnan(obj) else None
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        return obj

    # Clean all data for JSON serialization
    recommendations["cluster_id"] = int(recommendations["cluster_id"])
    recommendations["total_recommendations"] = int(recommendations["total_recommendations"])

    # Clean reasoning data
    if "reasoning" in recommendations:
        recommendations["reasoning"]["top_topics"] = [int(t) if pd.notna(t) else None for t in recommendations["reasoning"]["top_topics"]]

    return recommendations


def get_user_recommendations(user_id: int, num_recommendations: int = 4) -> Dict[str, Any]:
    """
    Get personalized recommendations for a specific user

    Parameters:
    -----------
    user_id : int
        User ID
    num_recommendations : int
        Number of recommendations to generate

    Returns:
    --------
    Dict: User recommendations with cluster context
    """
    try:
        # Load user data to find cluster
        df_users, _, _ = load_recommendation_data()

        user_data = df_users[df_users['id'] == user_id]

        if user_data.empty:
            return {
                "error": f"User {user_id} not found",
                "user_id": user_id,
                "recommendations": []
            }

        cluster_id = int(user_data.iloc[0]['cluster'])

        # Generate cluster-based recommendations
        recommendations = generate_recommendations_for_cluster(cluster_id, num_recommendations)

        # Add user context
        recommendations["user_id"] = user_id
        recommendations["user_cluster"] = cluster_id

        return recommendations

    except Exception as e:
        return {
            "error": f"Erreur lors de la génération des recommandations pour l'utilisateur {user_id}: {str(e)}",
            "user_id": user_id,
            "recommendations": []
        }
