#!/usr/bin/env python3
"""One-time shared toolkit installation (Python 3.11+, no packages)."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parent
BEGIN = '<!-- dotfiles-embedded:begin -->'
END = '<!-- dotfiles-embedded:end -->'
sys.path.insert(0, str(ROOT/'scripts'))
from permissions import codex_memory, claude_memory


def linked(path):
    return path.is_symlink() or (os.name == 'nt' and path.exists() and bool(path.lstat().st_file_attributes & 0x400))


def same(path, target):
    return path.exists() and os.path.samefile(path, target)


def directory_link(path, target):
    if os.name != 'nt':
        path.symlink_to(target, target_is_directory=True)
    else:
        # Fixed PowerShell code; paths are data in environment variables, not code.
        env = dict(os.environ, TOOLKIT_LINK=str(path), TOOLKIT_TARGET=str(target))
        subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command',
                        'New-Item -ItemType Junction -Path $env:TOOLKIT_LINK -Target $env:TOOLKIT_TARGET | Out-Null'],
                       env=env, check=True, capture_output=True, text=True)
    if not same(path, target):
        raise OSError(f'Link did not resolve to canonical directory: {path}')


def remove_link(path):
    if path.is_symlink():
        path.unlink()
    else:
        os.rmdir(path)  # Windows junction: remove only the junction, never its target.


def merge_block(old, body):
    block = f'{BEGIN}\n{body}\n{END}'
    if BEGIN not in old and END not in old:
        return old.rstrip('\n') + '\n\n' + block + '\n'
    if old.count(BEGIN) != 1 or old.count(END) != 1 or old.index(BEGIN) > old.index(END):
        raise ValueError('Malformed toolkit block in existing instructions')
    return old[:old.index(BEGIN)] + block + old[old.index(END)+len(END):]


def layout(home, project=None):
    if project:
        p = Path(project).expanduser().resolve()
        if not p.is_dir():
            raise ValueError('Project must be an existing directory')
        return [p/'.claude/skills', p/'.agents/skills'], [p/'CLAUDE.md', p/'AGENTS.md'], p/'.engineering-toolkit.json'
    c = Path(os.environ.get('CLAUDE_CONFIG_DIR', str(home/'.claude'))).expanduser().absolute()
    x = Path(os.environ.get('CODEX_HOME', str(home/'.codex'))).expanduser().absolute()
    return [c/'skills', home/'.agents/skills'], [c/'CLAUDE.md', x/'AGENTS.md'], home/'.engineering-toolkit.json'


def install(home, project=None, memory=None, migrate=False, dry_run=False, root=ROOT):
    home = Path(home).expanduser().resolve()
    root = Path(root).resolve()
    links, instructions, config = layout(home, project)
    skills = root/'skills'
    if not skills.is_dir() or not (skills/'using-superpowers/SKILL.md').is_file():
        raise ValueError('Incomplete toolkit checkout')
    memory = Path(memory).expanduser().resolve() if memory else root/'experience'
    body = (f'Engineering toolkit: `{root.as_posix()}`.\n'
            f'At the start of engineering tasks, read `{root.as_posix()}/policies/ENGINEERING.md` '
            f'and `{root.as_posix()}/policies/MEMORY.md`, then load `using-superpowers`.\n'
            f'Use the same canonical skills `{skills.as_posix()}`, scripts `{root.as_posix()}/scripts`, '
            f'and shared experience directory `{memory.as_posix()}` in both clients.\n'
            'Choose relevant skills automatically. No per-session activation or agent switching.\n'
            'Work only in the user-assigned scope; a project workflow takes precedence.\n'
            'Keep the main context small: delegate bulky work per `delegating-work`.\n'
            'Before work recall relevant experience; before finishing record useful outcomes and evidence.\n')
    writes, backups, new_links = {}, {}, []
    settings = [(links[0].parent/'settings.json', claude_memory),
                ((Path(project).resolve()/'.codex/config.toml') if project else instructions[1].parent/'config.toml', codex_memory)]
    # Preflight everything before mutation, preserving unrelated configuration.
    for link in links:
        if same(link, skills):
            continue
        if link.exists() or link.is_symlink():
            if not migrate:
                raise ValueError(f'Existing skills at {link}; --migrate archives them before linking')
        for parent in link.parents:
            if linked(parent):
                raise ValueError(f'Resolve linked configuration parent before installing: {parent}')
        new_links.append(link)
    for p in instructions + [config] + [item[0] for item in settings]:
        if p.is_symlink() or (p.exists() and not p.is_file()):
            raise ValueError(f'Refusing non-regular configuration file: {p}')
        for parent in p.parents:
            if linked(parent):
                raise ValueError(f'Resolve linked configuration parent: {parent}')
    for p in instructions:
        old = p.read_text(encoding='utf-8') if p.exists() else ''
        # Recognize the original citypaul global policy; retain it as a backup,
        # but do not run it together with the new policy.
        legacy = 'TypeScript strict mode always' in old and 'TDD non-negotiable' in old
        if legacy and not migrate:
            raise ValueError(f'Legacy TypeScript policy at {p}; use --migrate to archive it')
        if legacy:
            backups[p] = p.with_name(p.name + '.before-embedded-' + uuid.uuid4().hex[:8])
            old = ''
        value = merge_block(old, body).encode()
        if not p.exists() or value != p.read_bytes():
            writes[p] = value
    for p, updater in settings:
        old = p.read_text(encoding='utf-8') if p.exists() else ''
        value = updater(old, str(memory)).encode('utf-8')
        if not p.exists() or value != p.read_bytes():
            writes[p] = value
            if p.exists():
                backups[p] = p.with_name(p.name + '.before-embedded-' + uuid.uuid4().hex[:8])
    manifest = dict(version=2, toolkit=str(root), memory=str(memory), links=[str(p) for p in links])
    encoded = (json.dumps(manifest, indent=2) + '\n').encode()
    if not config.exists() or config.read_bytes() != encoded:
        writes[config] = encoded
    for link in new_links:
        if link.exists() or link.is_symlink():
            backups[link] = link.with_name(link.name + '.before-embedded-' + uuid.uuid4().hex[:8])
    actions = {'links': [str(p) for p in new_links], 'writes': [str(p) for p in writes],
               'backups': {str(p):str(q) for p,q in backups.items()}, 'memory': str(memory)}
    if dry_run:
        return actions
    before = {p: p.read_bytes() if p.exists() else None for p in writes}
    moved, made, written = [], [], []
    try:
        memory.mkdir(parents=True, exist_ok=True)
        for p,q in backups.items():
            p.rename(q); moved.append((p,q))
        for link in new_links:
            link.parent.mkdir(parents=True, exist_ok=True)
            directory_link(link, skills); made.append(link)
        for p,data in writes.items():
            p.parent.mkdir(parents=True, exist_ok=True)
            written.append(p); p.write_bytes(data)
    except (OSError, subprocess.SubprocessError):
        for p in reversed(written):
            if before[p] is None: p.unlink(missing_ok=True)
            else: p.write_bytes(before[p])
        for p in reversed(made): remove_link(p)
        for p,q in reversed(moved):
            if p.exists() and p.is_file(): p.unlink()
            q.rename(p)
        raise
    return actions


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', help='optional project-scoped install; default is user-wide')
    p.add_argument('--home', type=Path, default=Path.home(), help='alternate OS home for testing')
    p.add_argument('--memory', help='shared local experience directory; default CHECKOUT/experience')
    p.add_argument('--migrate', action='store_true', help='archive conflicting skill directories/known legacy policy')
    p.add_argument('--dry-run', action='store_true')
    a=p.parse_args()
    try: print(json.dumps(install(a.home,a.project,a.memory,a.migrate,a.dry_run), indent=2))
    except (OSError, ValueError, subprocess.SubprocessError) as e: p.exit(1,str(e)+'\n')
if __name__=='__main__': main()
