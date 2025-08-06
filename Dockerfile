FROM python:3.10-slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY etreprof etreprof
COPY setup.py setup.py

RUN mkdir -p data

COPY data/cluster_profiles.csv data/
COPY data/cluster_personas.json data/
COPY data/cluster_personas_lisibles.json data/
COPY data/user_cluster_assignments.csv data/
COPY data/users_final_with_clusters.csv data/
COPY data/content_with_topics.csv data/
COPY data/content_recommendations_mapping.csv data/

RUN pip install -e .

CMD uvicorn etreprof.api.main:app --host 0.0.0.0 --port $PORT
