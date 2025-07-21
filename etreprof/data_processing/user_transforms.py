import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from collections import Counter
import os
from dotenv import load_dotenv


def drop_col(df, string):
    """
    Drops a column from the DataFrame df if it exists.
    """
    if string in df.columns:
        df.drop(string, axis=1, inplace=True)
        return


def clean_json_niveaux(df):
    """
    Cleans the 'niveaux' column in the DataFrame df.
    Converts JSON strings to lists and handles missing values.
    """

niveaux_rares = [
    "Études supérieures", "Enseignement spécialisé", "Maternelle",
    "Elémentaire", "Collège", "Lycée", "Étudiant stagiaire",
    "6ème primaire", "", "Autres"
]

def clean_json_niveau(niveaux_str):
    if pd.isna(niveaux_str):
        return niveaux_str

    try:
        niveaux_list = json.loads(niveaux_str)

        # Séparer les éléments rares des éléments valides
        elements_rares = [niveau for niveau in niveaux_list if niveau in niveaux_rares]
        elements_valides = [niveau for niveau in niveaux_list if niveau not in niveaux_rares]

        # Si il y a des éléments valides, on garde que ceux-là
        if elements_valides:
            return json.dumps(elements_valides, ensure_ascii=False)
        # Sinon, on garde les éléments rares (cas où il n'y a que ça)
        else:
            return json.dumps(elements_rares, ensure_ascii=False)

    except:
        return niveaux_str

def replace_categories(niveaux_str):
    if pd.isna(niveaux_str):
        return niveaux_str

    try:
        niveaux_list = json.loads(niveaux_str)

        # Remplacer les catégories
        niveaux_replaced = []
        for niveau in niveaux_list:
            if niveau == "Enseignement spécialisé":
                niveaux_replaced.append("ASH")
            elif niveau == "Études supérieures":
                niveaux_replaced.append("POST BAC")
            else:
                niveaux_replaced.append(niveau)

        return json.dumps(niveaux_replaced, ensure_ascii=False)

    except:
        return niveaux_str


all_niveaux = ['1ère',
 '2nde',
 '3e',
 '4e',
 '5e',
 '6e',
 'ASH',
 'Bac Pro',
 'CAP',
 'CE1',
 'CE2',
 'CM1',
 'CM2',
 'CP',
 'Direction',
 'Formateur-trice /Inspecteur-trice',
 'GS',
 'MS',
 'POST BAC',
 'PS',
 'Professeur-e documentaliste',
 'SEGPA',
 'TPS',
 'Terminale']

def extract_etablissement_info(etab_str):
    """
    Extracts information from the 'etablissement' JSON string.
    """
    if pd.isna(etab_str)or etab_str == '[]':
        return np.nan, np.nan, np.nan

    try:
        etab_list = json.loads(etab_str)

        # Vérifier qu'on a bien une liste non vide
        if isinstance(etab_list, list) and len(etab_list) > 0:
            etab_obj = etab_list[0]  # Prendre le premier (et probablement unique) établissement

            # Extraire les infos avec valeur par défaut 'NR'
            code_postal = etab_obj.get('code_postal', 'NR')
            academie = etab_obj.get('academie', 'NR')
            type_etablissement = etab_obj.get('type_etablissement', 'NR')

            return code_postal, academie, type_etablissement
        else:
            return 'NR', 'NR', 'NR'

    except:
        return 'NR', 'NR', 'NR'

def complete_codepostal(row):
    codepostal = row['codepostal']
    code_postal_etab = row['code_postal_etab']

    # Cas 1: codepostal NaN et code_postal_etab NaN → NaN
    if pd.isna(codepostal) and pd.isna(code_postal_etab):
        return np.nan

    # Cas 2: codepostal NaN et code_postal_etab a une valeur → code_postal_etab
    elif pd.isna(codepostal) and pd.notna(code_postal_etab):
        return code_postal_etab

    # Cas 3: codepostal a une valeur et code_postal_etab NaN → ne rien faire (garder codepostal)
    elif pd.notna(codepostal) and pd.isna(code_postal_etab):
        return codepostal

    # Cas 4: codepostal a une valeur et code_postal_etab a une valeur → code_postal_etab (priorité)
    elif pd.notna(codepostal) and pd.notna(code_postal_etab):
        return code_postal_etab

