# Documentation Dataset Utilisateurs ÊtrePROF (english below)

## 📋 Vue d'ensemble

Ce dataset contient les profils des utilisateurs de la plateforme ÊtrePROF, une plateforme de développement professionnel pour enseignants développée par l'association Ecolhuma. Les données ont été nettoyées et structurées pour faciliter l'analyse et l'apprentissage automatique.

**Taille du dataset** : ~200 000 utilisateurs
**Nombre de colonnes** : 40
**Format** : DataFrame pandas nettoyé

## 🗂️ Description des colonnes

### **Informations de base**
| Colonne | Type | Description |
|---------|------|-------------|
| `id` | int | Identifiant unique de l'utilisateur |
| `statut_infolettre` | object | Statut d'abonnement à la newsletter |
| `statut_mailchimp` | object | Statut dans le système d'emailing |
| `created_at` | date | Date de création du compte (format YYYY-MM-DD) |

### **Localisation**
| Colonne | Type | Description |
|---------|------|-------------|
| `code_postal` | object | Code postal de l'utilisateur (5 chiffres) |
| `departement` | object | Code département déduit du code postal (2-3 chiffres) |
| `academie` | object | Académie déduite du département |

### **Profil professionnel**
| Colonne | Type | Description |
|---------|------|-------------|
| `anciennete` | int | Ancienneté dans l'enseignement (en années) |
| `degre` | int | Degré d'enseignement principal : 1=Primaire, 2=Secondaire, 3=Formateur |
| `type_etab` | object | Type d'établissement de l'utilisateur |
| `discipline` | object | Discipline principale enseignée (secondaire uniquement) |

### **Établissements d'enseignement (colonnes binaires)**
| Colonne | Type | Description |
|---------|------|-------------|
| `maternelle` | int | 1 si enseigne en maternelle (TPS-GS), 0 sinon |
| `elementaire` | int | 1 si enseigne en élémentaire (CP-CM2), 0 sinon |
| `college` | int | 1 si enseigne au collège (6e-3e), 0 sinon |
| `lycee` | int | 1 si enseigne au lycée général (2nde-Terminale), 0 sinon |
| `lycee_pro` | int | 1 si enseigne en lycée professionnel (CAP-Bac Pro), 0 sinon |
| `autre` | int | 1 si post-bac ou formateur, 0 sinon |

### **Niveaux d'enseignement détaillés (colonnes binaires)**

#### **Maternelle**
| Colonne | Description |
|---------|-------------|
| `niveau_tps` | Très Petite Section (2-3 ans) |
| `niveau_ps` | Petite Section (3-4 ans) |
| `niveau_ms` | Moyenne Section (4-5 ans) |
| `niveau_gs` | Grande Section (5-6 ans) |

#### **Élémentaire**
| Colonne | Description |
|---------|-------------|
| `niveau_cp` | Cours Préparatoire (6-7 ans) |
| `niveau_ce1` | Cours Élémentaire 1ère année (7-8 ans) |
| `niveau_ce2` | Cours Élémentaire 2ème année (8-9 ans) |
| `niveau_cm1` | Cours Moyen 1ère année (9-10 ans) |
| `niveau_cm2` | Cours Moyen 2ème année (10-11 ans) |

#### **Collège**
| Colonne | Description |
|---------|-------------|
| `niveau_6e` | Sixième (11-12 ans) |
| `niveau_5e` | Cinquième (12-13 ans) |
| `niveau_4e` | Quatrième (13-14 ans) |
| `niveau_3e` | Troisième (14-15 ans) |

#### **Lycée général**
| Colonne | Description |
|---------|-------------|
| `niveau_2nde` | Seconde (15-16 ans) |
| `niveau_1ere` | Première (16-17 ans) |
| `niveau_terminale` | Terminale (17-18 ans) |

#### **Lycée professionnel**
| Colonne | Description |
|---------|-------------|
| `niveau_cap` | Certificat d'Aptitude Professionnelle |
| `niveau_bac_pro` | Baccalauréat Professionnel |

#### **Enseignement supérieur et spécialisé**
| Colonne | Description |
|---------|-------------|
| `niveau_post_bac` | Enseignement supérieur |
| `niveau_segpa` | Section d'Enseignement Général et Professionnel Adapté |
| `niveau_ash` | Adaptation Scolaire et Handicap |
| `niveau_direction` | Direction d'établissement |
| `niveau_formateur` | Formation/Inspection |
| `niveau_documentaliste` | Documentation (CDI) |

## 🔧 Traitement des données

### **Nettoyage effectué**
- ✅ Standardisation des codes postaux (ajout des zéros initiaux)
- ✅ Mapping département → académie automatique
- ✅ Actualisation de l'ancienneté basée sur la date de création du compte
- ✅ Extraction et structuration des niveaux d'enseignement depuis les données JSON
- ✅ Filtrage pour ne garder que les utilisateurs français
- ✅ One-hot encoding des niveaux et établissements

### **Logique métier**
- **Multi-niveaux** : Un utilisateur peut enseigner à plusieurs niveaux (colonnes binaires)
- **Primaire/Secondaire** : Classification basée sur la majorité des niveaux enseignés
- **Discipline** : Seulement pour le secondaire (NaN pour primaire/maternelle)
- **Académie** : Déduite automatiquement du département si manquante

