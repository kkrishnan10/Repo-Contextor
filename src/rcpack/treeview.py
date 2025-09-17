"""Tree view generation for repository structure."""

from pathlib import Path
from typing import Dict, List


def create_tree_view(repo_path: Path, files_data: Dict[str, str]) -> str:
    """Create a tree view of the repository structure."""
    paths = list(files_data.keys())
    return render_tree(paths)


def render_tree(paths: List[str]) -> str:
    """Render a tree view from a list of relative POSIX paths."""
    tree_structure: dict = {}

    for p in paths:
        parts = Path(p).parts
        current = tree_structure
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        if parts:
            current[parts[-1]] = None

    def _render(structure: dict, prefix: str = "") -> str:
        lines = []
        items = sorted(structure.items(), key=lambda x: (x[1] is None, x[0]))
        for i, (name, subtree) in enumerate(items):
            is_last = i == len(items) - 1
            lines.append(f"{prefix}{'└── ' if is_last else '├── '}{name}")
            if subtree is not None:
                extension = ("    " if is_last else "│   ")
                lines.append(_render(subtree, prefix + extension))
        return "\n".join(filter(None, lines))

    if not tree_structure:
        return "No files found"
    return _render(tree_structure)