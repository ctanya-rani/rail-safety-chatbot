import importlib

from railsafe import config


def _reload(monkeypatch, **env):
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return importlib.reload(config)


def test_defaults_when_unset(monkeypatch):
    for key in ("RAILSAFE_MODEL", "RAILSAFE_TOP_K", "RAILSAFE_MAX_TOKENS"):
        monkeypatch.delenv(key, raising=False)
    cfg = importlib.reload(config)
    assert cfg.MODEL == "claude-opus-4-8"
    assert cfg.DEFAULT_TOP_K == 6
    assert cfg.MAX_TOKENS == 16000


def test_env_overrides(monkeypatch):
    cfg = _reload(monkeypatch, RAILSAFE_MODEL="claude-sonnet-5", RAILSAFE_TOP_K="3")
    assert cfg.MODEL == "claude-sonnet-5"
    assert cfg.DEFAULT_TOP_K == 3


def test_blank_env_falls_back_to_default(monkeypatch):
    # Hosting dashboards create set-but-empty variables; these must not crash
    # the process at import time or silently become invalid values.
    cfg = _reload(monkeypatch, RAILSAFE_MODEL="   ", RAILSAFE_TOP_K="")
    assert cfg.MODEL == "claude-opus-4-8"
    assert cfg.DEFAULT_TOP_K == 6


def test_corpus_path_resolves_under_project_root():
    cfg = importlib.reload(config)
    assert cfg.CORPUS_DIR.is_dir()
    assert cfg.CHUNKS_FILE.parent == cfg.INDEX_DIR
