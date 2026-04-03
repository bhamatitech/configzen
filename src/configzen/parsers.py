import json
import os

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[import-untyped]
    except ImportError:
        tomllib = None

def load_file(filepath: str):
    if not os.path.exists(filepath):
        # A clear, specific error message
        raise FileNotFoundError(f"Config file not found at: {os.path.abspath(filepath)}")

    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.json':
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError(
                f"JSON root must be an object, got {type(data).__name__}"
            )
        return data

    elif ext == '.toml':
        if tomllib is None:
            raise ImportError(
                "TOML requires Python 3.11+ or: pip install configzen[toml]"
            )
        with open(filepath, "rb") as f:  # tomllib requires binary mode
            return tomllib.load(f)

    elif ext in ['.yaml', '.yml']:
        if not HAS_YAML:
            raise ImportError(
                "YAML support is missing. Install it with: pip install configzen[yaml]"
            )
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data is None:
            return {}
        if not isinstance(data, dict):
            raise ValueError(
                f"YAML root must be a mapping (object), got {type(data).__name__}"
            )
        return data

    else:
        raise ValueError(f"Unsupported file extension: {ext}")