def extract_departement(code_postal):
    if pd.isna(code_postal):
        return np.nan

    # Convertir en string et s'assurer qu'on a 5 chiffres (zfill pour ajouter les 0)
    cp = str(code_postal).strip().zfill(5)

    # Vérifier que c'est numérique après padding
    if not cp.isdigit():
        return np.nan

    # Cas spéciaux des DOM-TOM (3 chiffres)
    if cp.startswith('97') or cp.startswith('98'):
        return cp[:3]  # 971, 972, 973, 974, 975, 976, 977, 978, 984, 986, 987, 988

    # Cas général (2 chiffres) - garder le zéro initial
    return cp[:2]


dept_to_academie = {
    # Clermont-Ferrand
    '03': 'Clermont-Ferrand', '15': 'Clermont-Ferrand', '43': 'Clermont-Ferrand', '63': 'Clermont-Ferrand',

    # Grenoble
    '07': 'Grenoble', '26': 'Grenoble', '38': 'Grenoble', '73': 'Grenoble', '74': 'Grenoble',

    # Lyon
    '01': 'Lyon', '42': 'Lyon', '69': 'Lyon', '69D': 'Lyon', '69M': 'Lyon',

    # Besançon
    '25': 'Besançon', '39': 'Besançon', '70': 'Besançon', '90': 'Besançon',

    # Dijon
    '21': 'Dijon', '58': 'Dijon', '71': 'Dijon', '89': 'Dijon',

    # Rennes
    '22': 'Rennes', '29': 'Rennes', '35': 'Rennes', '56': 'Rennes',

    # Orléans-Tours
    '18': 'Orléans-Tours', '28': 'Orléans-Tours', '36': 'Orléans-Tours', '37': 'Orléans-Tours', '41': 'Orléans-Tours', '45': 'Orléans-Tours',

    # Corse
    '2A': 'Corse', '2B': 'Corse',

    # Nancy-Metz
    '54': 'Nancy-Metz', '55': 'Nancy-Metz', '57': 'Nancy-Metz', '88': 'Nancy-Metz',

    # Reims
    '08': 'Reims', '10': 'Reims', '51': 'Reims', '52': 'Reims',

    # Strasbourg
    '67': 'Strasbourg', '68': 'Strasbourg',

    # Guadeloupe
    '971': 'Guadeloupe', '977': 'Guadeloupe', '978': 'Guadeloupe',

    # Guyane
    '973': 'Guyane',

    # Amiens
    '02': 'Amiens', '60': 'Amiens', '80': 'Amiens',

    # Lille
    '59': 'Lille', '62': 'Lille',

    # Créteil
    '77': 'Créteil', '93': 'Créteil', '94': 'Créteil',

    # Paris
    '75': 'Paris',

    # Versailles
    '78': 'Versailles', '91': 'Versailles', '92': 'Versailles', '95': 'Versailles',

    # Martinique
    '972': 'Martinique',

    # Normandie
    '14': 'Normandie', '27': 'Normandie', '50': 'Normandie', '61': 'Normandie', '76': 'Normandie', '975': 'Normandie',

    # Bordeaux
    '24': 'Bordeaux', '33': 'Bordeaux', '40': 'Bordeaux', '47': 'Bordeaux', '64': 'Bordeaux',

    # Limoges
    '19': 'Limoges', '23': 'Limoges', '87': 'Limoges',

    # Poitiers
    '16': 'Poitiers', '17': 'Poitiers', '79': 'Poitiers', '86': 'Poitiers',

    # Montpellier
    '11': 'Montpellier', '30': 'Montpellier', '34': 'Montpellier', '48': 'Montpellier', '66': 'Montpellier',

    # Toulouse
    '09': 'Toulouse', '12': 'Toulouse', '31': 'Toulouse', '32': 'Toulouse', '46': 'Toulouse', '65': 'Toulouse', '81': 'Toulouse', '82': 'Toulouse',

    # Nantes
    '44': 'Nantes', '49': 'Nantes', '53': 'Nantes', '72': 'Nantes', '85': 'Nantes',

    # Aix-Marseille
    '04': 'Aix-Marseille', '05': 'Aix-Marseille', '13': 'Aix-Marseille', '84': 'Aix-Marseille',

    # Nice
    '06': 'Nice', '83': 'Nice',

    # La Réunion
    '974': 'La Réunion',

    # Mayotte
    '976': 'Mayotte'
}

