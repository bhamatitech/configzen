import os
from typing import Any


class ConfigDict(dict):
    """A dictionary that allows dot-access and recursive attribute lookup."""

    def __init__(self, data: dict[str, Any]):
        # Convert nested dicts into ConfigDicts recursively
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = ConfigDict(value)
        super().__init__(data)

    def __getattr__(self, item):
        if item in self:
            return self[item]
        # This makes it clear which key was missing in a dot-access chain
        raise AttributeError(f"Configuration key '{item}' is missing.")


def _merge_env_vars(data: dict, prefix: str, case_sensitive: bool = True) -> dict:
    prefix = f"{prefix}_"
    for env_key, env_val in os.environ.items():
        if not env_key.startswith(prefix):
            continue

        # CONFIGZEN_DB__HOST -> ['DB', 'HOST']
        parts = env_key[len(prefix):].split("__")
        current = data

        for i, part in enumerate(parts):
            # Find matching key
            target_key = part
            existing_key = next((k for k in current if k.lower() == part.lower()), None) if isinstance(current,
                                                                                                       dict) else None

            if existing_key:
                target_key = existing_key
            elif not case_sensitive:
                target_key = part.lower()

            if i == len(parts) - 1:  # At the leaf
                if isinstance(current, dict):
                    current[target_key] = _cast_value(current.get(target_key), env_val)
            else:  # Navigating deeper
                if isinstance(current, dict):
                    if target_key not in current or not isinstance(current[target_key], dict):
                        current[target_key] = {}
                    current = current[target_key]
    return data

def _cast_value(original_val, new_val: str):
    if original_val is None:
        return new_val
    target_type = type(original_val)
    if target_type is bool:
        return new_val.lower() in ("true", "1", "yes", "on")
    try:
        return target_type(new_val)
    except (ValueError, TypeError):
        return new_val