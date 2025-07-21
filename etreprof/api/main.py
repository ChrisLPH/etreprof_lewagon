from fastapi import FastAPI
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_package import ContentClassifier, UserClustering, ContentRecommender

app = FastAPI(
    title="ÊtrePROF ML API",
    description="API pour la classification de contenu, clustering utilisateurs et recommandations",
    version="0.1.0"
)

print("🚀 Initialisation des modèles ML...")

classifier = ContentClassifier()
clusterer = UserClustering(n_clusters=6)
recommender = ContentRecommender()

print("✅ Modèles ML initialisés avec succès !")


@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "It's Alive !"
    }


@app.get("/health")
async def health_check():
    """Health check de l'API"""
    return {
        "status": "healthy",
        "models_loaded": {
            "classifier": True,
            "clusterer": True,
            "recommender": True
        }
    }


# ML endpoints
@app.post("/content/classify")
async def classify_content(markdown_text: str):
    """
    Classifie un contenu markdown en thème + défi prioritaire

    Args:
        markdown_text: Le contenu markdown à analyser

    Returns:
        Classification avec thème principal, défi prioritaire et scores de confiance
    """
    try:
        result = classifier.get_top_predictions(markdown_text)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/users/clusters")
async def get_clusters_info():
    """
    Retourne les informations sur tous les clusters d'utilisateurs

    Returns:
        Informations détaillées sur chaque cluster
    """
    try:
        clusters_info = clusterer.get_cluster_info()
        return {
            "success": True,
            "data": clusters_info
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/users/clusters/summary")
async def get_clusters_summary():
    """
    Retourne un résumé des clusters sous forme de tableau

    Returns:
        Résumé des clusters avec tailles et caractéristiques principales
    """
    try:
        summary = clusterer.get_cluster_summary()
        return {
            "success": True,
            "data": summary.to_dict('records')
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/recommend/{cluster_id}")
async def get_recommendations(cluster_id: int, n_recommendations: int = 5):
    """
    Génère des recommandations pour un cluster spécifique

    Args:
        cluster_id: ID du cluster (0 à 7)
        n_recommendations: Nombre de recommandations à retourner (défaut: 5)

    Returns:
        Liste des recommandations avec scores et justifications
    """
    try:
        recs = recommender.get_recommendations_for_cluster(cluster_id, n_recommendations)
        return {
            "success": True,
            "cluster_id": cluster_id,
            "data": recs.to_dict('records')
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
