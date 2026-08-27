# CyGRC Platform

CyGRC Platform is a Governance, Risk & Compliance (GRC) SaaS platform designed to help organizations manage compliance frameworks, controls, risks, evidence, and related security requirements.

## Project Structure

```text
cygrc-platform/
├── .github/
│   └── workflows/
│       └── backend-ci.yml
├── backend/
├── database/
├── deployment/
│   ├── docker-compose.yml
│   └── .env.example
├── docs/
├── frontend/
├── scripts/
├── tests/
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Backend

The backend is built with Python and FastAPI.

Main backend dependencies include:

* FastAPI
* Uvicorn
* SQLAlchemy
* PostgreSQL drivers
* Alembic
* Pydantic
* Python-JOSE
* Passlib
* HTTPX
* OpenAI/LangChain components
* Pytest

## Docker Services

The Docker Compose configuration in `deployment/docker-compose.yml` provides the following development services:

### PostgreSQL

* PostgreSQL 16.14
* Database: configured through environment variables
* Persistent Docker volume: `postgres_data`
* Default port: `5432`

### Redis

* Redis 7
* Default container port: `6379`

### Keycloak

* Keycloak 26.7.0
* Runs in development mode
* Default port: `8080`

Keycloak is used for authentication and identity-management integration.

## Environment Configuration

The Docker setup uses environment variables for configuration.

The example configuration is available at:

```text
deployment/.env.example
```

Create a local `.env` file based on the example:

```powershell
Copy-Item deployment\.env.example deployment\.env
```

The example file contains development credentials such as:

```text
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=cygrc

REDIS_PORT=6379

KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123
```

These credentials are intended only for local development and testing.

**Do not use the example credentials in a production environment. Never commit real passwords, API keys, tokens, or other secrets to the repository.**

## Running the Development Services

From the repository root, start the Docker services with:

```powershell
docker compose -f deployment/docker-compose.yml --env-file deployment/.env up -d
```

To view running containers:

```powershell
docker ps
```

To stop the services:

```powershell
docker compose -f deployment/docker-compose.yml --env-file deployment/.env down
```

## Python Environment

Create and activate a Python virtual environment if one is not already available.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the application dependencies:

```powershell
python -m pip install -r requirements.txt
```

Install development dependencies:

```powershell
python -m pip install -r requirements-dev.txt
```

## Running the Backend

The FastAPI application is located at:

```text
backend/main.py
```

Run the development server with:

```powershell
python -m uvicorn backend.main:app --reload
```

The application will normally be available at:

```text
http://127.0.0.1:8000
```

FastAPI's interactive API documentation is normally available at:

```text
http://127.0.0.1:8000/docs
```

## Running Tests

Run the test suite with:

```powershell
python -m pytest
```

Using `python -m pytest` ensures that pytest runs through the active Python interpreter and correctly resolves the project package structure.

## Code Quality Checks

Team A's CI workflow performs the following checks:

### Black

Checks Python formatting:

```powershell
black --check backend
```

### isort

Checks import ordering:

```powershell
isort --check-only backend
```

### Flake8

Runs Python linting:

```powershell
flake8 backend
```

### Pytest

Runs the automated tests:

```powershell
python -m pytest
```

## GitHub Actions CI

The Backend CI workflow is located at:

```text
.github/workflows/backend-ci.yml
```

The workflow runs automatically for pushes to:

* `main`
* `teamA/**`

It also runs for pull requests targeting `main`.

The workflow performs:

1. Repository checkout
2. Python 3.10 setup
3. Dependency installation
4. Black formatting check
5. isort import check
6. Flake8 linting
7. Pytest test execution

The workflow also supports manual execution through GitHub Actions using the `workflow_dispatch` trigger.

## Security

Do not commit real secrets to the repository.

Secret Scanning and Push Protection should be enabled by the repository administrator when available. These settings may require GitHub repository-administrator permissions.

Team members should never intentionally commit real credentials to test security scanning.

## Development Notes

The Docker configuration is intended for development and testing.

Before using the platform in a production environment, review:

* Database credentials
* Keycloak administrator credentials
* Secret management
* Docker configuration
* Authentication configuration
* Network exposure
* TLS/HTTPS configuration
* Database security
* GitHub repository security settings

## Team A Contribution

Team A is responsible for repository infrastructure and development automation, including:

* Git repository setup
* Docker support
* Backend CI
* Automated formatting and linting checks
* Automated tests in CI
* Development environment support
* CI/security documentation
* Support for repository security controls
