#!/usr/bin/env python3
"""CLI for Repository Context Packager."""

import argparse
import sys
from pathlib import Path
from .gitinfo import get_git_info
from .discover import discover_files
from .treeview import create_tree_view
from .renderer.markdown import render_markdown
from .renderer.jsonyaml import render_json, render_yaml
from .io_utils import write_output
from datetime import datetime, timedelta


def main():
    parser = argparse.ArgumentParser(
        description="Package repository content for LLM context"
    )
    parser.add_argument(
        "path", 
        nargs="?", 
        default=".", 
        help="Repository path (default: current directory)"
    )
    parser.add_argument(
        "-o", "--output", 
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "-f", "--format", 
        choices=["text", "json", "yaml"], 
        default="text",
        help="Output format (default: text)"
    )

    """ This will read -r from the console and able to search it with this"""
    parser.add_argument(
    "-r", "--recent",
    action="store_true",
    help="Include only files modified in the last 7 days"
    )
    
    args = parser.parse_args()
    
    try:
        repo_path = Path(args.path).resolve()
        if not repo_path.exists():
            print(f"Error: Path {repo_path} does not exist", file=sys.stderr)
            sys.exit(1)
            
        # Get repository information
        repo_info = get_git_info(repo_path)
        
        # Discover files
        discovered_files = discover_files([repo_path], repo_path, [], [])
        
        # will check the file in last 7 days
        if args.recent:
            seven_days_ago = datetime.now() - timedelta(days=7)
            recent_files = []
            for f in discovered_files:
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    if mtime >= seven_days_ago:
                        recent_files.append(f)
                except Exception:
                    continue
            discovered_files = recent_files
        
        # Read file contents
        files_data = {}
        for file_path in discovered_files:
            try:
                relative_path = file_path.relative_to(repo_path)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                files_data[str(relative_path)] = content
            except (UnicodeDecodeError, PermissionError):
                files_data[str(relative_path)] = f"[Binary or unreadable file: {file_path.name}]"
            except Exception:
                continue
        
        # Create tree view
        tree_text = create_tree_view(repo_path, files_data)
        
        # Count totals
        total_files = len(files_data)
        total_lines = sum(len(content.splitlines()) for _, content in files_data.items())
        
        # Render based on format
        if args.format == "json":
            content = render_json(
                str(repo_path), repo_info, tree_text, 
                files_data, total_files, total_lines,
                recent_files=[str(f.relative_to(repo_path)) for f in discovered_files] if args.recent else []
            )
        elif args.format == "yaml":
            content = render_yaml(
                str(repo_path), repo_info, tree_text, 
                files_data, total_files, total_lines,
                recent_files=[str(f.relative_to(repo_path)) for f in discovered_files] if args.recent else []
            )
        else:  # text/markdown
            content = render_markdown(
                str(repo_path), repo_info, tree_text, 
                files_data, total_files, total_lines,
                recent_files=[str(f.relative_to(repo_path)) for f in discovered_files] if args.recent else []
            )
        
        if args.output:
            # Write to file
            write_output(args.output, content)
            print(f"Context package created: {args.output}")
        else:
            # Output to stdout
            print(content)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
