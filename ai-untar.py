#!/usr/bin/env python3
"""
ai-untar.py - Extract archives produced by ai-tar.py (format v2).

Parser is tolerant of transport-induced changes: normalizes CRLF/CR to LF,
tolerates whitespace inside base64 bodies, validates paths against
zip-slip-style escapes.
"""

import argparse
import base64
import os
import re
import sys
from pathlib import Path

DELIM_RE = re.compile(
    r'^<<<FILE\|(?P<nonce>[0-9a-f]+)\|(?P<enc>utf8|base64|symlink)\|(?P<body>[^>\n]+)>>>$',
    re.MULTILINE,
)
END_RE = re.compile(r'^<<<END\|(?P<nonce>[0-9a-f]+)>>>\s*$', re.MULTILINE)


def b64_decode_path(s: str) -> str:
    pad = '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad).decode('utf-8')


def parse_archive(text: str):
    """Yield (rel_path, kind, payload) for each file.

    kind is one of {'utf8', 'base64', 'symlink'}.
    payload is bytes for utf8/base64, and the target string for symlink.
    """
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    file_matches = list(DELIM_RE.finditer(text))
    if not file_matches:
        return

    nonce = file_matches[0]['nonce']
    file_matches = [m for m in file_matches if m['nonce'] == nonce]

    end_match = None
    for m in END_RE.finditer(text):
        if m['nonce'] == nonce:
            end_match = m
            break

    boundaries = [(m.start(), m.end(), m) for m in file_matches]
    if end_match:
        boundaries.append((end_match.start(), end_match.end(), None))
    else:
        boundaries.append((len(text), len(text), None))

    for i in range(len(boundaries) - 1):
        _start, end, m = boundaries[i]
        next_start = boundaries[i + 1][0]

        content_start = end + 1 if end < len(text) and text[end:end + 1] == '\n' else end
        content_end = next_start
        if content_end > content_start and text[content_end - 1:content_end] == '\n':
            content_end -= 1

        enc = m['enc']
        body = m['body']

        if enc == 'utf8':
            rel_path = b64_decode_path(body)
            payload = text[content_start:content_end].encode('utf-8')
            yield rel_path, 'utf8', payload
        elif enc == 'base64':
            rel_path = b64_decode_path(body)
            b64_text = re.sub(r'\s+', '', text[content_start:content_end])
            payload = base64.b64decode(b64_text) if b64_text else b''
            yield rel_path, 'base64', payload
        elif enc == 'symlink':
            parts = body.split('|', 1)
            if len(parts) != 2:
                continue
            rel_path = b64_decode_path(parts[0])
            target = b64_decode_path(parts[1])
            yield rel_path, 'symlink', target


def _safe_output_path(output_dir: Path, rel_path: str) -> Path:
    out = (output_dir / rel_path).resolve()
    base = output_dir.resolve()
    if out != base and base not in out.parents:
        raise ValueError(f"refusing unsafe path: {rel_path!r}")
    return out


def extract(archive_path: Path, output_dir: Path, verbose=False):
    text = archive_path.read_text(encoding='utf-8')

    if output_dir is None:
        output_dir = Path(archive_path.stem)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    n_files = n_links = 0
    for rel_path, kind, payload in parse_archive(text):
        out = _safe_output_path(output_dir, rel_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if kind == 'symlink':
            if out.is_symlink() or out.exists():
                out.unlink()
            os.symlink(payload, out)
            n_links += 1
            msg = f"[+] symlink: {rel_path} -> {payload}" if verbose else f"[+] {rel_path}"
        else:
            out.write_bytes(payload)
            n_files += 1
            msg = (f"[+] {kind}: {rel_path} ({len(payload)} bytes)"
                   if verbose else f"[+] {rel_path}")
        print(msg, file=sys.stderr)

    print(f"\n[OK] Extracted {n_files} files and {n_links} symlinks to {output_dir}",
          file=sys.stderr)
    return n_files + n_links


def main():
    parser = argparse.ArgumentParser(
        description="Extract archives produced by ai-tar (format v2)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    ai-untar project.txt                  # extract to ./project/
    ai-untar project.txt -o path/out      # extract to specific directory
    ai-untar project.txt -v               # verbose
        """,
    )
    parser.add_argument('archive')
    parser.add_argument('-o', '--output')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    archive_path = Path(args.archive)
    if not archive_path.exists():
        print(f"Error: archive not found: {archive_path}", file=sys.stderr)
        return 1

    try:
        extract(archive_path,
                output_dir=Path(args.output) if args.output else None,
                verbose=args.verbose)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
