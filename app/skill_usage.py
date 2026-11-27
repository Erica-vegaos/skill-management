"""Collect observable Skill file reads from local AI session logs."""

from datetime import datetime
import json
from pathlib import Path
import re
import shlex


READ_COMMANDS = {'cat', 'head', 'tail', 'sed', 'nl'}
MAX_BYTES = 128 * 1024 * 1024
EXIT_OK = re.compile(r'(?m)^(?:Process exited with code 0\b|Exit code:\s*0\b)')


def codex_paths(payload, wanted):
    if payload.get('name', '').rsplit('.', 1)[-1] != 'exec_command':
        return set()
    try:
        arguments = json.loads(payload.get('arguments', ''))
        lexer = shlex.shlex(arguments['cmd'], posix=True, punctuation_chars=';&|<>')
        lexer.whitespace_split = True
        tokens = list(lexer)
    except (ValueError, TypeError, KeyError, AttributeError):
        return set()
    paths, reading = set(), False
    for i, token in enumerate(tokens):
        if i == 0 or tokens[i - 1] in (';', '&&', '||', '|'):
            reading = Path(token).name in READ_COMMANDS
        elif token.startswith(('>', '<')):
            reading = False
        elif reading and token in wanted:
            paths.add(wanted[token])
    return paths


def recorded_reads(record, kind, wanted, pending):
    payload = record.get('payload')
    if kind == 'codex' and record.get('type') == 'response_item' and isinstance(payload, dict):
        call = payload.get('call_id')
        if payload.get('type') == 'function_call':
            paths = codex_paths(payload, wanted)
            if call and paths:
                pending[call] = paths
        elif payload.get('type') == 'function_call_output':
            paths = pending.pop(call, ())
            output = payload.get('output')
            if paths and isinstance(output, str) and EXIT_OK.search(output):
                yield from paths
    elif kind == 'claude':
        message = record.get('message')
        content = message.get('content') if isinstance(message, dict) else None
        if not isinstance(content, list):
            return
        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get('type') == 'tool_use' and item.get('name') == 'Read':
                args = item.get('input')
                path = args.get('file_path') if isinstance(args, dict) else None
                if isinstance(path, str) and path in wanted and item.get('id'):
                    pending[item['id']] = {wanted[path]}
            elif item.get('type') == 'tool_result':
                paths = pending.pop(item.get('tool_use_id'), ())
                if not item.get('is_error'):
                    yield from paths


def scan_usage(home, kind, paths):
    base = home / ('.codex' if kind == 'codex' else '.claude')
    roots = ('sessions', 'archived_sessions') if kind == 'codex' else ('projects',)
    pattern = 'rollout-*.jsonl' if kind == 'codex' else '*.jsonl'
    wanted = {spelling: path for path in paths for spelling in (str(home / path), '~/' + path)}
    latest, candidates = {}, []
    for name in roots:
        root = base / name
        try:
            if root.resolve() != root:
                continue
            for file in root.rglob(pattern):
                if file.resolve() == file and file.is_file():
                    info = file.stat()
                    candidates.append((info.st_mtime, info.st_size, file))
        except (OSError, RuntimeError):
            continue
    scanned, remaining, partial = 0, MAX_BYTES, False
    for _, size, file in sorted(candidates, reverse=True):
        if size > remaining:
            partial = True
            continue
        remaining -= size
        try:
            with file.open('rb') as stream:
                pending, valid = {}, False
                for line in stream:
                    try:
                        record = json.loads(line)
                        stamp = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                        if stamp.tzinfo is None:
                            continue
                        for path in recorded_reads(record, kind, wanted, pending):
                            if path not in latest or stamp > latest[path]:
                                latest[path] = stamp
                        valid = True
                    except (AttributeError, KeyError, TypeError, ValueError, OverflowError):
                        continue
                scanned += valid
        except OSError:
            partial = True
    return {'files': scanned, 'partial': partial, 'last': {path: stamp.isoformat() for path, stamp in latest.items()}}
