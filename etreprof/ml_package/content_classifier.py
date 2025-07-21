"""
Content Classification Module
Classifie automatiquement le contenu markdown en thématiques et défis prioritaires.

Version MOCK pour développement - à remplacer par les vrais modèles de l'équipe

Généré par IA pour simuler le comportement d'un classifieur de contenu en attendant l'intégration de modèles NLP réels.
Utilise des mots-clés bidons et des scores aléatoires pour la démonstration de la logique de classification.
A utiliser uniquement pour les tests et la démonstration de l'interface utilisateur.
Ne pas utiliser en production.
"""

import random
import re
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


class ContentClassifier:
    """Classifieur de contenu (VERSION MOCK)"""

    def __init__(self):
        self.themes = [
            "Pédagogie différenciée",
            "Évaluation des apprentissages",
            "Gestion de classe",
            "Numérique éducatif",
            "Bien-être enseignant",
            "Relations parents-école",
            "Orientation scolaire",
            "Éducation inclusive"
        ]

        self.defis_prioritaires = [
            "transition_ecologique",
            "sante_mentale",
            "ecole_inclusive",
            "competences_psychosociales",
            "reussite_tous_eleves"
        ]

        # Mots-clés bidons pour la démo (à remplacer par le vrai NLP)
        self.keywords_themes = {
            "Pédagogie différenciée": ["différenci", "adapt", "niveau", "besoin"],
            "Évaluation des apprentissages": ["évalua", "compétenc", "test", "contrôl"],
            "Gestion de classe": ["classe", "disciplin", "comport", "group"],
            "Numérique éducatif": ["numériq", "digital", "technolog", "ordinateur"],
            "Bien-être enseignant": ["stress", "burn", "bien-être", "équilibr"],
            "Relations parents-école": ["parent", "famil", "communication", "rencontr"],
            "Orientation scolaire": ["orient", "métier", "parcour", "projet"],
            "Éducation inclusive": ["inclusiv", "handicap", "adapt", "besoin"]
        }

        self.keywords_defis = {
            "transition_ecologique": ["écolog", "environn", "durabl", "climat"],
            "sante_mentale": ["mental", "stress", "bien-être", "émotio"],
            "ecole_inclusive": ["inclusiv", "handicap", "dys", "adapt"],
            "competences_psychosociales": ["social", "émotionn", "compétenc", "savoir-être"],
            "reussite_tous_eleves": ["réussit", "difficul", "décroch", "motiv"]
        }

    def _extract_features_mock(self, markdown_text: str) -> Dict:
        """Extraction de features basique pour la démo (à remplacer par NLP)"""
        if not markdown_text:
            return {"word_count": 0, "themes_detected": [], "defis_detected": []}

        text_lower = markdown_text.lower()
        word_count = len(text_lower.split())

        # Détection simple par mots-clés
        themes_detected = []
        for theme, keywords in self.keywords_themes.items():
            if any(keyword in text_lower for keyword in keywords):
                themes_detected.append(theme)

        defis_detected = []
        for defi, keywords in self.keywords_defis.items():
            if any(keyword in text_lower for keyword in keywords):
                defis_detected.append(defi)

        return {
            "word_count": word_count,
            "themes_detected": themes_detected,
            "defis_detected": defis_detected
        }

    def classify_theme(self, markdown_text: str) -> Dict[str, float]:
        """
        Classifie le thème principal du contenu

        Returns:
            Dict avec les scores par thème (somme = 1.0)
        """
        features = self._extract_features_mock(markdown_text)

        # MOCK : génération de scores aléatoires mais cohérents
        if features["themes_detected"]:
            # Si des thèmes sont détectés, on leur donne plus de poids
            scores = {}
            detected_themes = features["themes_detected"]

            for theme in self.themes:
                if theme in detected_themes:
                    scores[theme] = random.uniform(0.3, 0.8)
                else:
                    scores[theme] = random.uniform(0.01, 0.2)
        else:
            # Scores complètement aléatoires
            scores = {theme: random.uniform(0.01, 0.5) for theme in self.themes}

        # Normalisation pour que la somme = 1.0
        total = sum(scores.values())
        scores = {theme: score/total for theme, score in scores.items()}

        return scores

    def classify_defi_prioritaire(self, markdown_text: str) -> Dict[str, float]:
        """
        Classifie le défi prioritaire du contenu (1 seul max)

        Returns:
            Dict avec les scores par défi + "aucun"
        """
        features = self._extract_features_mock(markdown_text)

        # MOCK : logique similaire
        scores = {"aucun": 0.3}  # Score de base pour "aucun défi"

        if features["defis_detected"]:
            detected_defis = features["defis_detected"]

            for defi in self.defis_prioritaires:
                if defi in detected_defis:
                    scores[defi] = random.uniform(0.4, 0.9)
                    scores["aucun"] = random.uniform(0.05, 0.3)
                else:
                    scores[defi] = random.uniform(0.01, 0.1)
        else:
            # Aucun défi détecté
            for defi in self.defis_prioritaires:
                scores[defi] = random.uniform(0.01, 0.2)

        # Normalisation
        total = sum(scores.values())
        scores = {defi: score/total for defi, score in scores.items()}

        return scores

    def get_top_predictions(self, markdown_text: str) -> Dict:
        """
        Retourne les prédictions principales avec scores de confiance
        """
        theme_scores = self.classify_theme(markdown_text)
        defi_scores = self.classify_defi_prioritaire(markdown_text)

        # Thème avec le score le plus élevé
        top_theme = max(theme_scores, key=theme_scores.get)
        theme_confidence = theme_scores[top_theme]

        # Défi avec le score le plus élevé
        top_defi = max(defi_scores, key=defi_scores.get)
        defi_confidence = defi_scores[top_defi]

        return {
            "theme_principal": {
                "nom": top_theme,
                "confidence": round(theme_confidence, 3),
                "all_scores": theme_scores
            },
            "defi_prioritaire": {
                "nom": top_defi,
                "confidence": round(defi_confidence, 3),
                "all_scores": defi_scores
            },
            "features_extracted": self._extract_features_mock(markdown_text)
        }

    def batch_classify(self, contents_df: pd.DataFrame, content_column: str = "content") -> pd.DataFrame:
        """
        Classification en lot d'un DataFrame de contenus
        """
        results = []

        for idx, row in contents_df.iterrows():
            content = row[content_column] if pd.notna(row[content_column]) else ""
            prediction = self.get_top_predictions(content)

            results.append({
                "content_id": row.get("id", idx),
                "theme_principal": prediction["theme_principal"]["nom"],
                "theme_confidence": prediction["theme_principal"]["confidence"],
                "defi_prioritaire": prediction["defi_prioritaire"]["nom"],
                "defi_confidence": prediction["defi_prioritaire"]["confidence"],
                "word_count": prediction["features_extracted"]["word_count"]
            })

        return pd.DataFrame(results)


# Fonction utilitaire pour tester
def demo_classification():
    """Démonstration de la classification"""
    classifier = ContentClassifier()

    # Texte d'exemple
    sample_text = """
    # Gérer les élèves en difficulté

    Cette fiche pratique présente des stratégies pour adapter
    votre pédagogie aux élèves qui rencontrent des difficultés d'apprentissage.

    ## Différenciation pédagogique
    - Adapter les supports selon les besoins
    - Proposer différents niveaux d'exercices
    - Utiliser des outils numériques adaptés

    ## Accompagnement personnalisé
    L'objectif est de permettre la réussite de tous les élèves.
    """

    result = classifier.get_top_predictions(sample_text)

    print("=== DÉMONSTRATION CLASSIFICATION ===")
    print(f"Thème principal: {result['theme_principal']['nom']}")
    print(f"Confiance: {result['theme_principal']['confidence']}")
    print(f"Défi prioritaire: {result['defi_prioritaire']['nom']}")
    print(f"Confiance: {result['defi_prioritaire']['confidence']}")

    return result


if __name__ == "__main__":
    demo_classification()
