# JobTracker API

REST API for tracking job applications through every stage of the pipeline. Built with FastAPI, PostgreSQL, and Docker.

## What it does

A backend service that lets you log job applications, update their status as you move through rounds, and get a quick breakdown of where everything stands. Supports filtering, pagination, and per-user isolation via JWT auth.

## Tech stack

- **FastAPI** for the API layer
- **PostgreSQL** for persistence
- **SQLAlchemy** as the ORM
- **JWT** (python-jose + passlib/bcrypt) for auth
- **Docker + Docker Compose** for local dev and deployment
- **pytest** for testing
- **GitHub Actions** for CI

## Running locally

```bash
# start the API + postgres
docker compose up --build

# API is at http://localhost:8000
# docs at http://localhost:8000/docs
```

## API overview

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Create account |
| POST | `/auth/login` | Get JWT token |

### Jobs (all require auth)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/jobs/` | Log a new application |
| GET | `/jobs/` | List your applications (filterable by status, company) |
| GET | `/jobs/stats` | Counts by status |
| GET | `/jobs/{id}` | Get one application |
| PATCH | `/jobs/{id}` | Update status, notes, etc. |
| DELETE | `/jobs/{id}` | Remove an application |

Application statuses: `saved`, `applied`, `phone_screen`, `interview`, `offer`, `rejected`, `withdrawn`

## Running tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## Project structure

```
jobtracker-api/
  app/
    main.py          # FastAPI app setup
    database.py      # SQLAlchemy engine + session
    models.py        # User + JobApplication tables
    schemas.py       # Pydantic request/response models
    auth.py          # JWT + password hashing
    routers/
      auth.py        # signup, login
      jobs.py        # CRUD + filtering + stats
  tests/
    test_api.py      # integration tests
  Dockerfile
  docker-compose.yml
  requirements.txt
```
