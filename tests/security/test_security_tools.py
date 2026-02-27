from pathlib import Path
import importlib.util
import subprocess
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _run(cmd, timeout=120):
    try:
        return subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        pytest.fail(f"Command timed out after {timeout}s: {cmd}")


def _run_pip_audit(cmd, timeout=45):
    process = subprocess.Popen(
        cmd,
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        return process.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        pytest.fail(
            f"pip-audit timed out after {timeout}s.\n{stdout}\n{stderr}"
        )


@pytest.mark.security
def test_bandit_scan():
    if importlib.util.find_spec("bandit") is None:
        pytest.skip("bandit not installed")
    targets = [
        PROJECT_ROOT / "app.py",
        PROJECT_ROOT / "routes",
        PROJECT_ROOT / "services",
        PROJECT_ROOT / "agente-ia",
        PROJECT_ROOT / "database.py",
        PROJECT_ROOT / "models.py",
        PROJECT_ROOT / "config.py",
    ]
    cmd = [sys.executable, "-m", "bandit", "-r", "-x", "ambiente,tests,agente-ia/ambiente"]
    cmd.extend(str(target) for target in targets if target.exists())
    result = _run(cmd)
    assert result.returncode == 0, result.stdout + "\n" + result.stderr


@pytest.mark.security
@pytest.mark.skip(reason="Run pip-audit separately: python -m pip_audit -r requirements.txt --timeout 30")
def test_pip_audit():
    pass
