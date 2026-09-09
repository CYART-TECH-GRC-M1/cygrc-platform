# cygrc-platform

CyGRC Platform - Governance, Risk & Compliance SaaS Platform

## Project Overview

CyGRC Platform is a Governance, Risk & Compliance (GRC) SaaS platform.

## Development Branch

Development work is organized through feature branches.

Before merging changes into the main branch:

1. Create or use a feature branch.
2. Commit changes to the feature branch.
3. Push the branch to GitHub.
4. Create a Pull Request.
5. Wait for the required CI checks and approvals.

## CI Pipeline

The project uses GitHub Actions for continuous integration.

The CI pipeline currently includes:

- Repository checkout
- Python 3.12 setup
- Repository structure check
- Ruff linting for Python code

If Python files are present, Ruff checks the repository for linting issues.

## Secret Scanning

The project includes a GitHub Actions workflow for secret scanning using Gitleaks.

The secret scanner runs on:

- Pushes to `main`
- Pushes to `develop`
- Pushes to feature branches
- Pull Requests

## Architecture Decision Records

Architecture and design decisions are documented using ADRs.

ADR templates are located in:

`docs/adr/`

New architecture decisions should follow the ADR template provided there.

## Testing

Automated application testing will be integrated into the CI pipeline when the project's test suite is available.

## RLS Testing

RLS test integration into CI is pending availability of the RLS test suite.

## Local Development

Project-specific local development and service setup instructions will be added as the application components are integrated.

## Contributing

Keep changes focused on the relevant feature or task.

Do not commit secrets, credentials, or sensitive configuration files.

Use Pull Requests for changes intended for the main branch.