def complete_academie(row):
    academie_etab = row['academie_etab']
    departement = row['departement']

    if pd.notna(academie_etab):
        return academie_etab

    if pd.notna(departement) and departement in dept_to_academie:
        return dept_to_academie[departement]

    return np.nan

def extract_discipline(row):
    maternelle = row['maternelle']
    elementaire = row['elementaire']
    json_discipline = row['json_discipline']

    # Si maternelle ou élémentaire = 1, on met NaN
    if maternelle == 1 or elementaire == 1:
        return np.nan

    # Sinon, on extrait la première discipline du JSON
    if pd.notna(json_discipline):
        try:
            discipline_list = json.loads(json_discipline)

            # Vérifier qu'on a bien une liste non vide
            if isinstance(discipline_list, list) and len(discipline_list) > 0:
                return discipline_list[0]  # Premier élément au format string
            else:
                return np.nan
        except:
            return np.nan

    return np.nan


def update_anciennete(row):
    anciennete = row['anciennete']
    created_at = row['created_at']

    if pd.isna(created_at):
        return anciennete

    try:
        if isinstance(created_at, str):
            created_date = pd.to_datetime(created_at)
        else:
            created_date = created_at

        annee_creation = created_date.year
        ecart_annees = 2025 - annee_creation

        if pd.isna(anciennete):
            return ecart_annees

        return anciennete + ecart_annees

    except:
        return anciennete

