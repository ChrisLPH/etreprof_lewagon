import pickle
import os
from sklearn.dummy import DummyClassifier
import numpy as np

# Créer des modèles sklearn simples mockés
def create_simple_pickles():

    # Thèmes (30 classes)
    themes = [
        "Gérer ma classe", "Faire progresser mes élèves",
        "Gérer les besoins spécifiques (DYS, handicap, TSA…)",
        "Gérer les relations au travail (collègues, direction, parents)",
        "Ma vie de prof (équilibre pro‑perso, santé mentale, gestion du stress)",
        "Enrichir ma pédagogie", "Ressources par matière (français, maths, sciences, langues vivantes…)",
        "Activités maternelle", "Activités élémentaire / cycle 2–3",
        "Activités collège & lycée", "Fiches outils (guides pratiques synthétiques)",
        "Guides pratiques thématiques", "Kits d'accompagnement (par mail ou parcours progressifs)",
        "Ateliers thématiques (en ligne)", "Lives & webinaires",
        "Tutos vidéo (capsules courtes)", "Parcours structurés (modules thématiques diplômants ou progressions)",
        "Rituels de classe (accueil, maths, français, anglais…)", "Différenciation & pédagogie inclusive",
        "Évaluation & suivi des progrès", "Gestion du comportement & autorité",
        "Organisation & outils numériques", "Préparation de la rentrée",
        "Continuité pédagogique / enseignement à distance", "Bien-être professionnel",
        "Développement de l'autonomie des élèves", "Thématiques socio‑culturelles (laïcité, inclusion, engagement citoyen)",
        "Motivation et engagement des élèves", "Coopération & travail en groupe",
        "Partage d'expériences & témoignages de profs"
    ]

    # Défis (6 classes)
    defis = ["aucun_defi", "transition_ecologique", "sante_mentale",
             "ecole_inclusive", "competences_psychosociales", "reussite_tous_eleves"]

    # Créer des modèles sklearn mockés
    theme_model = DummyClassifier(strategy="uniform", random_state=42)
    defi_model = DummyClassifier(strategy="uniform", random_state=42)

    # "Entraîner" avec des données fictives
    X_fake = np.random.rand(100, 10)  # 100 samples, 10 features
    y_themes = np.random.choice(themes, 100)
    y_defis = np.random.choice(defis, 100)

    theme_model.fit(X_fake, y_themes)
    defi_model.fit(X_fake, y_defis)

    # Sauvegarder
    os.makedirs("ml_package/pickles", exist_ok=True)

    with open("ml_package/pickles/theme_model.pkl", "wb") as f:
        pickle.dump(theme_model, f)

    with open("ml_package/pickles/defi_model.pkl", "wb") as f:
        pickle.dump(defi_model, f)

    print("✅ Pickles sklearn simples créés!")
    return theme_model, defi_model

if __name__ == "__main__":
    create_simple_pickles()
