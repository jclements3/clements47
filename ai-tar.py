#!/usr/bin/env python3
"""
ai-tar.py - Create AI-readable archives for transport through web-based
Claude project files.

Format v2: printable sentinels with a per-archive nonce, hybrid utf8/base64
content encoding. Designed to survive browser/textarea/file-upload paths
that strip C0 control characters or normalize whitespace. Supports binary
files and SVG (base64-encoded inside a .txt archive), bypassing the
web-claude upload-type restriction.

Archive layout:

    # <basename> - AI Archive
    Format: ai-tar v2
    Nonce: <16 hex chars>
    Files: N (utf8=A, base64=B, symlinks=S)
    Generated: YYYY-MM-DD HH:MM:SS

    ---

    <<<FILE|NONCE|utf8|B64PATH>>>
    <plain text content, newline-terminated>
    <<<FILE|NONCE|base64|B64PATH>>>
    <base64 body, 76-col wrapped>
    <<<FILE|NONCE|symlink|B64PATH|B64TARGET>>>
    <<<END|NONCE>>>

A file is stored as utf8 iff its bytes are valid UTF-8 and contain only
printable ASCII plus TAB / LF in the ASCII range. Everything else (CR,
other C0 controls, invalid UTF-8, binary) goes as base64 - exact bytes
preserved.
"""

import argparse
import base64
import datetime
import secrets
import sys
from fnmatch import fnmatch
from pathlib import Path

FORMAT_VERSION = "2"

_PLAIN_ASCII = set(range(0x20, 0x7F)) | {0x09, 0x0A}


def is_plain_utf8_safe(data: bytes) -> bool:
    try:
        data.decode('utf-8')
    except UnicodeDecodeError:
        return False
    for b in data:
        if b < 0x80 and b not in _PLAIN_ASCII:
            return False
    return True


def b64_path(path: str) -> str:
    return base64.urlsafe_b64encode(path.encode('utf-8')).rstrip(b'=').decode('ascii')


def b64_bytes(data: bytes) -> str:
    return base64.b64encode(data).decode('ascii')


def wrap(s: str, width: int = 76) -> str:
    if not s:
        return ''
    return '\n'.join(s[i:i + width] for i in range(0, len(s), width))


def make_nonce() -> str:
    return secrets.token_hex(8)


def should_include_file(file_path, include_ext=None, include_noext=False,
                        include_files=None, exclude_patterns=None):
    if file_path.name.endswith('~'):
        return False
    if file_path.name.startswith('.'):
        return False
    if exclude_patterns:
        for pattern in exclude_patterns:
            if fnmatch(file_path.name, pattern):
                return False
    if include_files:
        return any(fnmatch(file_path.name, p) for p in include_files)
    if include_ext:
        if file_path.suffix:
            return file_path.suffix.lower() in include_ext
        return include_noext
    return True


def collect_files(directory, include_ext=None, include_noext=False,
                  include_files=None, exclude_patterns=None):
    directory = directory.resolve()
    files = []
    symlinks = []
    for item in directory.rglob('*'):
        if item.is_symlink():
            if should_include_file(item, include_ext, include_noext,
                                   include_files, exclude_patterns):
                symlinks.append(item)
        elif item.is_file():
            if should_include_file(item, include_ext, include_noext,
                                   include_files, exclude_patterns):
                files.append(item)
    return sorted(set(files + symlinks)), directory


def encode_entry(rel_path, data, is_symlink, symlink_target, nonce):
    bp = b64_path(rel_path)
    if is_symlink:
        bt = b64_path(symlink_target)
        return f"<<<FILE|{nonce}|symlink|{bp}|{bt}>>>\n", 'symlink'
    if is_plain_utf8_safe(data):
        text = data.decode('utf-8')
        # Always append a separator newline (unconditionally). The parser
        # strips exactly one trailing '\n' from the content slice, so this
        # preserves files that already ended with '\n' without ambiguity.
        return f"<<<FILE|{nonce}|utf8|{bp}>>>\n{text}\n", 'utf8'
    body = wrap(b64_bytes(data))
    if body:
        body = body + '\n'
    return f"<<<FILE|{nonce}|base64|{bp}>>>\n{body}", 'base64'


