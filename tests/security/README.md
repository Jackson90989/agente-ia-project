Security tests

- test_security_tools.py runs bandit
- pip-audit is run separately to avoid hangs on Windows
- install dev tools: pip install -r requirements-dev.txt
- run bandit: pytest -m security
- run pip-audit: python -m pip_audit -r requirements.txt --timeout 30
