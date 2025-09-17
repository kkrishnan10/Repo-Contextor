from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, Tuple

from rcpack.discover import discover_files
from rcpack.gitinfo import get_git_info, is_git_repo
from rcpack.io_utils import read_text_safely, is_binary_file
from rcpack.renderer import markdown as md_renderer
from rcpack.renderer.jsonyaml import render_json, render_yaml
from rcpack.treeview import render_tree


def _find_root(inputs: list[str]) -> Path:
    paths = [Path(p) for p in inputs]
    if len(paths) == 1 and Path(paths[0]).is_dir():
        return paths[0].resolve()
    parents = [p if p.is_dir() else p.parent for p in paths]
    root = Path(*Path.commonpath([str(p.resolve()) for p in parents]).split("/"))
    return root.resolve()


def build_package(
    inputs: list[str],
    include_patterns: list[str] | None,
    exclude_patterns: list[str] | None,
    max_file_bytes: int,
    fmt: str = "markdown",
) -> Tuple[str, dict]:
    root = _find_root(inputs)
    root_abs = root.resolve()

    repo_info = (
        get_git_info(root_abs) if is_git_repo(root_abs) else {
            "is_repo": False,
            "commit": None,
            "branch": None,
            "author": None,
            "date": None,
            "note": "Not a git repository",
        }
    )

    files = discover_files(
        inputs=[Path(p) for p in inputs],
        root=root_abs,
        include_patterns=include_patterns or [],
        exclude_patterns=exclude_patterns or [],
    )
    rel_files = [f.relative_to(root_abs) for f in files]

    project_tree = render_tree([p.as_posix() for p in rel_files])

    file_sections: list[dict] = []
    total_lines = 0
    total_chars = 0

    for f in files:
        rel = f.relative_to(root_abs).as_posix()
        try:
            if is_binary_file(f):
                content = f"[binary file skipped: {f.name}, {f.stat().st_size} bytes]"
                file_sections.append({
                    "path": rel,
                    "language": _language_from_ext(f.suffix),
                    "content": content,
                    "is_truncated": False,
                })
                total_chars += len(content)
                continue

            content, used_encoding, truncated = read_text_safely(f, max_bytes=max_file_bytes)
            total_lines += content.count("\n") + (1 if content and not content.endswith("\n") else 0)
            total_chars += len(content)

            if truncated:
                note = f"\n\n[... TRUNCATED to first {max_file_bytes} bytes ...]"
                content = content + note
                total_chars += len(note)

            file_sections.append({
                "path": rel,
                "language": _language_from_ext(f.suffix),
                "content": content,
                "is_truncated": truncated,
            })
        except Exception as exc:
            print(f"[rcpack] error reading {rel}: {exc}", file=sys.stderr)
            continue

    # render in chosen format
    if fmt == "markdown":
        out_text = md_renderer.render_markdown(
            root=str(root_abs),
            repo_info=repo_info,
            tree_text=project_tree,
            files=file_sections,
            total_files=len(file_sections),
            total_lines=total_lines,
        )
    elif fmt == "json":
        out_text = render_json(
            root=str(root_abs),
            repo_info=repo_info,
            tree_text=project_tree,
            files=file_sections,
            total_files=len(file_sections),
            total_lines=total_lines,
        )
    elif fmt == "yaml":
        out_text = render_yaml(
            root=str(root_abs),
            repo_info=repo_info,
            tree_text=project_tree,
            files=file_sections,
            total_files=len(file_sections),
            total_lines=total_lines,
        )
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    stats = {"files": len(file_sections), "lines": total_lines, "chars": total_chars}
    return out_text, stats


def _language_from_ext(ext: str) -> str:
    ext = ext.lower().lstrip(".")
    mapping = {
        "py": "python", "js": "javascript", "ts": "typescript",
        "json": "json", "md": "markdown", "yml": "yaml", "yaml": "yaml",
        "toml": "toml", "sh": "bash", "c": "c", "cpp": "cpp",
        "java": "java", "go": "go", "rs": "rust",
    }
    return mapping.get(ext, "")
