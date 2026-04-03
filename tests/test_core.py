import os
import json

import pytest

import configzen
from configzen.core import ConfigDict

# --- JSON TESTING ---

def test_load_json(tmp_path):
    # Create a temporary config file
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "config.json"
    p.write_text(json.dumps({"port": 8080}))

    # Load it
    config = configzen.load(str(p))
    assert config.port == 8080


def test_json_non_dict_root_raises(tmp_path):
    p = tmp_path / "config.json"
    p.write_text(json.dumps([1, 2, 3]))

    with pytest.raises(ValueError, match="JSON root must be an object"):
        configzen.load(str(p))


def test_configdict_does_not_mutate_nested_input():
    inner = {"port": 5432}
    data = {"db": inner}
    cfg = ConfigDict(data)
    inner["port"] = 9999
    assert cfg.db.port == 5432


# --- ENV OVERRIDE TESTING ---

def test_env_override(tmp_path):
    p = tmp_path / "config.json"
    p.write_text(json.dumps({"port": 8080}))

    # Set env var
    os.environ["CONFIGZEN_PORT"] = "9999"

    config = configzen.load(str(p))
    assert config.port == 9999

    # Cleanup env var so it doesn't mess up other tests
    del os.environ["CONFIGZEN_PORT"]


# --- TOML TESTING ---

def test_load_toml(tmp_path):
    """
    Test TOML loading.
    This will automatically SKIP if no TOML parser (built-in or tomli) is found.
    """
    # This is the magic line for Python 3.9/3.10 compatibility
    pytest.importorskip("tomli") if __import__("sys").version_info < (3, 11) else None

    p = tmp_path / "config.toml"
    p.write_text('title = "Zen App"\nport = 5000')

    config = configzen.load(str(p))
    assert config.title == "Zen App"
    assert config.port == 5000


# --- YAML TESTING ---

def test_load_yaml(tmp_path):
    """This will automatically SKIP if PyYAML is not installed."""
    pytest.importorskip("yaml")

    p = tmp_path / "config.yaml"
    p.write_text("app:\n  name: ZenApp\n  debug: true")

    config = configzen.load(str(p))
    assert config.app.name == "ZenApp"
    assert config.app.debug is True


def test_load_empty_yaml(tmp_path):
    pytest.importorskip("yaml")

    p = tmp_path / "config.yaml"
    p.write_text("# only comments\n")

    config = configzen.load(str(p))
    assert dict(config) == {}


def test_yaml_non_dict_root_raises(tmp_path):
    pytest.importorskip("yaml")

    p = tmp_path / "config.yaml"
    p.write_text("[1, 2, 3]\n")

    with pytest.raises(ValueError, match="YAML root must be a mapping"):
        configzen.load(str(p))


# --- ENV OVERRIDE TESTING (Cross-Format) ---

@pytest.mark.parametrize("ext, content", [
    ("json", '{"db": {"host": "localhost"}}'),
    ("toml", '[db]\nhost = "localhost"'),
    ("yaml", 'db:\n  host: localhost'),
])
def test_cross_format_overrides(tmp_path, ext, content):
    """Tests that the double-underscore override works regardless of file format."""
    # Skip logic for YAML/TOML within the loop
    if ext == "yaml": pytest.importorskip("yaml")
    if ext == "toml" and __import__("sys").version_info < (3, 11):
        pytest.importorskip("tomli")

    p = tmp_path / f"config.{ext}"
    p.write_text(content)

    os.environ["CONFIGZEN_DB__HOST"] = "127.0.0.1"

    try:
        config = configzen.load(str(p))
        assert config.db.host == "127.0.0.1"
    finally:
        if "CONFIGZEN_DB__HOST" in os.environ:
            del os.environ["CONFIGZEN_DB__HOST"]


def test_case_insensitive_override(tmp_path):
    p = tmp_path / "config.json"
    # Case 1: Existing key with different casing
    p.write_text(json.dumps({"Database": {"Port": 5432}}))

    os.environ["CONFIGZEN_DATABASE__PORT"] = "9000"

    try:
        # In Strict Mode, we now expect it to SMART-MATCH
        # because we want to avoid duplicate keys like 'Port' and 'PORT'
        config = configzen.load(str(p), case_sensitive=True)
        assert config.Database.Port == 9000

        # Case 2: Brand-new key with case-insensitivity
        # Let's add a NEW env var that doesn't exist in the file
        os.environ["CONFIGZEN_NEWKEY"] = "value"

        # If case_sensitive is False, config.newkey should work
        # even though it was set as NEWKEY
        config_zen = configzen.load(str(p), case_sensitive=False)
        assert config_zen.newkey == "value"

    finally:
        if "CONFIGZEN_DATABASE__PORT" in os.environ:
            del os.environ["CONFIGZEN_DATABASE__PORT"]
        if "CONFIGZEN_NEWKEY" in os.environ:
            del os.environ["CONFIGZEN_NEWKEY"]