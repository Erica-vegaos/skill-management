"""Prepare and apply explicit changes to personal Codex Skills."""

import codecs
from difflib import unified_diff
import os
from pathlib import Path
import re
import secrets
import sqlite3
import stat
import tempfile
import threading
import time

from local_library import digest, redact


MAX_DRAFT_BYTES = 48_000
PREVIEW_SECONDS = 30 * 60
FRONT_MATTER = re.compile(r'\A---\s*\r?\n(.*?)\r?\n---(?=\r?\n|\Z)', re.S)
SKILL_NAME = re.compile(r'^name:[ \t]*(.*)$', re.M)


def plain_directory(path, create=False):
    if not path.exists() and not path.is_symlink() and create:
        try:
            path.mkdir(mode=0o700)
        except FileExistsError:
            pass
    if path.resolve() != path or not path.is_dir():
        raise ValueError(f'無法使用資料夾 {path.name}。')
    return path


def source_snapshot(path, max_bytes=None):
    plain_directory(path.parent)
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError('SKILL.md 必須是一般檔案。')
    if max_bytes is not None and info.st_size > max_bytes:
        raise ValueError('原文超過自動草擬可處理的大小，可使用複製指令。')
    with path.open('rb') as stream:
        opened = os.fstat(stream.fileno())
        if (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
            raise ValueError('原檔已更換，請重新預覽。')
        data = stream.read() if max_bytes is None else stream.read(max_bytes + 1)
    if max_bytes is not None and len(data) > max_bytes:
        raise ValueError('原文超過自動草擬可處理的大小，可使用複製指令。')
    return data, stat.S_IMODE(info.st_mode)


def replacement(original, draft):
    if not isinstance(draft, str) or not draft.strip() or '\0' in draft:
        raise ValueError('Codex 未回傳可用的修改草稿。')
    before = original.decode('utf-8-sig')
    front = FRONT_MATTER.match(before)
    if front:
        new_front = FRONT_MATTER.match(draft)
        name = SKILL_NAME.search(front[1])
        new_name = SKILL_NAME.search(new_front[1]) if new_front else None
        if not new_front or (name and (not new_name or name[1].strip() != new_name[1].strip())):
            raise ValueError('草稿變更了 Skill 的名稱或移除了前置資料，可使用複製指令。')
    draft = draft.replace('\r\n', '\n').rstrip('\n') + '\n'
    if '\r\n' in before and '\n' not in before.replace('\r\n', ''):
        draft = draft.replace('\n', '\r\n')
    delta = '\n'.join(unified_diff(before.splitlines(), draft.splitlines(), '原檔', '草稿', lineterm=''))
    if not delta:
        raise ValueError('草稿沒有內容變更。')
    data = draft.encode('utf-8')
    if len(data) > MAX_DRAFT_BYTES:
        raise ValueError('草稿超過可套用的大小。')
    if original.startswith(codecs.BOM_UTF8):
        data = codecs.BOM_UTF8 + data
    return data, delta


def write_replacement(path, original, data, mode):
    with tempfile.NamedTemporaryFile(prefix='.skill-room-', dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
            stream.close()
            temporary.chmod(mode)
            if source_snapshot(path, MAX_DRAFT_BYTES)[0] != original:
                raise ValueError('備份後原文已變更，請重新預覽。')
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)


class SkillEffects:
    def __init__(self, library):
        self.library = library
        self.root = library.home / '.codex'
        self.previews = {}
        self.lock = threading.Lock()

    def resolve(self, book):
        path = Path(book['path'])
        parts = path.parts
        if len(parts) != 4 or parts[:2] != ('.codex', 'skills') or parts[2].startswith('.') or parts[3] != 'SKILL.md':
            raise ValueError('只能套用本機 Codex 的個人 Skill。')
        plain_directory(self.root / 'skills')
        folder = plain_directory(self.library.home / path.parent)
        return folder / 'SKILL.md'

    def marked(self, keys):
        room = self.library.read()
        books = {book['key']: book for book in room['skills'] if book.get('manageable')}
        for key in keys:
            book, mark = books.get(key), room['marks'].get(key, {})
            valid = bool(book and book['hash'] == mark.get('hash') and mark.get('status') in ('retire', 'revise'))
            yield key, book if valid else None, mark.get('status')

    def archive_target(self, path):
        archive = self.root / 'skills-archive'
        if archive.exists() or archive.is_symlink():
            plain_directory(archive)
        target = archive / path.parent.name
        if target.exists() or target.is_symlink():
            raise ValueError('封存資料夾內已有同名項目。')
        return target

    def preview(self, payload, draft_skill):
        keys = payload.get('keys')
        if not isinstance(keys, list) or not keys or any(not isinstance(key, str) for key in keys):
            raise ValueError('請選擇要套用的 Skill。')
        items, ready = [], {}
        for key, book, action in self.marked(dict.fromkeys(keys)):
            if not book:
                items.append({'key': key, 'error': 'Skill 已移除或整理標記已變更。'})
                continue
            item = {'key': key, 'path': book['path'], 'action': action}
            try:
                path = self.resolve(book)
                original, _ = source_snapshot(path, MAX_DRAFT_BYTES if action == 'revise' else None)
                source = original.decode('utf-8-sig')
                if digest(source) != book['hash']:
                    raise ValueError('原文已更新，請重新掃描。')
                if action == 'retire':
                    item['target'] = self.archive_target(path).relative_to(self.library.home).as_posix()
                    revised = None
                else:
                    if not draft_skill:
                        raise ValueError('找不到本機 Codex，可使用複製指令。')
                    if redact(source)[1]:
                        raise ValueError('原文含需遮蔽的資訊，可使用複製指令。')
                    revised, item['diff'] = replacement(original, draft_skill(source))
                ready[key] = (book['hash'], action, revised, book['path'])
            except (OSError, ValueError, RuntimeError) as error:
                item['error'] = '無法讀取原檔。' if isinstance(error, OSError) else str(error)
            items.append(item)
        token = None
        if ready:
            token = secrets.token_urlsafe(24)
            now = time.monotonic()
            with self.lock:
                self.previews = {k: v for k, v in self.previews.items() if v[0] > now}
                self.previews[token] = (now + PREVIEW_SECONDS, ready)
        return {'result': {'token': token, 'items': items}}

    def apply(self, payload):
        token, keys = payload.get('token'), payload.get('keys')
        if not isinstance(token, str) or not isinstance(keys, list) or not keys or any(not isinstance(key, str) for key in keys):
            raise ValueError('請確認要套用的 Skill。')
        with self.lock:
            expiry, plan = self.previews.get(token, (0, {}))
            if expiry <= time.monotonic() or any(key not in plan for key in keys):
                raise ValueError('預覽已失效，請重新開始。')
            del self.previews[token]
            results = [self.apply_one(key, book, action, plan[key]) for key, book, action in self.marked(dict.fromkeys(keys))]
        try:
            result = self.library.refresh()
        except (OSError, sqlite3.Error):
            result = {'room': None, 'warning': '已執行檔案操作，請手動重新掃描。'}
        result['result'] = {'items': results, 'warning': result.get('warning')}
        return result

    def apply_one(self, key, book, action, planned):
        expected, expected_action, revised, path_label = planned
        item = {'key': key, 'path': path_label, 'action': expected_action}
        try:
            if not book or book['hash'] != expected or action != expected_action:
                raise ValueError('整理標記或原文已變更，請重新預覽。')
            path = self.resolve(book)
            original, mode = source_snapshot(path, MAX_DRAFT_BYTES if action == 'revise' else None)
            if digest(original.decode('utf-8-sig')) != expected:
                raise ValueError('原文於預覽後已更新，請重新掃描。')
            target = self.archive_target(path) if action == 'retire' else None
            plain_directory(self.library.directory)
            backup_root = plain_directory(self.library.directory / 'skill-backups', create=True)
            backup = Path(tempfile.mkdtemp(prefix=path.parent.name[:40] + '-', dir=backup_root)) / 'SKILL.md'
            with backup.open('xb') as stream:
                stream.write(original)
                stream.flush()
                os.fsync(stream.fileno())
            item['backup'] = backup.relative_to(self.library.home).as_posix()
            if target:
                plain_directory(target.parent, create=True)
                target = self.archive_target(path)
                if source_snapshot(self.resolve(book))[0] != original:
                    raise ValueError('備份後原文已變更，請重新預覽。')
                path.parent.rename(target)
                item['target'] = target.relative_to(self.library.home).as_posix()
            else:
                write_replacement(self.resolve(book), original, revised, mode)
        except (OSError, ValueError, RuntimeError) as error:
            item['error'] = '檔案操作失敗，請確認權限及磁碟空間。' if isinstance(error, OSError) else str(error)
        return item