def main_users_cleaning(csv):
    """
    Cleans the user data from the given csv file.
    """

    # Drop unnecessary columns and filter data
    df = pd.read_csv(csv, low_memory=False)
    df = df[df.locale != "be"]
    df['pays'] = df['pays'].fillna('france')
    df = df[df.pays == 'france']

    col_to_drop = ['locale', 'public', 'name', 'prenom', 'pays', 'statut',
                   'fonction', 'fontion_longue', 'enseigne_en_eefe',
                   'date_derniere_action', 'updated_at', 'json_format',
                   'json_centre_interet', 'json_metadata']

    for col in col_to_drop:
        drop_col(df, col)

    # Clean and process the 'json_niveau' column
    df['json_niveau'] = df['json_niveau'].fillna('[]')
    df['json_niveau'] = df['json_niveau'].apply(clean_json_niveau)
    df['json_niveau'] = df['json_niveau'].apply(replace_categories)
    df = df.dropna(subset=['json_niveau'])
    df = df.reset_index(drop=True)

    # One-hot encoding for 'json_niveau'
    for niveau in sorted(all_niveaux):
        col_name = f"niveau_{niveau}".replace(" ", "_").replace("-", "_").replace("è", "e").replace("é", "e").lower()
        df[col_name] = 0
    for idx, niveaux_str in df['json_niveau'].items():
        niveaux_list = json.loads(niveaux_str)
        for niveau in niveaux_list:
            col_name = f"niveau_{niveau}".replace(" ", "_").replace("-", "_").replace("è", "e").replace("é", "e").lower()
            if col_name in df.columns:
                df.loc[idx, col_name] = 1

    # Encode 'degre' column
    niveaux_primaires = ['TPS', 'PS', 'MS', 'GS', 'CP', 'CE1', 'CE2', 'CM1', 'CM2', 'Direction', 'ASH']
    niveaux_secondaires = ['6e', '5e', '4e', '3e', '2nde', '1ère', 'Terminale', 'Bac Pro', 'CAP', 'SEGPA', 'Professeur-e documentaliste', 'POST BAC']
    niveaux_formateurs = ['Formateur-trice /Inspecteur-trice']

    # Créer la colonne degre (0 par défaut)
    df['degre'] = 0

    for idx, niveaux_str in df['json_niveau'].items():
        if isinstance(niveaux_str, str):
            niveaux_list = json.loads(niveaux_str)

            count_primaire = sum(1 for niveau in niveaux_list if niveau in niveaux_primaires)
            count_secondaire = sum(1 for niveau in niveaux_list if niveau in niveaux_secondaires)
            count_formateur = sum(1 for niveau in niveaux_list if niveau in niveaux_formateurs)

            if count_formateur > 0:
                df.loc[idx, 'degre'] = 3  # Formateur
            elif count_primaire > count_secondaire:
                df.loc[idx, 'degre'] = 1  # Primaire
            elif count_secondaire > count_primaire:
                df.loc[idx, 'degre'] = 2  # Secondaire
            elif count_primaire == count_secondaire and count_primaire > 0:
                df.loc[idx, 'degre'] = 1  # En cas d'égalité, primaire par défaut

    # Encode 'grandsNiveaux' column
    niveaux_maternelle = ['TPS', 'PS', 'MS', 'GS', 'Direction','ASH']
    niveaux_elementaire = ['CP', 'CE1', 'CE2', 'CM1', 'CM2', 'ASH', 'Direction']
    niveaux_college = ['6e', '5e', '4e', '3e', 'SEGPA', 'Professeur-e documentaliste']
    niveaux_lycee = ['2nde', '1ère', 'Terminale', 'Professeur-e documentaliste']
    niveaux_lycee_pro = ['Bac Pro', 'CAP']
    niveaux_autre = ['POST BAC', 'Formateur-trice /Inspecteur-trice']

    etablissements = ['maternelle', 'elementaire', 'college', 'lycee', 'lycee_pro', 'autre']

    for etab in etablissements:
        df[etab] = 0

    for idx, niveaux_str in df['json_niveau'].items():
        if isinstance(niveaux_str, str):
            niveaux_list = json.loads(niveaux_str)

            if any(niveau in niveaux_maternelle for niveau in niveaux_list):
                df.loc[idx, 'maternelle'] = 1
            if any(niveau in niveaux_elementaire for niveau in niveaux_list):
                df.loc[idx, 'elementaire'] = 1
            if any(niveau in niveaux_college for niveau in niveaux_list):
                df.loc[idx, 'college'] = 1
            if any(niveau in niveaux_lycee for niveau in niveaux_list):
                df.loc[idx, 'lycee'] = 1
            if any(niveau in niveaux_lycee_pro for niveau in niveaux_list):
                df.loc[idx, 'lycee_pro'] = 1
            if any(niveau in niveaux_autre for niveau in niveaux_list):
                df.loc[idx, 'autre'] = 1

    # Drop the original 'json_niveau' column
    drop_col(df, 'json_niveau')

    # Clean and process the 'etablissement' column
    df[['code_postal_etab', 'academie_etab', 'type_etablissement_etab']] = df['json_etablissement'].apply(
        lambda x: pd.Series(extract_etablissement_info(x))
    )

    df['codepostal'] = df.apply(complete_codepostal, axis=1)

    drop_col(df, "aucun_etablissement")
    drop_col(df, "json_etablissement")

    # Create departement column
    df['departement'] = df['codepostal'].apply(extract_departement)

    # Complete academie column
    df['academie_etab'] = df.apply(complete_academie, axis=1)

    # Complete 'discipline' column
    df['discipline'] = df.apply(extract_discipline, axis=1)
    drop_col(df, 'json_discipline')

    # Clean 'anciennete' column
    df['anciennete'] = df.apply(update_anciennete, axis=1)

    # Clean 'created_at' column (only keep date part)
    df['created_at'] = pd.to_datetime(df['created_at']).dt.date

    df = df.rename(columns={
        'codepostal': 'code_postal',
        'type_etablissement_etab': 'type_etab',
        'academie_etab': 'academie',
        'niveau_formateur_trice_/inspecteur_trice': 'niveau_formateur',
        'niveau_professeur_e_documentaliste': 'niveau_documentaliste'
    })

    columns_order = [
    'id', 'statut_infolettre', 'statut_mailchimp', 'code_postal', 'departement', 'academie',
    'anciennete', 'created_at', 'degre', 'maternelle', 'elementaire', 'college', 'lycee', 'lycee_pro', 'autre',
    'type_etab', 'discipline',
    'niveau_tps',
    'niveau_ps',
    'niveau_ms',
    'niveau_gs',
    'niveau_cp',
    'niveau_ce1',
    'niveau_ce2',
    'niveau_cm1',
    'niveau_cm2',
    'niveau_6e',
    'niveau_5e',
    'niveau_4e',
    'niveau_3e',
    'niveau_2nde',
    'niveau_1ere',
    'niveau_terminale',
    'niveau_cap',
    'niveau_bac_pro',
    'niveau_post_bac',
    'niveau_segpa',
    'niveau_ash',
    'niveau_direction',
    'niveau_formateur',
    'niveau_documentaliste',
    ]

    df = df[columns_order]

    return df
