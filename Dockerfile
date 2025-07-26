FROM python:3.10-slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY etreprof etreprof
COPY data/cluster_profiles.csv data/cluster_profiles.csv
COPY data/user_cluster_assignments.csv data/user_cluster_assignments.csv
COPY setup.py setup.py

RUN pip install -e .

CMD uvicorn etreprof.api.main:app --host 0.0.0.0 --port $PORT
