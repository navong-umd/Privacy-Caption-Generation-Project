"""Neo4j connection settings: the password comes only from NEO4J_PASSWORD, never from config."""
from __future__ import annotations

import pytest

from stage4_ppg import neo4j_loader
from stage4_ppg.neo4j_loader import connection_settings


@pytest.fixture(autouse=True)
def _isolated_env(monkeypatch):
    """Ignore the developer's real .env and any NEO4J_* variables already set."""
    monkeypatch.setattr(neo4j_loader, "load_dotenv", lambda path: [])
    for var in ("NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"):
        monkeypatch.delenv(var, raising=False)


def test_missing_password_fails_with_the_variable_name():
    with pytest.raises(RuntimeError, match="NEO4J_PASSWORD"):
        connection_settings({"uri": "bolt://db:7687", "user": "neo4j", "password": "password"})


def test_password_in_config_is_ignored(monkeypatch):
    monkeypatch.setenv("NEO4J_PASSWORD", "from-env")
    conf = connection_settings({"uri": "bolt://db:7687", "user": "u", "password": "from-config"})
    assert conf == {"uri": "bolt://db:7687", "user": "u", "password": "from-env"}


def test_environment_overrides_config_uri_and_user(monkeypatch):
    monkeypatch.setenv("NEO4J_PASSWORD", "pw")
    monkeypatch.setenv("NEO4J_URI", "bolt://env:7687")
    monkeypatch.setenv("NEO4J_USER", "env-user")
    conf = connection_settings({"uri": "bolt://cfg:7687", "user": "cfg-user"})
    assert (conf["uri"], conf["user"]) == ("bolt://env:7687", "env-user")


def test_defaults_when_config_is_empty(monkeypatch):
    monkeypatch.setenv("NEO4J_PASSWORD", "pw")
    assert connection_settings({}) == {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "pw"}


def test_cypher_runner_passes_the_config_neo4j_block(monkeypatch, tmp_path):
    import sys
    from stage4_ppg import cypher_runner
    cfg = tmp_path / "ppg.yaml"
    cfg.write_text("neo4j:\n  uri: bolt://cfg:7687\n  user: cfg-user\n", encoding="utf-8")
    seen = {}
    monkeypatch.setattr(cypher_runner, "run_query", lambda q, params, neo4j_cfg: seen.update(neo4j_cfg) or [])
    monkeypatch.setattr(sys, "argv", ["cypher_runner", "--run", "list_apps", "--config", str(cfg)])
    cypher_runner.main()
    assert seen == {"uri": "bolt://cfg:7687", "user": "cfg-user"}
