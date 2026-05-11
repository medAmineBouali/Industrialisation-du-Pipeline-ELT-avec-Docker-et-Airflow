# 🚀 YouTube Data Pipeline : Orchestration Airflow & Dockerisation

Ce projet simule une architecture réelle de **Data Engineering**.  
L'objectif est de dépasser le stade du simple script local pour construire un pipeline **industrialisé, scalable et reproductible**.

Le pipeline automatise :

- l’extraction de données depuis l’API YouTube,
- leur stockage dans un Data Warehouse PostgreSQL,
- leur transformation analytique via Apache Airflow.

---

# 🏗️ Architecture du Système

Le projet repose sur un environnement **multi-conteneurs** géré par Docker Compose :

- **Apache Airflow (CeleryExecutor)** : orchestration des tâches
- **PostgreSQL** : Data Warehouse structuré en deux couches (*Staging* & *Core*)
- **Redis** : broker de messages pour la gestion distribuée des tâches

---

# 🎯 Objectifs Pédagogiques

## Conteneurisation
Industrialiser le pipeline avec Docker afin de garantir la portabilité et la reproductibilité de l’environnement.

## Orchestration
Concevoir un DAG (*Directed Acyclic Graph*) permettant de gérer les dépendances :

```text
Extraction >> Staging >> Transformation >> Core
```

## Data Warehousing
Implémenter une stratégie **ELT (Extract, Load, Transform)** avec gestion de l’**Upsert** afin d’éviter les doublons.

## Sécurité
Gérer rigoureusement les secrets et clés d’API via des variables d’environnement (`.env`).

---

# 🛠️ Stack Technique

| Domaine | Technologie |
|---|---|
| Langage | Python (`pandas`, `psycopg2`, `requests`) |
| Orchestration | Apache Airflow |
| Conteneurisation | Docker & Docker Compose |
| Base de données | PostgreSQL |
| Messaging | Redis |

---

# 🪜 Structure du Pipeline (DAG)

## 1. Extraction
Récupération des métriques YouTube :

- vues
- likes
- commentaires

via l’API **YouTube Data v3**.

## 2. Staging
Ingestion des données brutes dans une table de transition.

## 3. Transformation
Nettoyage et enrichissement des données :

- conversion du format ISO 8601 vers `timedelta`
- création de variables métiers
- catégorisation des vidéos

## 4. Core Load
Chargement des données enrichies et prêtes pour l’analyse BI.

---

# 📂 Structure du Projet

```plaintext
├── dags/               # Définition des workflows Airflow
├── include/            # Scripts Python et logique métier
├── data/               # Stockage local et persistance (volumes)
├── config/             # Fichiers de configuration
├── Dockerfile          # Image personnalisée pour Airflow
├── docker-compose.yaml # Orchestration des services
│                         (Airflow, Postgres, Redis)
└── .env                # Variables d’environnement
                          (API Key, DB Credentials)
```

---

# 🚀 Installation et Lancement

## 1. Cloner le dépôt

```bash
git clone <repo-url>
cd <repo-folder>
```

---

## 2. Configurer les credentials

Créer un fichier `.env` basé sur le modèle fourni puis ajouter :

- votre clé API YouTube
- les credentials PostgreSQL

---

## 3. Lancer l’architecture

```bash
docker-compose up --build
```

---

## 4. Accéder à l’interface

L’interface **Airflow UI** est disponible sur :

```text
http://localhost:8080
```

---

# 📊 Résultat

Le pipeline permet de construire une base de données analytique exploitable pour :

- dashboards Power BI
- analyses de performance YouTube
- reporting automatisé
- suivi des KPIs vidéo

---

# 🔒 Gestion des Variables d’Environnement

Exemple de fichier `.env` :

```env
YOUTUBE_API_KEY=your_api_key
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=youtube_dw
```

---

# 📌 Améliorations Futures

- Intégration d’un Data Lake
- Déploiement Kubernetes
- Monitoring avec Prometheus & Grafana
- CI/CD avec GitHub Actions
- Partitionnement PostgreSQL
- Intégration dbt pour les transformations

---

# 👨‍💻 Auteur

Projet réalisé dans le cadre d’un apprentissage avancé en :

- Data Engineering
- Orchestration de pipelines
- Data Warehousing
- Dockerisation d’applications analytiques