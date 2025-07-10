# Fighting School Inequalities, One Algorithm at a Time!

## 📔CONTEXT

### ÊtrePROF, your daily companion to manage your class

### ÊtrePROF : a digital platform provided by Ecolhuma, a french non-profit structure

- Discover [**Ecolhuma](https://ecolhuma.fr/)** - 12 years old
- Discover [**ÊtrePROF](https://etreprof.fr/)** - 7 years old

### What is the purpose of ÊtrePROF ?

- Since its launch, ÊtrePROF has relied on a growing community of teachers to deploy content and tools that meet their needs.
- ÊtrePROF is a digital professional development platform that supports teachers in their profession.
- Our mission is to support teachers and school leaders so that they can give all students the best opportunities.

### Understand french school system

| Level | Establishment | Class/Grade | Age |
| --- | --- | --- | --- |
| **PRIMARY** | **Nursery School - Maternelle** | Petite Section (PS) | 3 years |
|  |  | Moyenne Section (MS) | 4 years |
|  |  | Grande Section (GS) | 5 years |
|  | **Elementary School - Élémentaire** | CP | 6 years |
|  |  | CE1 | 7 years |
|  |  | CE2 | 8 years |
|  |  | CM1 | 9 years |
|  |  | CM2 | 10 years |
| **SECONDARY** | **Middle School - Collège** | 6e | 11 years |
|  |  | 5e | 12 years |
|  |  | 4e | 13 years |
|  |  | 3e | 14 years |
|  | **High School - Lycée** | 2de | 15 years |
|  |  | 1ère | 16 years |
|  |  | Terminale | 17 years |
|  | **Vocational High School - Lycée profession** | 2de Pro | 15 years |
|  |  | 1ère Pro | 16 years |
|  |  | Terminale Pro | 17 years |

**Notes:**

- Nursery School: Not mandatory (but very very common)
- Mandatory schooling: Ages 3 to 16 (CP to 1ère)
- Vocational High School: Vocational training leading to a professional baccalaureate

### Priority challenges at ÊtrePROF

There are 5 priority challenges identified at ÊtrePROF which are the levers for a fairer and more equal school:

- The success of all students
- Mental health
- Inclusive school
- Psychosocial skills
- Ecological transition

In parallel, other contents are created

---

## 📊 DATAS

### Datas

- A database with all of the content created by teachers (called *Mentors* internally) - **around 2 000 contents**
- A database with user information: structural details (academy, newsletter subscription, etc.) and data on consulted content - **around 190 000 users**
- A database of interactions with the interaction date and type (account creation, article reading, tool sheet download, etc.) - **around 12 000 000 interactions**

### What contents ?

- **articles** : something to read online ;-)  - [example](https://etreprof.fr/ressources/4840/6-facons-dutiliser-l-ia-dans-mon-quotidien-de-prof)
- **fiche_outils** : A one- or two-page document containing tips and tricks for implementing teaching practices in the classroom - [example](https://etreprof.fr/fiches-outils/167/etablir-des-rituels-qui-cadrent)
- **guide_pratique** : between 10 and 20 sheets. Like a short book of fiche_outils - [example](https://etreprof.fr/fiches-outils/167/etablir-des-rituels-qui-cadrent)
- **fiche_activité** : some ready-to-use lesson preparation *(pretty new)* - [example](https://etreprof.fr/activite-maternelle/1041/le-printemps-du-papier)
- **ateliers** : like a webinar/online workshop - [example](https://etreprof.fr/ateliers/918/construire-sa-strategie-de-gestion-du-bruit-elementairesecondaire)
- **kits** : 5 mails with content, sent in a week after subscription - [example](https://etreprof.fr/boite-a-outils/ecole-dehors-milieu-urbain-elementaire)
- **parcours** : like a short mooc (old but still active) - [example](https://etreprof.fr/parcours/affuter-ma-pedagogie-pour-mes-eleves-a-besoins-educatifs-particuliers)

### Focus on `interaction_events` table

- attended : attended a workshop
- click : clicked
- click_mail : clicked in a mail
- opened_mail : opened a mail
- comment_posted : post a comment
- completed : validation of a step in a parcours
- connexion : easy to understand
- download : download something
- ~~inscription : deprecated~~
- register : subscribed to etreprof
- session : a session on the website
- ~~submitted : deprecated~~
- subscribed : for different things (atelier, parcours, kit, …)
- ~~subscription-completed : deprecated~~
- ~~subscription-ended : deprecated~~
- page_view : article viewed
- contenu_vote : like or dislike on a content
- contenu_favoris : content added to favs - not really used by users

---

## 🎯 **TARGET**

### SubGoal 1: Categorize content

- Identify the main themes of each content
- Identify those who are in a Priority Challenge (and which one)

### SubGoal 2: User Segmentation

- Dynamic clustering based on behaviors
- Tracking transitions between segments
- Detailed profiling of each group
- Weekly recalculation of assignments

### SubGoal 3: Personalize content suggestions

- Hybrid system (collaborative + content-based)
- Balance 70% engagement on interest / 30% development (on Priority Challenges)
- Matching users ↔ creators
- Continuous optimization of recommendations

### SubGoal 4: Churn Prevention

- Predict and prevent dropout
- Early detection of risk signals
- Probabilistic churn scoring
- Targeted intervention recommendations
- Analysis of critical moments
