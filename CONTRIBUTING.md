# Contributing

Thanks for helping improve QRSCANNER.

## Development Workflow

1. Create a branch from `main`.
2. Set up the project using the steps in `README.md`.
3. Keep changes focused and avoid committing generated files.
4. Run tests before opening a pull request:

```bash
python manage.py test
```

## Code Guidelines

- Follow the existing Django app structure.
- Keep database changes in migrations.
- Use environment variables for secrets and local configuration.
- Do not commit `.env`, local databases, virtual environments, logs, or `__pycache__` files.

## Pull Requests

Include:

- What changed.
- Why the change is needed.
- How it was tested.
- Any required database migrations or deployment steps.

