from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict, Any


def _git(cmd: list[str], cwd: Path) -> str:
    # Validate git commands to prevent injection
    allowed_commands = {
        "rev-parse", "show", "log", "status", "branch", "config"
    }
    if not cmd or cmd[0] not in allowed_commands:
        raise ValueError(f"Git command not allowed: {cmd[0] if cmd else 'empty'}")
    
    out = subprocess.check_output(["git", *cmd], cwd=str(cwd), timeout=30)
    return out.decode("utf-8", errors="replace").strip()


def is_git_repo(path: Path) -> bool:
    try:
        flag = _git(["rev-parse", "--is-inside-work-tree"], cwd=path)
        return flag == "true"
    except Exception:
        return False


def get_git_info(path: Path) -> Dict[str, Any]:
    """
    Return info for the current HEAD of a repo rooted at `path`.
    """
    try:
        commit = _git(["rev-parse", "HEAD"], cwd=path)
        branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=path)
        author = _git(["show", "-s", "--format=%an <%ae>"], cwd=path)
        date = _git(["show", "-s", "--date=local", "--format=%ad"], cwd=path)
        return {
            "is_repo": True,
            "commit": commit,
            "branch": branch,
            "author": author,
            "date": date,
            "note": None,
        }
    except Exception:
        # treat as not a repo if anything fails
        return {
            "is_repo": False,
            "commit": None,
            "branch": None,
            "author": None,
            "date": None,
            "note": "Not a git repository",
        }
