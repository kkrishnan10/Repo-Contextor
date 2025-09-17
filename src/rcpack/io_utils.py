"""I/O utilities for file operations."""

from pathlib import Path
from typing import Tuple


def write_output(output_path: str, content: str) -> None:
    """Write content to output file."""
    output_file = Path(output_path)
    
    # Create parent directories if they don't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)


def is_binary_file(path: Path, sniff_bytes: int = 2048) -> bool:
    """Heuristically determine if a file is binary by scanning for NUL bytes."""
    try:
        with open(path, 'rb') as fb:
            chunk = fb.read(sniff_bytes)
        if b"\x00" in chunk:
            return True
        # If the chunk has a lot of non-text bytes, consider it binary
        text_byte_count = sum(32 <= b <= 126 or b in (9, 10, 13) for b in chunk)
        return (len(chunk) - text_byte_count) > max(1, len(chunk) // 3)
    except Exception:
        # If we cannot read, treat as binary to avoid further processing
        return True


def read_text_safely(path: Path, max_bytes: int = 16_384) -> Tuple[str, str, bool]:
    """Read a text file safely with size limit and encoding fallbacks.

    Returns (content, encoding_used, truncated).
    """
    truncated = False
    raw: bytes
    with open(path, 'rb') as fb:
        raw = fb.read(max_bytes + 1)
    if len(raw) > max_bytes:
        truncated = True
        raw = raw[:max_bytes]

    for enc in ("utf-8", "utf-16", "utf-16-le", "utf-16-be", "latin-1"):
        try:
            text = raw.decode(enc)
            return text, enc, truncated
        except Exception:
            continue
    # Fallback: replace errors with utf-8
    text = raw.decode("utf-8", errors="replace")
    return text, "utf-8", truncated