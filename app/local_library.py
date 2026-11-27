"""Read this room's own AI sources (~/.codex or ~/.claude) and persist the local room, schema v1."""

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import stat

from skill_usage import scan_usage


# Keep these patterns aligned with SECRETS in index.html (standalone import).
SECRETS = [
    ('私鑰', r'-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----'),
    ('API 金鑰', r'\b(?:sk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|xox[abprs]-[A-Za-z0-9-]{10,})\b'),
    ('登入權杖', r'\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b'),
    ('密碼／金鑰設定', r'''(?i)\b(password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|client[_-]?secret)(\s*[:=]\s*)(["']?)(?!\[已遮蔽)[^\s"'`]{6,}\3'''),
    ('Email', r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b'),
    ('電話', r'(?<!\d)(?:\+?886[- ]?|0)9\d{2}[- ]?\d{3}[- ]?\d{3}(?!\d)'),
    ('電腦路徑', r'''/(?:Users|home)/[^/\s"'`]+'''),
]
SECRETS = [(label, re.compile(pattern)) for label, pattern in SECRETS]
ZONES = ('support', 'writing', 'tools', 'foundation')
COLLECTIONS = ('skills', 'marks', 'explains')
MARK_FIELDS = ('status', 'hash', 'at', 'star', 'queued', 'readHash', 'readAt')


def redact(text):
    hits = {}
    for label, pattern in SECRETS:
        def substitute(match):
            if label == '電腦路徑':
                return '~'
            if label == '密碼／金鑰設定':
                return f'{match[1]}{match[2]}[已遮蔽]'
            return f'[已遮蔽{label}]'

        text, count = pattern.subn(substitute, text)
        if count:
            hits[label] = count
    return text, hits


def clean_text(value):
    return redact(value)[0] if isinstance(value, str) else ''


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def clean_hash(value):
    return value if isinstance(value, str) and re.fullmatch(r'[a-f0-9]{64}', value) else ''


def encoded(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def guess_zone(name):
    for zone, terms in (
        ('foundation', 'source|backup|attachment|timestamp|AGENTS|skill-creator|skill-installer'),
        ('writing', 'helpcenter|article|supervisor|writ|doc|report'),
        ('tools', 'test|playwright|tool|imagegen|pet|openai-docs|computer|qa|csv|json|statusline|review|script'),
    ):
        if re.search(terms, name):
            return zone
    return 'support'


def body_fields(raw):
    text, hits = redact(raw)
    lines = text.split('\n')
    return {
        'raw': text, 'hits': hits, 'lines': len(lines),
        'headings': [{'line': i, 'title': re.sub(r'^#+\s*', '', line)}
                     for i, line in enumerate(lines, 1) if re.match(r'^#{1,4}\s', line)],
    }


def read_source(path, home):
    relative = path.relative_to(home).as_posix()
    resolved = path.resolve(strict=True)
    if not any(resolved.is_relative_to(home / folder) for folder in AI_FOLDERS):
        raise ValueError('outside')
    if not stat.S_ISREG(resolved.stat().st_mode):
        raise ValueError('來源必須是一般檔案')
    with resolved.open(encoding='utf-8-sig', newline='') as stream:
        raw = stream.read()
        modified = datetime.fromtimestamp(os.fstat(stream.fileno()).st_mtime, timezone.utc).isoformat()
    if not raw.strip():
        return None
    agents = path.name in ('AGENTS.md', 'CLAUDE.md')
    name = path.name if agents else path.parent.name
    front_matter = re.match(r'^---\s*\n([\s\S]*?)\n---', raw)
    description = re.search(r'^description:\s*(.+)$', front_matter[1], re.M) if front_matter else None
    return {
        **body_fields(raw), 'key': 'source-' + digest(relative),
        'path': relative, 'name': name, 'alias': name, 'zone': guess_zone(name),
        'kind': 'AGENTS' if agents else 'Skill',
        'group': '系統' if path.parent.parent.name == '.system' else '個人',
        'manageable': path == resolved and not path.parent.name.startswith('.'),
        'description': clean_text(description[1].strip().strip('"\'')) if description else '',
        'modified': modified, 'hash': digest(raw), 'chinese': None,
    }


AI_FOLDERS = ('.codex', '.claude')


def scan_sources(home, kind='codex'):
    """Each room reads only its own AI's folder: ~/.codex for Codex, ~/.claude for Claude."""
    if kind == 'claude':
        base = home / '.claude'
        paths, roots = [base / 'CLAUDE.md'], (base / 'skills',)
    else:
        base = home / '.codex'
        paths, roots = [base / 'AGENTS.md'], (base / 'skills', base / 'skills' / '.system')
    errors = []
    for root in roots:
        try:
            root.resolve(strict=True).relative_to(base)
            paths.extend(entry / 'SKILL.md' for entry in sorted(root.iterdir())
                         if not entry.name.startswith('.') and entry.is_dir())
        except FileNotFoundError:
            continue
        except (OSError, ValueError, RuntimeError) as error:
            errors.append(f'{root.relative_to(home).as_posix()}：{error_reason(error)}')

    documents = []
    skipped = 0
    for path in paths:
        try:
            document = read_source(path, home)
        except FileNotFoundError:
            continue
        except (OSError, ValueError, RuntimeError) as error:
            errors.append(f'{path.relative_to(home).as_posix()}：{error_reason(error)}')
        else:
            if document:
                documents.append(document)
            else:
                skipped += 1
    return documents, {'found': len(documents), 'blank': skipped, 'errors': errors}


def error_reason(error):
    if isinstance(error, UnicodeError):
        return '檔案不是有效的 UTF-8'
    if isinstance(error, PermissionError):
        return '沒有讀取權限'
    if isinstance(error, ValueError):
        return '來源超出 ~/.codex、~/.claude 或不是一般檔案'
    return '無法讀取來源'


def clean_mark(value):
    result = {}
    for field in MARK_FIELDS:
        item = value.get(field)
        if field == 'status' and item in ('keep', 'revise', 'retire'):
            result[field] = item
        elif field in ('star', 'queued') and isinstance(item, bool):
            result[field] = item
        elif field in ('hash', 'readHash') and clean_hash(item):
            result[field] = item
        elif field in ('at', 'readAt') and isinstance(item, str):
            result[field] = clean_text(item)
    return result


def clean_explanation(value):
    return {'hash': clean_hash(value.get('hash')), 'text': clean_text(value.get('text')),
            'at': clean_text(value.get('at'))}


def clean_guide(value):
    if not isinstance(value, dict):
        return None
    guide = {field: clean_text(value.get(field))
             for field in ('one', 'when', 'summary', 'important', 'caution')}
    guide['source_hash'] = clean_hash(value.get('source_hash'))
    for field in ('importance', 'priority'):
        number = value.get(field)
        guide[field] = min(5, max(1, number)) if isinstance(number, int) else 3
    return guide


def legacy_book(book):
    fields = {field: clean_text(book.get(field)) for field in (
        'name', 'alias', 'path', 'description', 'modified', 'created',
    )}
    fields['name'] = fields['name'] or '舊書房文件'
    fields['alias'] = fields['alias'] or fields['name']
    fields['hash'] = clean_hash(book.get('hash')) or digest(book['raw'])
    fields['zone'] = book['zone'] if book.get('zone') in ZONES else guess_zone(fields['name'])
    fields['kind'] = 'AGENTS' if book.get('kind') == 'AGENTS' else 'Skill'
    fields['group'] = '系統' if book.get('group') == '系統' else '個人'
    fields['chinese'] = clean_guide(book.get('chinese'))
    fields['legacy'] = True
    fields.update(body_fields(book['raw']))
    if isinstance(book.get('hits'), dict):
        for label, _ in SECRETS:
            count = book['hits'].get(label)
            if isinstance(count, int) and label not in fields['hits']:
                fields['hits'][label] = count
    if isinstance(book.get('usage'), dict):
        usage = book['usage']
        chats = usage.get('chats')
        fields['usage'] = {'chats': max(chats, 0) if isinstance(chats, int) else 0,
                           'frequent': bool(usage.get('frequent')), 'last': clean_text(usage.get('last'))}
    return fields


class LocalLibrary:
    def __init__(self, home, kind='codex'):
        self.home = home.resolve()
        self.kind = kind
        self.directory = self.home / '.skill-room'
        # Codex keeps the original file name so existing rooms keep their data.
        self.database = self.directory / ('library-v1.sqlite3' if kind == 'codex' else f'library-{kind}-v1.sqlite3')

    def initialise(self):
        self.directory.mkdir(mode=0o700, exist_ok=True)
        descriptor = os.open(self.database, os.O_CREAT | os.O_WRONLY, 0o600)
        os.close(descriptor)
        with self.connect() as connection:
            connection.execute('CREATE TABLE IF NOT EXISTS room (id INTEGER PRIMARY KEY, revision INTEGER, data TEXT)')
            state = {'skills': {}, 'marks': {}, 'explains': {}, 'scan': None}
            state['first_guides_pending'] = True
            connection.execute('INSERT OR IGNORE INTO room VALUES (1, 0, ?)', (encoded(state),))

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.database)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    @staticmethod
    def snapshot(revision, state):
        return {**state, 'revision': revision, 'skills': list(state['skills'].values())}

    def read(self, known_revision=None):
        with self.connect() as connection:
            revision, data = connection.execute('SELECT revision, data FROM room WHERE id = 1').fetchone()
        return None if str(revision) == known_revision else self.snapshot(revision, json.loads(data))

    def change(self, update):
        with self.connect() as connection:
            connection.execute('BEGIN IMMEDIATE')
            revision, data = connection.execute('SELECT revision, data FROM room WHERE id = 1').fetchone()
            state = json.loads(data)
            result = update(state)
            after = encoded(state)
            if after != data:
                revision += 1
                connection.execute('UPDATE room SET revision = ?, data = ? WHERE id = 1', (revision, after))
        return {'room': self.snapshot(revision, state), 'result': result}

    def claim_first_guides(self, _):
        # Claim inside the database transaction so only one browser starts the batch.
        return self.change(lambda state: state.pop('first_guides_pending', False))

    def refresh(self):
        def update(state):
            documents, scan = scan_sources(self.home, self.kind)
            for book in documents:
                path = self.home / book['path']
                book['manageable'] = book['manageable'] and path.parent.parent == self.home / f'.{self.kind}' / 'skills'
            for book in state['skills'].values():
                book.pop('manageable', None)
            for book in documents:
                old = state['skills'].get(book['key'])
                if old:
                    book.update({field: old[field] for field in ('alias', 'zone', 'chinese', 'usage', 'created')
                                 if field in old})
                state['skills'][book['key']] = book
            state['scan'] = scan

        return self.change(update)

    def usage(self):
        paths = [book['path'] for book in self.read()['skills'] if book.get('manageable')]
        return scan_usage(self.home, self.kind, paths)

    def stage_archive(self, data):
        requested = data.get('books')
        if not isinstance(requested, dict) or not requested:
            raise ValueError('請勾選要封存的 Skill。')

        def update(state):
            for key, source_hash in requested.items():
                book = state['skills'].get(key, {})
                mark = state['marks'].get(key, {})
                if (not book.get('manageable') or book['hash'] != source_hash or mark.get('star')
                        or (mark.get('hash') == source_hash and mark.get('status') == 'keep')):
                    raise ValueError('有 Skill 已更新、移除或標為保留，請重新確認清單。')
            at = datetime.now(timezone.utc).isoformat()
            for key, source_hash in requested.items():
                state['marks'].setdefault(key, {}).update(status='retire', hash=source_hash, at=at)
            return len(requested)

        return self.change(update)

    def save(self, data):
        collection, key, value = (data.get(field) for field in ('collection', 'key', 'value'))
        if collection not in COLLECTIONS or not isinstance(key, str) or not isinstance(value, dict):
            raise ValueError('整理資料格式不正確。')

        def update(state):
            book = state['skills'].get(key)
            if not book:
                raise ValueError('找不到這本書。')
            if collection == 'marks':
                mark = state['marks'].setdefault(key, {})
                for field in MARK_FIELDS:
                    if field in value and value[field] is None:
                        mark.pop(field, None)
                mark.update(clean_mark(value))
            elif collection == 'explains':
                explanation = clean_explanation(value)
                if explanation['hash'] != book['hash']:
                    raise ValueError('原文已更新，請重新產生解釋。')
                state['explains'][key] = explanation
            else:
                guide = clean_guide(value.get('chinese'))
                if not guide or guide['source_hash'] != book['hash']:
                    raise ValueError('原文已更新，請重新產生導讀。')
                book['chinese'] = guide
                book['alias'] = clean_text(value.get('alias')) or book['alias']
                if value.get('zone') in ZONES:
                    book['zone'] = value['zone']

        return self.change(update)

    def migrate(self, data):
        books = data.get('skills')
        marks, explains = data.get('marks', {}), data.get('explains', {})
        if not isinstance(books, list) or not isinstance(marks, dict) or not isinstance(explains, dict):
            raise ValueError('舊書房備份格式不正確。')

        def update(state):
            added = skipped = existing = 0
            for original in books:
                if not isinstance(original, dict) or not isinstance(original.get('key'), str):
                    raise ValueError('舊書房備份有無法辨識的書籍。')
                raw = original.get('raw')
                if not isinstance(raw, str) or not raw.strip():
                    skipped += 1
                    continue
                old_key = original['key']
                book = legacy_book(original)
                mark = marks.get(old_key)
                mark = clean_mark(mark) if isinstance(mark, dict) else {}
                explanation = explains.get(old_key)
                explanation = clean_explanation(explanation) if isinstance(explanation, dict) else {}
                key = 'legacy-' + digest(encoded([book, mark, explanation]))
                if key in state['skills']:
                    existing += 1
                    continue
                book['key'] = key
                state['skills'][key] = book
                if mark:
                    state['marks'][key] = mark
                if explanation:
                    state['explains'][key] = explanation
                added += 1
            return {'added': added, 'skipped': skipped, 'existing': existing}

        return self.change(update)
