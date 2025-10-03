# src/cli.py
import argparse
import sys
from pathlib import Path

from packager import package_repository
from config_loader import load_config
# If your environment requires package-relative imports, change the two lines above to:
# from .packager import package_repository
# from .config_loader import load_config

def main():
    parser = argparse.ArgumentParser(
        prog="repo-contextor",
        description="Repository Context Packager CLI"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Repository path to analyze (default: current directory)"
    )
    parser.add_argument(
        "-o", "--output",
        dest="output",
        default=None,
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "-f", "--format",
        dest="format",
        choices=["text", "json", "yaml"],
        default=None,
        help="Output format (default: text)"
    )
    parser.add_argument(
        "-r", "--recent",
        dest="recent",
        action="store_true",
        default=None,
        help="Include only files modified in the last 7 days"
    )

    args = parser.parse_args()

    # ---------------- TOML config integration ----------------
    KNOWN_KEYS = ("path", "output", "format", "recent")
    DEFAULTS = {
        "path": str(Path.cwd()),
        "output": None,     # stdout
        "format": "text",   # default per README
        "recent": False,
    }

    cli_cfg = {
        "path": args.path,
        "output": args.output,
        "format": args.format,
        "recent": args.recent,
    }

    # Merge precedence: CLI > TOML > DEFAULTS
    cfg = load_config(
        dotfile=".repo-contextor.toml",
        defaults=DEFAULTS,
        cli_cfg=cli_cfg,
        known_keys=KNOWN_KEYS
    )

    # Overwrite argparse namespace so the rest of the code remains unchanged
    args.path = cfg["path"]
    args.output = cfg["output"]
    args.format = cfg["format"]
    args.recent = cfg["recent"]
    # ----------------------------------------------------------

    # Execute main logic
    result = package_repository(
        repo_path=args.path,
        output=args.output,
        format=args.format,
        recent=args.recent,
    )

    if result is not None:
        sys.exit(result)

if __name__ == "__main__":
    main()
