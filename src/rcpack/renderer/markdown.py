"""Markdown renderer for repository context."""

from typing import Dict, Any


def render_markdown(root: str, repo_info: Dict[str, Any], tree_text: str, 
                   files: Dict[str, str], total_files: int, total_lines: int) -> str:
    """Render repository context as markdown."""
    
    lines = []
    
    # Header
    lines.append(f"# Repository Context: {root}")
    lines.append("")
    
    # Repository info
    if repo_info.get("is_repo"):
        lines.append("## Git Repository Information")
        lines.append(f"- **Branch**: {repo_info.get('branch', 'N/A')}")
        lines.append(f"- **Commit**: {repo_info.get('commit', 'N/A')}")
        lines.append(f"- **Author**: {repo_info.get('author', 'N/A')}")
        lines.append(f"- **Date**: {repo_info.get('date', 'N/A')}")
    else:
        lines.append("## Repository Information")
        lines.append(f"- **Note**: {repo_info.get('note', 'Not a git repository')}")
    lines.append("")
    
    # Summary
    lines.append("## Summary")
    lines.append(f"- **Total Files**: {total_files}")
    lines.append(f"- **Total Lines**: {total_lines}")
    lines.append("")
    
    # Directory structure
    lines.append("## Directory Structure")
    lines.append("```")
    lines.append(tree_text)
    lines.append("```")
    lines.append("")
    
    # File contents
    lines.append("## File Contents")
    lines.append("")
    
    for file_path, content in sorted(files.items()):
        lines.append(f"### {file_path}")
        lines.append("")
        
        # Detect language for syntax highlighting
        ext = file_path.split('.')[-1].lower() if '.' in file_path else ''
        lang_map = {
            'py': 'python', 'js': 'javascript', 'ts': 'typescript',
            'java': 'java', 'cpp': 'cpp', 'c': 'c', 'h': 'c',
            'cs': 'csharp', 'php': 'php', 'rb': 'ruby',
            'go': 'go', 'rs': 'rust', 'swift': 'swift',
            'html': 'html', 'css': 'css', 'scss': 'scss',
            'json': 'json', 'yaml': 'yaml', 'yml': 'yaml',
            'xml': 'xml', 'sql': 'sql', 'sh': 'bash',
            'md': 'markdown', 'dockerfile': 'dockerfile'
        }
        
        language = lang_map.get(ext, '')
        lines.append(f"```{language}")
        lines.append(content)
        lines.append("```")
        lines.append("")
    
    return "\n".join(lines)
