"""File discovery module for repository analysis."""

from pathlib import Path
from typing import List
import fnmatch


def discover_files(
    inputs: List[Path],
    root: Path,
    include_patterns: List[str],
    exclude_patterns: List[str],
) -> List[Path]:
    """Discover relevant files.

    - inputs: list of files/dirs to scan
    - root: common project root; patterns are matched against POSIX paths relative to root
    - include_patterns: glob patterns to include (if empty, use sensible defaults)
    - exclude_patterns: glob patterns to exclude
    Returns a list of absolute Paths to files.
    """

    default_include_exts = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
        '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
        '.html', '.css', '.scss', '.sass', '.less', '.vue', '.svelte',
        '.md', '.txt', '.rst', '.yaml', '.yml', '.json', '.toml', '.ini',
        '.cfg', '.conf', '.xml', '.sql', '.sh', '.bash', '.zsh', '.fish',
    }

    always_include_names = {
        'README', 'LICENSE', 'CHANGELOG', 'CONTRIBUTING', 'Makefile',
        'requirements.txt', 'package.json', 'Cargo.toml', 'pyproject.toml',
        'setup.py', 'setup.cfg', 'pom.xml', 'build.gradle', '.gitignore', '.gitattributes'
    }

    skip_dir_names = {
        '.git', '.svn', '.hg', '__pycache__', '.pytest_cache',
        'node_modules', '.venv', 'venv', 'env', '.env',
        'build', 'dist', 'target', 'out', '.next', '.nuxt',
        '.idea', '.vscode', '.vs', 'coverage', '.coverage'
    }

    def matches_any(patterns: List[str], rel_posix: str) -> bool:
        return any(fnmatch.fnmatch(rel_posix, pat) for pat in patterns)

    def should_take(file_path: Path) -> bool:
        rel_posix = file_path.relative_to(root).as_posix()
        if exclude_patterns and matches_any(exclude_patterns, rel_posix):
            return False
        if include_patterns:
            return matches_any(include_patterns, rel_posix)
        # default include logic
        return file_path.name in always_include_names or file_path.suffix.lower() in default_include_exts

    discovered: list[Path] = []
    seen = set()

    for item in inputs:
        p = item.resolve()
        if p.is_file():
            # Skip if excluded or in skipped directory
            if any(part in skip_dir_names for part in p.parts):
                continue
            if should_take(p):
                key = p.as_posix()
                if key not in seen:
                    seen.add(key)
                    discovered.append(p)
        elif p.is_dir():
            for child in p.rglob('*'):
                if not child.is_file():
                    continue
                if any(part in skip_dir_names for part in child.parts):
                    continue
                if should_take(child):
                    key = child.resolve().as_posix()
                    if key not in seen:
                        seen.add(key)
                        discovered.append(child.resolve())

    return sorted(discovered)