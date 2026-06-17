from pathlib import Path


def test_runtime_dependencies_do_not_require_pandas():
    requirements = Path("requirements.txt").read_text(encoding="utf-8")

    assert "pandas" not in requirements.lower()