## 📊 Utilisation pour le Machine Learning

Ce dataset est optimisé pour l'apprentissage automatique avec :
- **Features numériques** : Ancienneté, degré, colonnes binaires
- **Features catégorielles** : Académie, département, discipline, type_etab
- **Encodage one-hot** : Niveaux et établissements
- **Pas de valeurs manquantes critiques** : NaN gérés logiquement

---

# ÊtrePROF Users Dataset Documentation

## 📋 Overview

This dataset contains user profiles from the ÊtrePROF platform, a professional development platform for teachers developed by the French non-profit Ecolhuma. The data has been cleaned and structured to facilitate analysis and machine learning.

**Dataset size**: ~200,000 users
**Number of columns**: 40
**Format**: Cleaned pandas DataFrame

## 🗂️ Column descriptions

### **Basic information**
| Column | Type | Description |
|---------|------|-------------|
| `id` | int | Unique user identifier |
| `statut_infolettre` | object | Newsletter subscription status |
| `statut_mailchimp` | object | Email system status |
| `created_at` | date | Account creation date (YYYY-MM-DD format) |

### **Location**
| Column | Type | Description |
|---------|------|-------------|
| `code_postal` | object | User's postal code (5 digits) |
| `departement` | object | Department code derived from postal code (2-3 digits) |
| `academie` | object | Educational academy derived from department |

### **Professional profile**
| Column | Type | Description |
|---------|------|-------------|
| `anciennete` | int | Teaching experience (in years) |
| `degre` | int | Main teaching level: 1=Primary, 2=Secondary, 3=Trainer |
| `type_etab` | object | User's institution type |
| `discipline` | object | Main subject taught (secondary only) |

### **Teaching institutions (binary columns)**
| Column | Type | Description |
|---------|------|-------------|
| `maternelle` | int | 1 if teaches in kindergarten (TPS-GS), 0 otherwise |
| `elementaire` | int | 1 if teaches in elementary (CP-CM2), 0 otherwise |
| `college` | int | 1 if teaches in middle school (6e-3e), 0 otherwise |
| `lycee` | int | 1 if teaches in high school (2nde-Terminale), 0 otherwise |
| `lycee_pro` | int | 1 if teaches in vocational school (CAP-Bac Pro), 0 otherwise |
| `autre` | int | 1 if post-secondary or trainer, 0 otherwise |

### **Detailed teaching levels (binary columns)**

#### **Kindergarten (Maternelle)**
| Column | Description |
|---------|-------------|
| `niveau_tps` | Very Small Section (2-3 years) |
| `niveau_ps` | Small Section (3-4 years) |
| `niveau_ms` | Middle Section (4-5 years) |
| `niveau_gs` | Large Section (5-6 years) |

#### **Elementary (Élémentaire)**
| Column | Description |
|---------|-------------|
| `niveau_cp` | Preparatory Course (6-7 years) |
| `niveau_ce1` | Elementary Course 1st year (7-8 years) |
| `niveau_ce2` | Elementary Course 2nd year (8-9 years) |
| `niveau_cm1` | Middle Course 1st year (9-10 years) |
| `niveau_cm2` | Middle Course 2nd year (10-11 years) |

#### **Middle School (Collège)**
| Column | Description |
|---------|-------------|
| `niveau_6e` | 6th grade (11-12 years) |
| `niveau_5e` | 7th grade (12-13 years) |
| `niveau_4e` | 8th grade (13-14 years) |
| `niveau_3e` | 9th grade (14-15 years) |

#### **High School (Lycée)**
| Column | Description |
|---------|-------------|
| `niveau_2nde` | 10th grade (15-16 years) |
| `niveau_1ere` | 11th grade (16-17 years) |
| `niveau_terminale` | 12th grade (17-18 years) |

#### **Vocational School**
| Column | Description |
|---------|-------------|
| `niveau_cap` | Professional Aptitude Certificate |
| `niveau_bac_pro` | Professional Baccalaureate |

#### **Higher and specialized education**
| Column | Description |
|---------|-------------|
| `niveau_post_bac` | Higher education |
| `niveau_segpa` | Adapted General and Professional Education Section |
| `niveau_ash` | School Adaptation and Disability |
| `niveau_direction` | School administration |
| `niveau_formateur` | Training/Inspection |
| `niveau_documentaliste` | Library/Documentation |

## 🔧 Data processing

### **Cleaning performed**
- ✅ Postal code standardization (added leading zeros)
- ✅ Automatic department → academy mapping
- ✅ Teaching experience updated based on account creation date
- ✅ Teaching levels extracted and structured from JSON data
- ✅ Filtered to keep only French users
- ✅ One-hot encoding of levels and institutions

### **Business logic**
- **Multi-level** : Users can teach at multiple levels (binary columns)
- **Primary/Secondary** : Classification based on majority of taught levels
- **Discipline** : Only for secondary (NaN for primary/kindergarten)
- **Academy** : Automatically derived from department if missing

## 📊 Machine Learning usage

This dataset is optimized for machine learning with:
- **Numerical features** : Experience, degree, binary columns
- **Categorical features** : Academy, department, discipline, institution type
- **One-hot encoding** : Levels and institutions
- **No critical missing values** : NaN handled logically
