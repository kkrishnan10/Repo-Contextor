
"""
TOML config loader for Repo-Contextor.

Rules per Lab 4:
- Look for a dotfile in the CURRENT directory: .repo-contextor.toml
- If the file is missing: ignore it (use defaults/CLI)
- If the file exists but is invalid TOML: print a clear error to stderr and exit(1)
- Only recognized keys are applied; unknown keys are ignored
- Precedence: CLI > TOML > DEFAULTS
"""

from __future__ import annotations

import os
import sys
from typing import Dict, Iterable, Any


try:
    import tomllib  
    _toml_loads = tomllib.loads
except ModuleNotFoundError:
    try:
        import tomli  
        _toml_loads = tomli.loads
    except ModuleNotFoundError:
        _toml_loads = None


def _ensure_toml_available() -> None:
    if _toml_loads is None:
        print(
            "Error: TOML parser not available. Use Python 3.11+ (tomllib) "
            "or install 'tomli' for older versions (pip install tomli).",
            file=sys.stderr,
        )
        sys.exit(1)


def _load_toml_file(dotfile: str) -> Dict[str, Any]:
    """Parse TOML and return a dict. If file missing -> {}, if invalid -> exit(1)."""
    _ensure_toml_available()
    if not os.path.exists(dotfile):
        return {}
    try:
        with open(dotfile, "rb") as f:
            raw = f.read().decode("utf-8", errors="strict")
        data = _toml_loads(raw)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        print(f"Error: failed to parse {dotfile} as TOML.\n{e}", file=sys.stderr)
        sys.exit(1)


def _filter_known(d: Dict[str, Any], known: Iterable[str]) -> Dict[str, Any]:
    known_set = set(known)
    return {k: v for k, v in d.items() if k in known_set}


def _merge(defaults: Dict[str, Any],
           toml_cfg: Dict[str, Any],
           cli_cfg: Dict[str, Any],
           known: Iterable[str]) -> Dict[str, Any]:
    """
    Merge in precedence order: CLI > TOML > DEFAULTS.
    Only keys in `known` are considered (unknown ignored).
    """
    known_set = set(known)
    merged: Dict[str, Any] = {k: defaults.get(k) for k in known_set}
    
    for src in (toml_cfg, cli_cfg):
        for k, v in src.items():
            if k in known_set and v is not None:
                merged[k] = v
    return merged


def load_config(*,
                dotfile: str = ".repo-contextor.toml",
                defaults: Dict[str, Any] | None = None,
                cli_cfg: Dict[str, Any] | None = None,
                known_keys: Iterable[str] = ()) -> Dict[str, Any]:
    """
    Public helper used by cli.py

    Parameters
    ----------
    dotfile : str
        Filename to read in the current working directory.
    defaults : dict
        Internal defaults for the tool.
    cli_cfg : dict
        Values parsed from the command line (None for flags not provided).
    known_keys : Iterable[str]
        Keys the tool recognizes. Others will be ignored.

    Returns
    -------
    dict
        Final configuration with precedence CLI > TOML > DEFAULTS.
    """
    defaults = defaults or {}
    cli_cfg = cli_cfg or {}
    known = tuple(known_keys)  

    file_data = _load_toml_file(dotfile)
    toml_filtered = _filter_known(file_data, known)

    return _merge(defaults, toml_filtered, cli_cfg, known)
