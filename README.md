# YouTube Data Pipeline — Airflow & Docker

A production-style Data Engineering pipeline that extracts YouTube channel metrics via the YouTube Data API v3, loads them into a PostgreSQL Data Warehouse, transforms them using SQL, and validates data quality with Soda Core — all orchestrated automatically by Apache Airflow in a fully Dockerised environment.

---

## Architecture

Multi-container environment managed by Docker Compose:

- **Apache Airflow (CeleryExecutor)** — DAG orchestration with webserver, scheduler, and worker
- **PostgreSQL** — Data Warehouse with two layers: Staging and Core
- **Redis** — message broker for distributed task execution between scheduler and workers

---

## DAG Pipeline

```
extract >> load_staging >> transform_to_core >> data_quality_checks
```

| Task | What it does |
|---|---|
| `extract` | Calls YouTube Data API v3, fetches all video metadata, passes data via XCom |
| `load_staging` | Upserts raw data into `staging_youtube_videos` |
| `transform_to_core` | Runs SQL transformations: ISO 8601 parsing, duration conversion, video type classification, topic explosion |
| `data_quality_checks` | Runs Soda Core checks: null checks, negative counts, valid video_type values, referential integrity |

---

## Data Warehouse Schema

### Staging layer — raw data as received from the API

**`staging_youtube_videos`**
- `video_id`, `title`, `published_at` (raw string), `duration` (raw ISO 8601)
- `view_count`, `like_count`, `comment_count`
- `thumbnail_url`, `topic_categories` (Postgres array), `loaded_at`

### Core layer — transformed, analytics-ready data

**`core_youtube_videos`**
- `video_id`, `title`, `published_at` (TIMESTAMP), `publish_date`, `publish_hour`
- `duration_seconds` (INTEGER), `duration_display` (HH:MM:SS string)
- `view_count`, `like_count`, `comment_count`
- `video_type` (`shorts` or `normal`), `thumbnail_url`, `updated_at`

**`core_video_topics`** — bridge table
- `video_id`, `topic` (cleaned Wikipedia category name)

---

## Tech Stack

| Domain | Technology |
|---|---|
| Language | Python 3.10 |
| Orchestration | Apache Airflow 2.9.2 (CeleryExecutor) |
| Containerisation | Docker & Docker Compose |
| Database | PostgreSQL 13 |
| Messaging | Redis 7.2 |
| Data Quality | Soda Core (soda-core-postgres) |
| HTTP | requests |
| DB Driver | psycopg2 |

---

## Project Structure

```
├── dags/
│   └── youtube_pipeline.py       # DAG definition — task wiring only
├── include/
│   ├── youtube_api.py            # All business logic: extract, load, transform, checks
│   ├── soda/
│   │   ├── configuration.yml     # Soda data source connection
│   │   └── checks.yml            # Data quality check definitions
│   └── sql/
│       ├── create_staging_table.sql
│       ├── create_core_table.sql
│       └── transform_to_core.sql
├── docker/
│   └── postgres/
│       └── init-multiple-databases.sh   # Creates 3 Postgres DBs on first start
├── tests/                        # Integration tests
├── logs/                         # Airflow task logs
├── data/                         # Local data persistence
├── config/                       # Airflow config
├── Dockerfile                    # Custom Airflow image
├── docker-compose.yml            # Full stack definition
└── .env                          # Secrets and credentials (not committed)
```

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd <repo-folder>
```

### 2. Create your `.env` file

```env
# Airflow
AIRFLOW_UID=50000
AIRFLOW_WWW_USER_USERNAME=admin
AIRFLOW_WWW_USER_PASSWORD=admin
FERNET_KEY=<generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">

# Postgres superuser
POSTGRES_CONN_USERNAME=postgres
POSTGRES_CONN_PASSWORD=postgres
POSTGRES_CONN_HOST=postgres
POSTGRES_CONN_PORT=5432

# Airflow metadata DB
METADATA_DATABASE_NAME=airflow_metadata
METADATA_DATABASE_USERNAME=airflow_meta_user
METADATA_DATABASE_PASSWORD=airflow_meta_pass

# Celery backend DB
CELERY_BACKEND_NAME=airflow_celery
CELERY_BACKEND_USERNAME=celery_user
CELERY_BACKEND_PASSWORD=celery_pass

# ELT Data Warehouse
ELT_DATABASE_NAME=youtube_dw
ELT_DATABASE_USERNAME=elt_user
ELT_DATABASE_PASSWORD=elt_pass

# YouTube API
API_KEY=<your_youtube_data_v3_api_key>
CHANNEL_HANDLE=@YourChannelHandle
```

### 3. Build and start the stack

```bash
docker-compose up --build
```

On first start, `init-multiple-databases.sh` automatically creates the three required Postgres databases: `airflow_metadata`, `airflow_celery`, and `youtube_dw`.

### 4. Create the Data Warehouse tables

Connect to the `youtube_dw` database (localhost:5432) and run:

```bash
include/sql/create_staging_table.sql
include/sql/create_core_table.sql
```

### 5. Access the Airflow UI

```
http://localhost:8080
```

Log in with the credentials you set in `.env`, then trigger the `youtube_pipeline` DAG manually or let it run on its daily schedule.

---

## How the ELT Pattern Works

Unlike a traditional ETL where transformation happens before loading, this pipeline loads raw data first then transforms it inside the database:

1. Raw YouTube API responses land in `staging_youtube_videos` exactly as received
2. A SQL query reads from staging, applies all transformations, and upserts into the core tables
3. No data is ever lost — staging always holds the raw original

This means if a transformation logic changes, you can re-run `transform_to_core.sql` against existing staging data without hitting the API again.

---

## Data Quality Checks (Soda Core)

After every pipeline run, Soda Core validates:

- No null values on `video_id`, `title`, `published_at`
- No negative values on `view_count`, `like_count`, `comment_count`
- `video_type` contains only `shorts` or `normal`
- Bridge table `core_video_topics` has no null `video_id` or `topic` values

If any check fails, the Airflow task fails and no silent bad data enters the core layer.

---

## Future Improvements

- CI/CD with GitHub Actions
- Integration tests with pytest
- Kubernetes deployment
- Monitoring with Prometheus & Grafana
- PostgreSQL table partitioning by `publish_date`
- dbt for transformation layer management
- Data Lake integration