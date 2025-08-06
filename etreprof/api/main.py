from fastapi import FastAPI
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from etreprof.ml_package.models import classify_content, get_cluster_info, predict_user_clusters, get_user_profile
from etreprof.data_processing.user_full_processing import main_process_users
from etreprof.ml_package.recommender import generate_simple_recommendations


app = FastAPI(title="ÊtrePROF Classification API", version="1.0.0")

@app.get("/")
def root():
    """Root endpoint to check if the API is running.
    Returns a simple greeting message.
    """
    return {"greetings": "Welcome to ÊtrePROF API!", "status": "running"}

@app.post("/classify")
def classify(content: str):
    """    Endpoint to classify content based on its type.
    Parameters
    ----------
    content : str
        The content to classify.
    """
    result = classify_content(content)
    return {"success": True, "data": result}

@app.get("/clusters")
def get_clusters():
    """Endpoint to get information about user clusters.
    Returns a dictionary with cluster IDs and their descriptions."""
    cluster_info = get_cluster_info()
    return {"success": True, "clusters": cluster_info}

@app.post("/clusters/recompute")
def recompute_clusters():
    """
    Endpoint to recompute user clusters based on the latest data.
    Returns a summary of the clustering process including the number of users processed and cluster distribution.
    IMPORTANT: This endpoint will reprocess the entire user dataset. It's intended for administrative use only.
    It's a long-running operation and should be used with caution.
    It won't be available on cloud run.
    """
    df_users = pd.read_csv(os.getenv("USER_URL_DB"), low_memory=False)
    df_contents = pd.read_csv(os.getenv("CONTENTS_URL_DB"), low_memory=False)
    df_interactions = pd.read_csv(os.getenv("INTERACTIONS_URL_DB"), low_memory=False)
    df_content_valid = pd.read_csv(os.getenv("CONTENT_WITH_TOPICS_URL_DB"), low_memory=False)

    df_users_processed = main_process_users(df_users, df_contents, df_content_valid, df_interactions)

    new_clusters = predict_user_clusters(df_users_processed)

    cluster_counts = pd.Series(new_clusters).value_counts().sort_index()

    return {
        "success": True,
        "message": "Clusters recomputed successfully",
        "total_users_processed": len(df_users_processed),
        "cluster_distribution": {
            "cluster_0": int(cluster_counts.get(0, 0)),
            "cluster_1": int(cluster_counts.get(1, 0)),
            "cluster_2": int(cluster_counts.get(2, 0)),
            "cluster_3": int(cluster_counts.get(3, 0)),
            "cluster_4": int(cluster_counts.get(4, 0))
        },
        "processing_time": "calculated in real-time"
    }

@app.get("/user/{user_id}/profile")
def get_user_profile_endpoint(user_id: int):
    """Endpoint to get the profile of a user by their ID.
    Parameters
    ----------
    user_id : int
        The ID of the user whose profile is requested.
    Returns
    -------
    dict : A dictionary containing the user's profile data or an error message if the user is not found.
    """
    profile_data = get_user_profile(user_id)

    if "error" in profile_data:
        return {
            "success": False,
            "error": profile_data["error"]
        }

    return {
        "success": True,
        "data": profile_data
    }

@app.get("/recommend/{cluster_id}")
def get_recommendations(cluster_id: int):
    if cluster_id not in [0, 1, 2, 3, 4]:
        return {
            "success": False,
            "error": "Cluster ID must be 0, 1, 2, 3, or 4",
            "available_clusters": [0, 1, 2, 3, 4]
        }

    recommendations = generate_simple_recommendations(cluster_id)

    return {
        "success": True,
        "cluster_id": cluster_id,
        "recommendations": recommendations,
        "status": "Cluster recommendations generated successfully"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
