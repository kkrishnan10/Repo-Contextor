from __future__ import annotations
import json

try:
    import yaml
except ImportError:
    yaml = None


def render_json(root, repo_info, tree_text, files, total_files, total_lines,recent_files=None, file_sizes=None) -> str:
    data = {
        "root": root,
        "repo_info": repo_info,
        "structure": tree_text,
        "recent_changes": recent_files or [],
        "files": files,
        "file_sizes": file_sizes or {},
        "summary": {"total_files": total_files, "total_lines": total_lines},
        
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def render_yaml(root, repo_info, tree_text, files, total_files, total_lines,recent_files=None, file_sizes=None) -> str:
    if yaml is None:
        raise RuntimeError("PyYAML not installed; run `pip install pyyaml`")
    data = {
        "root": root,
        "repo_info": repo_info,
        "structure": tree_text,
        "recent_changes": recent_files or [],
        "files": files,
        "file_sizes": file_sizes or {},
        "summary": {"total_files": total_files, "total_lines": total_lines},
        
    }
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
