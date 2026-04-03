# configzen 🧘

The simplest way to handle configuration in Python.

- **Zero config:** Point at a file, or let configzen find a single default file in the current working directory.
- **Dot access:** `config.db.port` instead of `config["db"]["port"]`.
- **Env overrides:** Override file values with environment variables (default prefix `CONFIGZEN`).
- **Type-aware env values:** When a key already exists in the file, env strings are cast to match that value’s type.

## Installation

```bash
pip install configzen
pip install configzen[yaml]   # YAML files
pip install configzen[toml]   # TOML on Python < 3.11 (uses tomli)
pip install configzen[all]    # YAML + tomli
```

## Usage

```python
import configzen

# Load a specific file (JSON, YAML, or TOML by extension)
config = configzen.load("config.json")
print(config.host, config.port)

# Auto-pick a file in the process working directory: exactly one of
# config.toml, config.yaml, config.yml, config.json must exist
config = configzen.load()

# Nested objects (the file root must be a JSON/YAML object, not an array)
# config.database.host

# Environment overrides — prefix + key, or prefix + SECTION__KEY for nesting
# export CONFIGZEN_PORT=3000
# export CONFIGZEN_DATABASE__HOST=db.example.com
config = configzen.load("config.json")

# Custom prefix and key matching
config = configzen.load("app.json", env_prefix="MYAPP", case_sensitive=False)
```

## Caveats

`ConfigDict` subclasses `dict`, so dot access uses normal attribute rules: names that already exist on `dict` (for example `items`, `keys`, `values`, `get`, `update`) refer to those methods, not to a config key with the same name. Keys like that still work with brackets or `.get()`, e.g. `config["items"]` or `config.get("items")`.

## License

MIT — see [LICENSE](LICENSE).
