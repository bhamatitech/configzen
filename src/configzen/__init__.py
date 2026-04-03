import os
from typing import Optional
from .core import ConfigDict, _merge_env_vars
from .parsers import load_file

DEFAULT_NAMES = ["config.toml", "config.yaml", "config.yml", "config.json"]


def load(filepath: Optional[str] = None, env_prefix: str = "CONFIGZEN", case_sensitive: bool = True) -> ConfigDict:
    """
    Load a configuration file.
    Raises an error if multiple default config files are found to avoid ambiguity.
    """
    target_path = filepath

    if target_path is None:
        # Find all existing default files
        found_files = [name for name in DEFAULT_NAMES if os.path.exists(name)]

        if len(found_files) > 1:
            raise RuntimeError(
                f"ConfigZen: Multiple config files found: {', '.join(found_files)}. "
                "Please delete the extras or specify which one to load: load('filename.json')"
            )

        if len(found_files) == 1:
            target_path = found_files[0]
        else:
            raise FileNotFoundError(
                f"ConfigZen: No config file found. Expected one of: {', '.join(DEFAULT_NAMES)}"
            )

    data = load_file(target_path)
    data = _merge_env_vars(data=data, prefix=env_prefix, case_sensitive=case_sensitive)
    return ConfigDict(data)