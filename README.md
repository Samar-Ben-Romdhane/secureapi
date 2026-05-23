# SecureAPI Gateway

A mini DevSecOps project: a JWT-authenticated REST API with a full CI/CD pipeline including SAST scanning and container vulnerability analysis.

## Stack

| Layer | Tool |
|---|---|
| API | Python / Flask |
| Auth | JWT (PyJWT) |
| Rate limiting | flask-limiter |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Container | Docker + docker-compose |
| CI/CD | GitHub Actions |
| SAST | Bandit |
| Image scan | Trivy |
| Registry | DockerHub |

## Project structure

```
secureapi/
├── src/
│   ├── app.py                  # Flask app factory
│   ├── middleware/
│   │   └── auth.py             # JWT middleware
│   ├── models/
│   │   └── models.py           # SQLAlchemy models
│   └── routes/
│       ├── auth.py             # /auth/register, /auth/login
│       └── tasks.py            # /tasks CRUD
├── tests/
│   └── test_api.py             # pytest test suite
├── .github/workflows/
│   └── ci.yml                  # GitHub Actions pipeline
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── pyproject.toml
```

## Local setup

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd secureapi

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov flake8 bandit

# 4. Set up environment variables
cp .env.example .env
# Edit .env and set a strong SECRET_KEY

# 5. Run the API
python -m src.app
```

## Running tests

```bash
# All tests with coverage
pytest tests/ -v --cov=src

# Lint
flake8 src/ tests/ --max-line-length=100

# Security scan
bandit -r src/
```

## Docker

```bash
# Build and start
docker-compose up --build

# Test the health endpoint
curl http://localhost:5000/health
```

## API endpoints

### Auth
| Method | Endpoint | Body | Auth required |
|---|---|---|---|
| POST | /auth/register | `{username, password}` | No |
| POST | /auth/login | `{username, password}` | No |

### Tasks
| Method | Endpoint | Body | Auth required |
|---|---|---|---|
| GET | /tasks/ | — | Yes |
| POST | /tasks/ | `{title, description?}` | Yes |
| GET | /tasks/:id | — | Yes |
| PATCH | /tasks/:id | `{title?, description?, done?}` | Yes |
| DELETE | /tasks/:id | — | Yes |

All protected routes require `Authorization: Bearer <token>` header.

## GitHub Actions setup

Add these secrets to your GitHub repository (Settings → Secrets):

- `DOCKERHUB_USERNAME` — your DockerHub username
- `DOCKERHUB_TOKEN` — a DockerHub access token (not your password)

The pipeline runs automatically on every push to `main` or `develop`.

## Security features

- Passwords hashed with Werkzeug `pbkdf2:sha256`
- JWT tokens expire after 24 hours
- Rate limiting: 100 req/hour, 20 req/minute per IP
- Non-root Docker user
- Read-only container filesystem
- `no-new-privileges` security option
- Secrets injected via environment variables (never hardcoded)
- Bandit SAST scan blocks on HIGH severity findings
- Trivy blocks on CRITICAL/HIGH CVEs in the image
