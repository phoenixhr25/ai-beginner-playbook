#!/usr/bin/env python3
"""Check repository-local Markdown links against Git's index, not private local files."""
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

INLINE = re.compile(r'!?\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|((?:\\.|[^\s()\\]|\([^()\n]*\))+))(?:\s+[\"\'][^\n]*?[\"\'])?\s*\)')
DEFINITION = re.compile(r'^ {0,3}\[([^\]]+)\]:\s*(?:<([^>]+)>|(\S+))')
REFERENCE = re.compile(r'!?\[([^\]\n]+)\]\[([^\]\n]*)\]')


def prose_lines(text):
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if marker:
            marks = marker[1]
            if fence is None:
                fence = marks
            elif marks[0] == fence[0] and len(marks) >= len(fence):
                fence = None
            continue
        if fence is None:
            yield number, re.sub(r'(`+).*?\1', '', line)


def validate_links(root, tracked):
    root = Path(root).resolve()
    tracked = set(tracked)
    errors = []
    checked = 0
    for name in sorted(tracked):
        if not name.lower().endswith('.md'):
            continue
        source = root / name
        if not source.is_file():
            errors.append(f'{name}: tracked Markdown file is missing')
            continue
        lines = list(prose_lines(source.read_text(encoding='utf-8')))
        definitions = {}
        for _, line in lines:
            match = DEFINITION.match(line)
            if match:
                definitions[' '.join(match[1].lower().split())] = match[2] or match[3]
        links = []
        for number, line in lines:
            definition = DEFINITION.match(line)
            if definition:
                links.append((number, definition[2] or definition[3]))
                continue
            links.extend((number, m[1] or m[2]) for m in INLINE.finditer(line))
            for match in REFERENCE.finditer(line):
                label = ' '.join((match[2] or match[1]).lower().split())
                if label not in definitions:
                    errors.append(f'{name}:{number}: undefined link reference [{label}]')
        for number, target in links:
            try:
                url = urlsplit(target)
                if url.scheme or url.netloc or not url.path:
                    continue
                path = unquote(url.path, errors='strict')
                candidate = (root / path.lstrip('/') if path.startswith('/') else source.parent / path).resolve()
                relative = candidate.relative_to(root).as_posix()
            except (ValueError, UnicodeError):
                errors.append(f'{name}:{number}: invalid or outside-repository target: {target}')
                continue
            checked += 1
            exists_in_git = relative in tracked or any(x.startswith(relative.rstrip('/') + '/') for x in tracked)
            if not candidate.exists() or not exists_in_git:
                errors.append(f'{name}:{number}: missing or untracked target: {target}')
    return checked, errors


def main():
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(['git', 'ls-files', '-z'], cwd=root, check=True, capture_output=True)
    tracked = result.stdout.decode('utf-8').split('\0')
    checked, errors = validate_links(root, filter(None, tracked))
    if errors:
        print('\n'.join(errors))
        return 1
    print(f'Local links valid: {checked} targets (external URLs and anchors are not fetched)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
