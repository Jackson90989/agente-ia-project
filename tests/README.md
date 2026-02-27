Test structure

- tests/unit: fast unit tests (no IO)
- tests/integration: tests that talk to HTTP, DB, or MCP
- tests/regression: scripts that guard fixed bugs
- tests/security: vulnerability checks (bandit, pip-audit)

Notes

- Many existing tests are runnable scripts and may need services running.
- Use pytest markers to filter: pytest -m unit|integration|regression|security