def build_archive(file_paths, base_path, base_name, directories=None):
    entries_data = []
    for fp in file_paths:
        rel = str(fp.relative_to(base_path))
        if fp.is_symlink():
            entries_data.append((rel, None, True, str(fp.readlink())))
        else:
            entries_data.append((rel, fp.read_bytes(), False, None))

    # Generate nonce; ensure it does not collide with any file content as
    # a substring (astronomically unlikely, but cheap to verify).
    for _ in range(5):
        nonce = make_nonce()
        collision = False
        for _rel, data, _sym, _tgt in entries_data:
            if data is not None and nonce.encode('ascii') in data:
                collision = True
                break
        if not collision:
            break
    else:
        raise RuntimeError("could not find a non-colliding nonce after 5 tries")

    utf8_count = base64_count = symlink_count = 0
    parts = []
    for i, (rel, data, is_sym, tgt) in enumerate(entries_data, 1):
        chunk, kind = encode_entry(rel, data, is_sym, tgt, nonce)
        if kind == 'utf8':
            utf8_count += 1
        elif kind == 'base64':
            base64_count += 1
        else:
            symlink_count += 1
        parts.append(chunk)
        print(f"\rProcessing {i}/{len(entries_data)}: {rel}",
              end='', flush=True, file=sys.stderr)
    if entries_data:
        print('', file=sys.stderr)

    header_lines = [
        f"# {base_name} - AI Archive",
        "",
        f"Format: ai-tar v{FORMAT_VERSION}",
        f"Nonce: {nonce}",
        f"Files: {len(entries_data)} "
        f"(utf8={utf8_count}, base64={base64_count}, symlinks={symlink_count})",
        f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    ]
    if directories and len(directories) > 1:
        header_lines.append(f"Source dirs: {len(directories)}")
        for d in directories:
            try:
                rel_d = d.relative_to(base_path)
            except ValueError:
                rel_d = d
            header_lines.append(f"  - {rel_d}")
    header_lines.extend(["", "---", "", ""])
    header = '\n'.join(header_lines)

    return header + ''.join(parts) + f"<<<END|{nonce}>>>\n"


def main():
    parser = argparse.ArgumentParser(
        description="Create AI-readable archives for web-claude transport (format v2)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    ai-tar project/                             # archive to stdout
    ai-tar project/ -o project.txt              # write archive (.txt recommended)
    ai-tar dir1 dir2 -o combined.txt            # multiple dirs
    ai-tar project/ --include-ext .c .h
    ai-tar project/ --include-ext .py --include-noext
    ai-tar project/ --include-files "README*" "*.txt"
    ai-tar project/ --exclude "*.log" "build/*"

Format v2 supports binary files and SVGs via base64 - the archive itself
is printable ASCII and travels safely through web uploads.
        """
    )
    parser.add_argument('directories', nargs='+')
    parser.add_argument('--include-ext', nargs='*')
    parser.add_argument('--include-noext', action='store_true')
    parser.add_argument('--include-files', nargs='*')
    parser.add_argument('--exclude', nargs='*')
    parser.add_argument('--output', '-o', help='output file path (default: stdout)')
    args = parser.parse_args()

    include_ext = None
    if args.include_ext:
        include_ext = []
        for ext in args.include_ext:
            if not ext.startswith('.'):
                ext = '.' + ext
            include_ext.append(ext.lower())

    directories = [Path(d).resolve() for d in args.directories]
    for d in directories:
        if not d.is_dir():
            print(f"Error: {d} is not a directory", file=sys.stderr)
            sys.exit(1)

    if len(directories) == 1:
        base_path = directories[0]
        base_name = directories[0].name
    else:
        base_path = Path(*directories[0].parts[:1])
        for i in range(1, min(len(d.parts) for d in directories) + 1):
            candidate = Path(*directories[0].parts[:i])
            if all(str(d).startswith(str(candidate)) for d in directories):
                base_path = candidate
            else:
                break
        base_name = f"archive_{len(directories)}_dirs"

    all_files = []
    for d in directories:
        files, _ = collect_files(d, include_ext, args.include_noext,
                                 args.include_files, args.exclude)
        all_files.extend(files)
    all_files = sorted(set(all_files))

    if not all_files:
        print("Error: no files to archive", file=sys.stderr)
        sys.exit(1)

    archive = build_archive(all_files, base_path, base_name, directories)

    if args.output:
        Path(args.output).write_bytes(archive.encode('utf-8'))
        print(f"Archive written: {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(archive)


if __name__ == '__main__':
    main()
