# Security Policy

## Supported Versions

This repository currently tracks security updates on the `main` branch.

## Reporting a Vulnerability

Please report security issues privately to the repository owner or maintainer. Do not open a public issue for vulnerabilities that expose credentials, authentication bypasses, database access, or sensitive operational data.

Include:

- A clear description of the issue.
- Steps to reproduce.
- Affected routes, files, or configuration.
- Suggested mitigation, if known.

## Sensitive Data

Never commit:

- `.env` files.
- Database dumps or local database files.
- Production credentials.
- Secret keys.
- User data or operational cylinder records.

The current Django settings contain development defaults. Before production deployment, move `SECRET_KEY`, `DEBUG`, and host configuration into environment variables.

