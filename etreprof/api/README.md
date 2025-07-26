# ÊtrePROF ML API

Machine Learning API for content classification, user clustering, and personalized recommendations for the ÊtrePROF educational platform.

## 🚀 Features

- **Content Classification**: Analyze markdown content to identify themes and priority challenges
- **User Clustering**: Segment users into 4 behavioral clusters based on platform usage
- **Personalized Recommendations**: Content strategy recommendations based on user cluster
- **User Profiles**: Complete user profile lookup with cluster assignment

## 📋 API Endpoints

### Health Check
```http
GET /
```
Returns API status and welcome message.

### Content Classification
```http
POST /classify
Content-Type: application/json

{
  "content": "# Teaching mathematics\n\nStrategies for differentiated learning..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "theme": "Mathematics Education",
    "defi": "student_success"
  }
}
```

### User Clustering

#### Get Cluster Information
```http
GET /clusters
```

**Response:**
```json
{
  "success": true,
  "clusters": {
    "0": {
      "name": "Balanced Users",
      "count": 15234,
      "profile": {
        "nb_fiche_outils": 8.94,
        "total_interactions_x": 21.58,
        ...
      }
    },
    "1": {
      "name": "Email Specialists",
      "count": 8756,
      ...
    },
    "2": {
      "name": "Super Users",
      "count": 2341,
      ...
    },
    "3": {
      "name": "Inactive Users",
      "count": 28408,
      ...
    }
  }
}
```

#### Recompute Clusters
```http
POST /clusters/recompute
```

Recalculates user clusters using the complete data processing pipeline.

**Response:**
```json
{
  "success": true,
  "message": "Clusters recomputed successfully",
  "total_users_processed": 54739,
  "cluster_distribution": {
    "cluster_0": 15234,
    "cluster_1": 8756,
    "cluster_2": 2341,
    "cluster_3": 28408
  }
}
```

### Recommendations

#### Get Recommendations by Cluster
```http
GET /recommend/{cluster_id}
```

**Parameters:**
- `cluster_id` (int): Cluster ID (0, 1, 2, or 3)

**Response:**
```json
{
  "success": true,
  "cluster_id": 2,
  "recommendations": {
    "cluster_name": "Super Users",
    "strategy": "Advanced content and latest innovations",
    "recommended_content_types": ["expert_training", "advanced_guides", "cutting_edge_tools"],
    "engagement_approach": "satisfy_high_expertise_needs",
    "description": "Highly engaged users consuming diverse content types intensively",
    "next_steps": "Advanced recommendations will leverage thematic preferences analysis"
  },
  "status": "MVP - Behavioral recommendations only. Thematic personalization coming soon."
}
```

### User Profiles

#### Get User Profile
```http
GET /user/{user_id}/profile
```

**Parameters:**
- `user_id` (int): User identifier

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": 12345,
    "profile": {
      "anciennete": 15,
      "degre": 2,
      "academie": "Paris",
      "niveaux_enseignes": ["college", "lycee"]
    },
    "cluster": {
      "id": 2,
      "name": "Super Users"
    },
    "recommendations": {
      "cluster_name": "Super Users",
      "strategy": "Advanced content and latest innovations",
      "recommended_content_types": ["expert_training", "advanced_guides"],
      ...
    }
  }
}
```

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t etreprof-api .
```

### Run Locally
```bash
docker run -p 8000:8000 -e PORT=8000 etreprof-api
```

### Deploy to Google Cloud Run
```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/etreprof-api

# Deploy to Cloud Run
gcloud run deploy etreprof-api \
  --image gcr.io/PROJECT_ID/etreprof-api \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated
```

## 📊 Data Sources

The API relies on:
- **User behavioral data**: Interaction patterns, content consumption, email engagement
- **Content metadata**: Themes, priority challenges, content types
- **Clustering models**: Pre-trained K-means model with 4 clusters

## 🏗️ Architecture

```
etreprof/
├── api/
│   └── main.py              # FastAPI application
├── ml_package/
│   ├── models.py            # ML models and functions
│   └── pickles/             # Trained models (KMeans, Scaler, etc.)
├── data_processing/
│   └── user_full_processing.py  # Data pipeline
└── data/
    ├── cluster_profiles.csv      # Cluster characteristics
    └── user_cluster_assignments.csv  # User→cluster mappings
```

## 🔮 Cluster Definitions

| Cluster | Name | Description | Strategy |
|---------|------|-------------|----------|
| 0 | Balanced Users | Moderate, diversified usage | Varied content approach |
| 1 | Email Specialists | High email engagement, low content usage | Transition to platform content |
| 2 | Super Users | Highly engaged across all features | Advanced content and innovations |
| 3 | Inactive Users | Low engagement across platform | Re-engagement and accessibility |

## 📈 Future Enhancements

- **Thematic clustering**: Incorporate content preferences
- **Real-time recommendations**: Content-based filtering
- **A/B testing**: Recommendation effectiveness tracking
- **BigQuery integration**: Direct database connectivity
- **Caching layer**: Improved response times

## 📝 License

This project is developed for ÊtrePROF by Ecolhuma.
