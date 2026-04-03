import os
from typing import Any


def _deep_copy_dict_tree(d: dict[str, Any]) -> dict[str, Any]:
    return {k: _deep_copy_dict_tree(v) if isinstance(v, dict) else v for k, v in d.items()}


class ConfigDict(dict):
    """Dict with dot-access for keys; use bracket access if the key name matches a dict method (e.g. 'items')."""

    def __init__(
        self,
        data: dict[str, Any],
        *,
        _copy: bool = True,
        case_insensitive_access: bool = False,
    ):
        self._case_insensitive_access = case_insensitive_access
        if _copy:
            data = _deep_copy_dict_tree(data)
        for key, value in list(data.items()):
            if isinstance(value, dict):
                data[key] = ConfigDict(
                    value,
                    _copy=False,
                    case_insensitive_access=case_insensitive_access,
                )
        super().__init__(data)

    def __getattr__(self, item):
        if item in self:
            return self[item]
        if self._case_insensitive_access:
            for key in self:
                if isinstance(key, str) and key.lower() == item.lower():
                    return self[key]
        raise AttributeError(f"Configuration key '{item}' is missing.")


def _merge_env_vars(data: dict, prefix: str, case_sensitive: bool = True) -> dict:
    prefix_with_underscore = f"{prefix}_"
    plen = len(prefix_with_underscore)
    prefix_lower = prefix_with_underscore.lower()

    for env_key, env_val in os.environ.items():
        if case_sensitive:
            if not env_key.startswith(prefix_with_underscore):
                continue
        else:
            if len(env_key) < plen or env_key[:plen].lower() != prefix_lower:
                continue

        # CONFIGZEN_DB__HOST -> ['DB', 'HOST']
        parts = env_key[plen:].split("__")
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