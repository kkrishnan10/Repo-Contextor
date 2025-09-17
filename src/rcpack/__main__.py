#!/usr/bin/env python3
"""Module entry point to enable `python -m rcpack`.

This simply delegates to the CLI's main() function.
"""

from .cli import main


if __name__ == "__main__":
    main()


