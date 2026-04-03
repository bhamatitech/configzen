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
        import tomllib as tomllib # type: ignore
    except ImportError:
        tomllib = None

def load_file(filepath: str):
    if not os.path.exists(filepath):
        # A clear, specific error message
        raise FileNotFoundError(f"Config file not found at: {os.path.abspath(filepath)}")

    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.json':
        with open(filepath, 'r') as f:
            return json.load(f)

    elif ext == '.toml':
        if tomllib is None:
            raise ImportError(
                "For Python < 3.11, install tomli: pip install tomli"
            )
        with open(filepath, "rb") as f:  # tomllib requires binary mode
            return tomllib.load(f)

    elif ext in ['.yaml', '.yml']:
        if not HAS_YAML:
            raise ImportError(
                "YAML support is missing. Install it with: pip install configzen[yaml]"
            )
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)

    else:
        raise ValueError(f"Unsupported file extension: {ext}")