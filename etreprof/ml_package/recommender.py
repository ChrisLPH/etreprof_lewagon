import os
import pandas as pd
import random
from typing import Dict, Any

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

def load_recommendations_csv():
    """
    Load the content recommendations mapping CSV file.
    Returns:
    -------
    pd.DataFrame: DataFrame containing content recommendations.
    If the file does not exist, returns None.
    If there is an error during loading, returns None and prints the error.
    """
    csv_path = os.path.join(os.path.dirname(os.path.dirname(ROOT_PATH)), 'data/content_recommendations_mapping.csv')

    try:
        df_reco = pd.read_csv(csv_path)
        return df_reco
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {csv_path}")
        return None
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")
        return None

def build_url(content_id, content_type):
    """
    Construit l'URL appropriée en fonction du type de contenu.

    Parameters:
    -----------
    content_id : int ou str
        L'identifiant du contenu
    content_type : str
        Le type de contenu (article, fiche_outils, guide_pratique, etc.)

    Returns:
    --------
    str : L'URL complète du contenu
    """
    if pd.isna(content_id):
        return ''

    if content_type == 'fiche_outils':
        return f"https://etreprof.fr/fiches-outils/{content_id}/fo"
    elif content_type == 'guide_pratique':
        return f"https://etreprof.fr/guides-pratiques/{content_id}/gp"
    elif content_type == 'article':
        return f"https://etreprof.fr/ressources/{content_id}"
    else:
        return "https://etreprof.fr"

def generate_simple_recommendations(cluster_id: int, num_recommendations: int = 5) -> Dict[str, Any]:
    """
    Generate simple recommendations based on a CSV mapping of content to clusters.
    Parameters
    ----------
    cluster_id : int
        The cluster ID for which to generate recommendations (0-4).
    num_recommendations : int
        The number of recommendations to generate (default is 5).
    Returns
    -------
    Dict[str, Any]: A dictionary containing the cluster ID, total recommendations,
                    and a list of recommended content with details.
                    If an error occurs, it returns an error message.
    """

    if cluster_id not in range(5):
        return {
            "error": "Invalid cluster ID. Must be 0, 1, 2, 3, or 4",
            "available_clusters": [0, 1, 2, 3, 4]
        }

    # Load the recommendations CSV
    df_reco = load_recommendations_csv()
    if df_reco is None:
        return {
            "error": "Could not load recommendations CSV",
            "cluster_id": cluster_id,
            "recommendations": []
        }

    try:
        # 1. Filter contents for the specified cluster
        cluster_column = f'cluster_{cluster_id}'
        if cluster_column not in df_reco.columns:
            return {
                "error": f"Column {cluster_column} not found in CSV",
                "cluster_id": cluster_id,
                "recommendations": []
            }

        cluster_contents = df_reco[df_reco[cluster_column] == True].copy()

        if len(cluster_contents) == 0:
            return {
                "error": f"No content available for cluster {cluster_id}",
                "cluster_id": cluster_id,
                "recommendations": []
            }

        # 2. Separate normal contents and priority challenges
        normal_contents = cluster_contents[cluster_contents['priority_challenge'].isna()].copy()
        priority_contents = cluster_contents[cluster_contents['priority_challenge'].notna()].copy()

        recommendations = []

        # 3. Select normal contents randomly
        num_normal = min(num_recommendations - 1, len(normal_contents))  # Leave space for 1 priority challenge

        if num_normal > 0:
            selected_normal = normal_contents.sample(n=num_normal, random_state=None).reset_index(drop=True)

            for _, content in selected_normal.iterrows():
                rec = {
                    'id': int(content['id']) if pd.notna(content['id']) else None,
                    'title': str(content['title']) if pd.notna(content['title']) else 'Titre non disponible',
                    'type': str(content['type']) if pd.notna(content['type']) else 'contenu',
                    'url': build_url(content['id'], content['type']),
                    'source': 'cluster_matching',
                    'reason': f'Contenu populaire pour votre profil',
                    'is_priority_challenge': False,
                    'priority_challenge': None
                }
                recommendations.append(rec)

        # 4. Select one priority challenge if available
        if len(priority_contents) > 0 and len(recommendations) < num_recommendations:
            selected_priority = priority_contents.sample(n=1, random_state=None).iloc[0]

            priority_rec = {
                'id': int(selected_priority['id']) if pd.notna(selected_priority['id']) else None,
                'title': str(selected_priority['title']) if pd.notna(selected_priority['title']) else 'Titre non disponible',
                'type': str(selected_priority['type']) if pd.notna(selected_priority['type']) else 'contenu',
                'url': build_url(selected_priority['id'], selected_priority['type']),
                'source': 'priority_challenge',
                'reason': f'Développement professionnel - {selected_priority["priority_challenge"]}',
                'is_priority_challenge': True,
                'priority_challenge': str(selected_priority['priority_challenge'])
            }
            recommendations.append(priority_rec)

        # 5. Compléter si on n'a pas assez de contenus
        while len(recommendations) < num_recommendations:
            # Prendre du contenu normal supplémentaire s'il y en a
            remaining_normal = normal_contents[~normal_contents['id'].isin([r['id'] for r in recommendations])]

            if len(remaining_normal) > 0:
                extra_content = remaining_normal.sample(n=1, random_state=None).iloc[0]

                extra_rec = {
                    'id': int(extra_content['id']) if pd.notna(extra_content['id']) else None,
                    'title': str(extra_content['title']) if pd.notna(extra_content['title']) else 'Titre non disponible',
                    'type': str(extra_content['type']) if pd.notna(extra_content['type']) else 'contenu',
                    'url': build_url(extra_content['id'], extra_content['type']),
                    'source': 'cluster_matching',
                    'reason': f'Contenu additionnel pour votre profil',
                    'is_priority_challenge': False,
                    'priority_challenge': None
                }
                recommendations.append(extra_rec)
            else:
                break

        # 6. Mélanger l'ordre des recommandations
        random.shuffle(recommendations)

        return {
            "cluster_id": cluster_id,
            "total_recommendations": len(recommendations),
            "recommendations": recommendations,
            "reasoning": {
                "strategy": "Sélection aléatoire basée sur topics populaires + 1 défi prioritaire",
                "available_contents": len(cluster_contents),
                "normal_contents": len(normal_contents),
                "priority_contents": len(priority_contents)
            },
            "system_status": "ok"
        }

    except Exception as e:
        return {
            "error": f"Error generating recommendations: {str(e)}",
            "cluster_id": cluster_id,
            "recommendations": []
        }
