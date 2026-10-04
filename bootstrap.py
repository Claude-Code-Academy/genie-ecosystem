#!/usr/bin/env python3
"""Public, resumable bootstrap. No private source, credential values or lifecycle logic."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import uuid
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
ALLOWED_DOWNLOAD_HOSTS = {'github.com', 'raw.githubusercontent.com', 'claude.ai',
                          'chatgpt.com', 'hermes-agent.nousresearch.com'}

class Pending(ValueError):
    """User action or unreleased metadata is needed; retry the same invocation."""


def load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('Expected JSON object')
    return data


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temporary.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, target: Path, expected: str | None) -> str:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.hostname not in ALLOWED_DOWNLOAD_HOSTS or parsed.username:
        raise ValueError('Untrusted download origin')
    if expected is not None and not re.fullmatch('[0-9a-f]{64}', expected):
        raise ValueError('Invalid artifact digest')
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + '.' + uuid.uuid4().hex + '.part')
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'Genie-bootstrap'})
        with urllib.request.urlopen(request, timeout=60) as response, temporary.open('xb') as stream:
            final_url = getattr(response, 'url', url)
            if urlparse(final_url).scheme != 'https':
                raise ValueError('Download redirected to insecure transport')
            total = 0
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > 1024 ** 3:
                    raise ValueError('Artifact exceeds 1 GiB download limit')
                stream.write(chunk)
        digest = sha256(temporary)
        if expected is not None and digest != expected:
            raise ValueError('Artifact checksum mismatch')
        temporary.replace(target)
        return digest
    finally:
        temporary.unlink(missing_ok=True)


def safe_extract(archive: Path, destination: Path) -> None:
    """Reject path traversal, device nodes and external archive links before writing."""
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    def validate(name: str):
        relative = PurePosixPath(name.replace('\\', '/'))
        if relative.is_absolute() or '..' in relative.parts or ':' in name:
            raise ValueError('Unsafe archive path')
        path = (destination / str(relative)).resolve()
        if path != root and root not in path.parents:
            raise ValueError('Archive escapes destination')
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as bundle:
            for entry in bundle.infolist():
                validate(entry.filename)
                if (entry.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError('ZIP symlinks are unsupported')
            bundle.extractall(destination)
    else:
        with tarfile.open(archive, 'r:*') as bundle:
            entries = bundle.getmembers()
            for entry in entries:
                validate(entry.name)
                if not (entry.isfile() or entry.isdir() or entry.issym() or entry.islnk()):
                    raise ValueError('Unsafe archive member type')
                if entry.issym():
                    validate(str(PurePosixPath(entry.name).parent / entry.linkname))
                if entry.islnk():
                    validate(entry.linkname)
            # Validate all potential parent symlink traversals independent of member order.
            links = {PurePosixPath(e.name): e.linkname for e in entries if e.issym()}
            for entry in entries:
                for parent in PurePosixPath(entry.name).parents:
                    if parent in links:
                        raise ValueError('Archive member traverses symlink')
            bundle.extractall(destination, members=entries)


def run(command: list[str], *, interactive: bool = False, timeout: int = 120):
    # Never print arbitrary native output: auth tools may include account/credential data.
    try:
        return subprocess.run(command, check=False, text=True,
                              capture_output=not interactive,
                              timeout=None if interactive else timeout)
    except subprocess.TimeoutExpired as exc:
        raise Pending('Command timed out; retry setup') from exc


def platform_key() -> str:
    system, machine = platform.system(), platform.machine().lower()
    if system == 'Darwin' and machine in ('arm64', 'aarch64'):
        return 'macos-arm64'
    if system == 'Windows' and machine in ('amd64', 'x86_64'):
        return 'windows-x64'
    raise Pending('Bootstrap provisioning is not qualified for this OS/architecture')


def find_executable(name: str, user_home: Path, managed: Path) -> Path | None:
    found = shutil.which(name)
    candidates = [Path(found)] if found else []
    suffix = '.exe' if os.name == 'nt' else ''
    candidates += [user_home / '.local' / 'bin' / (name + suffix),
                   user_home / '.cargo' / 'bin' / (name + suffix),
                   managed / 'bin' / (name + suffix)]
    if name == 'hermes' and os.name == 'nt':
        candidates += [Path(os.environ.get('LOCALAPPDATA', user_home / 'AppData' / 'Local')) / 'hermes' / 'bin' / 'hermes.cmd']
    return next((p.resolve() for p in candidates if p.is_file()), None)


def ensure_gh(home: Path, registry: dict, key: str, user_home: Path) -> Path:
    executable = find_executable('gh', user_home, home / 'bootstrap')
    if executable and run([str(executable), '--version']).returncode == 0:
        return executable
    spec = registry['platforms'][key]['gh']
    base = home / 'bootstrap' / 'tools' / ('gh-' + spec['version'])
    executable = base / spec['executable']
    if executable.is_file() and run([str(executable), '--version']).returncode == 0:
        return executable.resolve()
    with tempfile.TemporaryDirectory(dir=home / 'bootstrap') as directory:
        directory = Path(directory)
        archive = directory / 'gh.zip'
        download(spec['url'], archive, spec['sha256'])
        safe_extract(archive, directory / 'stage')
        if base.exists():
            raise Pending('Incomplete managed gh directory; preserve it and retry with a new home or repair')
        shutil.move(str(directory / 'stage'), base)
    executable.chmod(executable.stat().st_mode | 0o100)
    if run([str(executable), '--version']).returncode:
        raise Pending('Managed GitHub CLI did not start')
    return executable.resolve()


def authenticate(gh: Path, repo: str, non_interactive: bool) -> None:
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
        raise ValueError('Invalid repository identity')
    if run([str(gh), 'auth', 'status', '--hostname', 'github.com']).returncode:
        if non_interactive:
            raise Pending('GitHub login required: run gh auth login, then rerun setup')
        print('GitHub will guide sign-in. Organization SSO approval may be required.')
        if run([str(gh), 'auth', 'login', '--hostname', 'github.com', '--web'], interactive=True).returncode:
            raise Pending('GitHub login unfinished; rerun setup to resume')
    if run([str(gh), 'api', 'repos/' + repo, '--silent']).returncode:
        raise Pending('Authenticated but private repository access is missing; check membership and organization SSO')


def core_inventory(root: Path) -> dict:
    result = {}
    for path in root.rglob('*'):
        if path.is_symlink():
            raise ValueError('Core cache symlinks are forbidden')
        if path.is_file() and path.name != '.genie-envelope.json':
            result[path.relative_to(root).as_posix()] = sha256(path)
    return result


def core_archive_inventory(archive: Path) -> dict:
    result, seen = {}, set()
    reserved = {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1,10)), *(f'LPT{i}' for i in range(1,10))}
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        if len(entries) > 100000 or sum(e.file_size for e in entries) > 2 * 1024 ** 3:
            raise ValueError('Core envelope exceeds extraction limits')
        for entry in entries:
            name = entry.filename.replace('\\', '/')
            path = PurePosixPath(name)
            folded = name.rstrip('/').casefold()
            if path.is_absolute() or '..' in path.parts or ':' in name or folded in seen:
                raise ValueError('Unsafe or case-colliding Core archive path')
            seen.add(folded)
            if any(part.rstrip(' .') != part or part.split('.')[0].upper() in reserved for part in path.parts):
                raise ValueError('Reserved Windows Core path')
            if (entry.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError('Core archive symlinks are forbidden')
            if any((part.startswith('.env') and part != '.env.example') or part.lower() in {'auth.json', 'credentials.json', '.credentials.json', '.npmrc', '.pypirc', 'id_rsa', 'id_ed25519'} or part.lower().endswith(('.pem','.key','.p12','.pfx')) for part in path.parts):
                raise ValueError('Private credential artifact in Core archive')
            if name.rstrip('/') == '.genie-envelope.json':
                raise ValueError('Publisher may not define a local verification marker')
            if not entry.is_dir():
                digest = hashlib.sha256()
                with bundle.open(entry) as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b''): digest.update(chunk)
                result[path.as_posix()] = digest.hexdigest()
    return result


def validate_core_cache(root: Path, expected: str) -> None:
    proof = root.parent.parent / 'core-artifacts' / (expected + '.zip')
    if not proof.is_file() or proof.is_symlink() or sha256(proof) != expected:
        raise ValueError('Core proof archive is missing or modified; preserve cache and repair')
    if core_archive_inventory(proof) != core_inventory(root):
        raise ValueError('Cached Core engine was modified; preserve it and repair')


def enable_command_path(home: Path, user_home: Path, key: str) -> dict:
    bindir = str(home / 'bin')
    if key.startswith('windows'):
        if user_home != Path.home().resolve():
            return {'status': 'pending-native-user-PATH', 'directory': bindir}
        import winreg
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_READ | winreg.KEY_WRITE) as registry:
            try: previous, kind = winreg.QueryValueEx(registry, 'Path')
            except FileNotFoundError: previous, kind = '', winreg.REG_EXPAND_SZ
            values = previous.split(';')
            if bindir.casefold() not in {item.casefold() for item in values}:
                write_json(home / 'bootstrap' / 'path-backup.json', {'previous': previous})
                winreg.SetValueEx(registry, 'Path', 0, kind, ';'.join([bindir, *values]))
        # Broadcast user environment change; already running terminals still need reopening.
        import ctypes
        from ctypes import wintypes
        broadcast = ctypes.windll.user32.SendMessageTimeoutW
        broadcast.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPCWSTR, wintypes.UINT, wintypes.UINT, ctypes.POINTER(ctypes.c_size_t)]
        broadcast.restype = ctypes.c_ssize_t
        result = ctypes.c_size_t()
        broadcast(0xffff, 0x001a, 0, 'Environment', 2, 5000, ctypes.byref(result))
        return {'status': 'user-PATH-enabled', 'restart_terminal': True}
    shell = Path(os.environ.get('SHELL', '/bin/zsh')).name
    if shell not in ('zsh', 'bash'):
        return {'status': 'pending-shell-specific-PATH', 'shell': shell, 'directory': bindir}
    profile = user_home / ('.zprofile' if shell == 'zsh' else '.bash_profile')
    if profile.is_symlink():
        raise ValueError('Shell profile is a symlink; retained, use the absolute Genie launcher')
    start, end = '# >>> Genie managed PATH >>>', '# <<< Genie managed PATH <<<'
    previous = profile.read_text(encoding='utf-8') if profile.exists() else ''
    block = start + '\nexport PATH=' + __import__('shlex').quote(bindir) + ':"$PATH"\n' + end
    if previous.count(start) != previous.count(end) or previous.count(start) > 1:
        raise ValueError('Ambiguous Genie PATH marker; profile retained')
    state = home / 'bootstrap' / 'path-receipt.json'
    receipt = load_json(state) if state.exists() else {}
    if start in previous:
        begin, finish = previous.index(start), previous.index(end) + len(end)
        existing = previous[begin:finish]
        if receipt.get('block_sha256') != hashlib.sha256(existing.encode()).hexdigest():
            raise ValueError('User-modified Genie PATH block retained; use absolute launcher')
        content = previous[:begin] + block + previous[finish:]
    else:
        content = previous + ('\n' if previous and not previous.endswith('\n') else '') + block + '\n'
    profile.parent.mkdir(parents=True, exist_ok=True)
    if content != previous:
        backup = home / 'backups' / ('shell-profile-' + uuid.uuid4().hex + '.txt')
        backup.parent.mkdir(parents=True, exist_ok=True); backup.write_text(previous, encoding='utf-8')
        temporary = profile.with_name(profile.name + '.genie-' + uuid.uuid4().hex)
        try:
            temporary.write_text(content, encoding='utf-8')
            temporary.chmod(profile.stat().st_mode & 0o777 if profile.exists() else 0o600)
            temporary.replace(profile)
        finally: temporary.unlink(missing_ok=True)
    write_json(state, {'path': str(profile), 'block_sha256': hashlib.sha256(block.encode()).hexdigest()})
    return {'status': 'user-shell-PATH-enabled', 'path': str(profile), 'restart_terminal': True}

def materialize_core(home: Path, *, source: Path | None, release: dict, gh: Path | None) -> Path:
    """Copy development code or retrieve a published, digest-pinned release artifact."""
    if source is not None:
        source = source.resolve()
        entry = source / 'genie_cli.py'
        if not entry.is_file() or not (source / 'src' / 'genie').is_dir():
            raise ValueError('--core-source must contain genie_cli.py and src/genie')
        selected = [entry, *sorted((source / 'src' / 'genie').rglob('*.py'))]
        for name in ('genie-package.json', 'LICENSE'):
            path = source / name
            if path.is_file():
                selected.append(path)
        portable = source / 'portable'
        if portable.is_dir():
            selected += sorted(p for p in portable.rglob('*') if p.is_file())
        for path in selected:
            if path.name.startswith('.env') and path.name != '.env.example':
                raise ValueError('Private data cannot travel in development Core')
        digest = hashlib.sha256()
        for path in selected:
            if path.is_symlink():
                raise ValueError('Development source symlinks are unsupported')
            digest.update(path.relative_to(source).as_posix().encode())
            digest.update(path.read_bytes())
        destination = home / 'bootstrap' / 'core' / ('dev-' + digest.hexdigest())
        if not destination.exists():
            with tempfile.TemporaryDirectory(dir=home / 'bootstrap') as temporary:
                stage = Path(temporary) / 'stage'; stage.mkdir()
                for path in selected:
                    target = stage / path.relative_to(source)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, target)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(stage), destination)
        for path in selected:
            target = destination / path.relative_to(source)
            if not target.is_file() or target.is_symlink() or sha256(target) != sha256(path):
                raise Pending('Managed development Core changed; preserve it and repair before retry')
        return destination
    core = release.get('core')
    if not core:
        raise Pending('Portable Core is not published: no approved release pin. Use --core-source only for development.')
    if gh is None:
        raise ValueError('GitHub CLI required for published core')
    for field in ('repo', 'tag', 'asset', 'sha256', 'source_revision'):
        if not isinstance(core.get(field), str) or not core[field]:
            raise ValueError('Incomplete core release metadata')
    if not re.fullmatch('[0-9a-f]{40}', core['source_revision']) or not re.fullmatch('[0-9a-f]{64}', core['sha256']):
        raise ValueError('Invalid core release pins')
    if core['tag'].startswith('-') or not re.fullmatch(r'[\w.-]+/[\w.-]+', core['repo']):
        raise ValueError('Unsafe core release identity')
    if '/' in core['asset'] or '\\' in core['asset'] or core['asset'].startswith('-'):
        raise ValueError('Unsafe core release asset name')
    destination = home / 'bootstrap' / 'core' / core['sha256']
    if destination.is_dir():
        validate_core_cache(destination, core['sha256'])
        return destination
    with tempfile.TemporaryDirectory(dir=home / 'bootstrap') as temporary:
        temporary = Path(temporary)
        result = run([str(gh), 'release', 'download', core['tag'], '--repo', core['repo'],
                      '--pattern', core['asset'], '--dir', str(temporary)])
        if result.returncode:
            raise Pending('Core release download failed; login or release access may need attention')
        archive = temporary / core['asset']
        if sha256(archive) != core['sha256']:
            raise ValueError('Core archive checksum mismatch')
        authoritative = core_archive_inventory(archive)
        stage = temporary / 'stage'
        safe_extract(archive, stage)
        if core_inventory(stage) != authoritative:
            raise ValueError('Extracted Core inventory differs from verified artifact')
        if not (stage / 'genie_cli.py').is_file() or not (stage / 'src' / 'genie').is_dir():
            raise ValueError('Core release layout missing portable entrypoint')
        proofs = home / 'bootstrap' / 'core-artifacts'; proofs.mkdir(parents=True, exist_ok=True)
        proof = proofs / (core['sha256'] + '.zip')
        if proof.exists() and sha256(proof) != core['sha256']:
            raise ValueError('Existing Core proof archive was modified')
        if not proof.exists(): shutil.copy2(archive, proof)
        write_json(stage / '.genie-envelope.json', {'schema_version': 1, 'sha256': core['sha256'], 'files': authoritative})
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(stage), destination)
    return destination


def provision_client(name: str, home: Path, user_home: Path, registry: dict,
                     key: str, non_interactive: bool) -> dict:
    executable = find_executable(name, user_home, home / 'bootstrap')
    if executable and run([str(executable), '--version']).returncode == 0:
        return {'name': name, 'executable': str(executable), 'installation': 'existing',
                'authentication': 'unverified', 'desktop': 'unverified'}
    spec = registry['clients'][name][key]
    downloads = home / 'bootstrap' / 'downloads'; downloads.mkdir(parents=True, exist_ok=True)
    path = downloads / spec['filename']
    digest = download(spec['url'], path, spec.get('sha256'))
    if spec['kind'] == 'binary':
        bindir = home / 'bootstrap' / 'bin'; bindir.mkdir(parents=True, exist_ok=True)
        target = bindir / ('codex.exe' if key.startswith('windows') else 'codex')
        if spec.get('archive'):
            with tempfile.TemporaryDirectory(dir=home / 'bootstrap') as temporary:
                temporary = Path(temporary)
                safe_extract(path, temporary)
                candidates = [p for p in temporary.rglob('*') if p.is_file() and p.name.startswith('codex-')]
                if len(candidates) != 1:
                    raise ValueError('Unexpected Codex archive layout')
                shutil.copy2(candidates[0], target)
        else:
            shutil.copy2(path, target)
        target.chmod(target.stat().st_mode | 0o100)
        for companion in spec.get('companions', []):
            auxiliary = bindir / companion['filename']
            download(companion['url'], auxiliary, companion['sha256'])
        executable = target
    elif spec['kind'] == 'vendor-script':
        # Vendor scripts own their dependency/payload verification and native update route.
        if key.startswith('windows'):
            command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(path)]
            if name == 'hermes' and non_interactive:
                command += ['-NonInteractive']
        else:
            command = ['/bin/bash', str(path)]
        if run(command, interactive=not non_interactive, timeout=1800).returncode:
            raise Pending(name + ' vendor installer unfinished; rerun setup')
        executable = find_executable(name, user_home, home / 'bootstrap')
    else:
        raise ValueError('Unknown client provisioning route')
    if not executable or run([str(executable), '--version']).returncode:
        raise Pending(name + ' installed but executable not yet discoverable; restart terminal or complete vendor prompts')
    return {'name': name, 'executable': str(executable.resolve()), 'installation': 'provisioned',
            'installer_sha256': digest, 'authentication': 'unverified', 'desktop': 'unverified'}


def authenticate_client(client: dict, non_interactive: bool) -> dict:
    """Guide native sign-in; never read tokens or select a billed provider for the member."""
    name, executable = client['name'], client['executable']
    if name in ('claude', 'codex'):
        status = ['auth', 'status'] if name == 'claude' else ['login', 'status']
        if run([executable, *status]).returncode == 0:
            return {'status': 'native-login-present', 'workflow_access': 'unverified'}
        login = ['auth', 'login'] if name == 'claude' else ['login']
        if non_interactive:
            return {'status': 'pending-native-login', 'next_command': [executable, *login]}
        print(name + ' will guide native sign-in; choose your account/provider in its prompts.')
        if run([executable, *login], interactive=True).returncode:
            raise Pending(name + ' sign-in unfinished; rerun setup')
        if run([executable, *status]).returncode:
            raise Pending(name + ' native login still needs attention')
        return {'status': 'native-login-present', 'workflow_access': 'unverified'}
    # Hermes supports multiple providers. Its wizard chooses the provider explicitly.
    if client['installation'] == 'existing':
        return {'status': 'unverified-existing-provider', 'next_command': [executable, 'doctor']}
    if non_interactive:
        return {'status': 'pending-native-setup', 'next_command': [executable, 'setup']}
    print('Hermes setup will guide provider selection. Existing subscriptions/API billing remain your choice.')
    if run([executable, 'setup'], interactive=True).returncode:
        raise Pending('Hermes provider setup unfinished; rerun setup')
    return {'status': 'native-wizard-completed', 'workflow_access': 'unverified'}

def provision_desktop(client: dict, home: Path, registry: dict, key: str,
                      non_interactive: bool) -> dict:
    name, executable = client['name'], client['executable']
    if name == 'hermes':
        if run([executable, 'desktop', '--build-only'], interactive=not non_interactive, timeout=1800).returncode:
            raise Pending('Hermes desktop build/install unfinished; complete vendor dependencies and resume')
        return {'installation': 'vendor-build-completed', 'verification': 'pending-fresh-local-session'}
    if name == 'codex':
        if non_interactive:
            return {'installation': 'pending-interactive-vendor-installer', 'verification': 'pending',
                    'next_command': [executable, 'app']}
        if run([executable, 'app'], interactive=True).returncode:
            raise Pending('Codex desktop vendor installation unfinished')
        return {'installation': 'vendor-installer-invoked', 'verification': 'pending-fresh-local-session'}
    spec = registry['desktop']['claude'][key]
    path = home / 'bootstrap' / 'downloads' / spec['filename']
    digest = download(spec['url'], path, spec.get('sha256'))
    if non_interactive:
        return {'installation': 'downloaded-pending-native-prompts', 'path': str(path),
                'installer_sha256': digest, 'verification': 'pending'}
    command = ['open', str(path)] if key.startswith('macos') else [str(path)]
    if run(command, interactive=True).returncode:
        raise Pending('Claude desktop installer could not open')
    return {'installation': 'native-installer-opened', 'installer_sha256': digest,
            'verification': 'pending-install-and-local-code-session'}


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, default=Path.home() / '.genie')
    parser.add_argument('--user-home', type=Path, default=Path.home())
    parser.add_argument('--harness', default=None)
    parser.add_argument('--module', action='append', default=[])
    parser.add_argument('--catalog')
    parser.add_argument('--core-source', type=Path)
    parser.add_argument('--release', type=Path, default=ROOT / 'bootstrap-release.json')
    parser.add_argument('--registry', type=Path, default=ROOT / 'bootstrap-registry.json')
    parser.add_argument('--non-interactive', action='store_true')
    parser.add_argument('--desktop', action=argparse.BooleanOptionalAction, default=None, help='provision selected local desktop surfaces')
    parser.add_argument('--enable-path', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--skip-dependencies', action='store_true', help='explicit development-only skip of dependency provisioning')
    args = parser.parse_args(argv)
    home, user_home = args.home.expanduser().resolve(), args.user_home.expanduser().resolve()
    receipt_path = home / 'bootstrap' / 'receipt.json'
    receipt = {'schema_version': 1, 'status': 'running', 'steps': {}, 'pending': []}
    if receipt_path.exists():
        receipt = load_json(receipt_path)
        receipt['status'], receipt['pending'] = 'running', []
    try:
        if sys.version_info < (3, 11):
            raise Pending('Python >=3.11 is required; use setup.sh/setup.ps1 to provision it')
        release = load_json(args.release)
        if not args.core_source and not release.get('core'):
            raise Pending('No approved portable Core release pin; this preview supports --core-source development only')
        registry = load_json(args.registry)
        key = platform_key()
        raw = args.harness
        if raw is None:
            if args.non_interactive:
                raise Pending('Choose --harness claude,codex,hermes (any subset)')
            raw = input('Select harnesses (claude,codex,hermes): ').strip()
        harnesses = list(dict.fromkeys(raw.split(',')))
        if not harnesses or any(name not in ('claude', 'codex', 'hermes') for name in harnesses):
            raise ValueError('Select one or more supported harnesses')
        if not args.module and not args.non_interactive:
            raw_modules = input('Optional departments (content-os,mobile-os,web-os; Enter for Core only): ').strip()
            args.module = list(dict.fromkeys(name.strip() for name in raw_modules.split(',') if name.strip()))
            if any(name not in ('content-os','mobile-os','web-os') for name in args.module):
                raise ValueError('Unknown optional department')
        if args.desktop is None:
            args.desktop = False if args.non_interactive else input('Set up local desktop applications too? [Y/n]: ').strip().lower() not in ('n','no')
        if args.skip_dependencies and args.core_source is None:
            raise ValueError('--skip-dependencies is available only with explicit development --core-source')
        receipt['selection'] = {'harnesses': harnesses, 'modules': args.module, 'desktop': args.desktop}
        write_json(receipt_path, receipt)
        gh = None
        if not args.core_source:
            gh = ensure_gh(home, registry, key, user_home)
            receipt['steps']['github-cli'] = {'executable': str(gh), 'status': 'available'}
            write_json(receipt_path, receipt)
            authenticate(gh, release['core']['repo'], args.non_interactive)
            receipt['steps']['github-access'] = {'repo': release['core']['repo'], 'status': 'verified'}
            write_json(receipt_path, receipt)
        core = materialize_core(home, source=args.core_source, release=release, gh=gh)
        receipt['steps']['core-source'] = {'path': str(core), 'status': 'available',
                                          'provenance': 'development' if args.core_source else 'published-pinned-release'}
        write_json(receipt_path, receipt)
        binaries = []
        for name in harnesses:
            client = provision_client(name, home, user_home, registry, key, args.non_interactive)
            receipt['steps'][name] = client
            write_json(receipt_path, receipt)
            client['authentication'] = authenticate_client(client, args.non_interactive)
            binaries.append(str(Path(client['executable']).parent))
            write_json(receipt_path, receipt)
            if args.desktop:
                client['desktop'] = provision_desktop(client, home, registry, key, args.non_interactive)
                write_json(receipt_path, receipt)
        # PATH is only this subprocess's discovery aid; Core persists explicit paths.
        previous_path = os.environ.get('PATH', '')
        command = [sys.executable, '-B', str(core / 'genie_cli.py'), '--home', str(home),
                   '--user-home', str(user_home), '--json', 'setup', '--harness', ','.join(harnesses)]
        if not args.skip_dependencies:
            command += ['--provision-dependencies']
        else:
            command += ['--skip-dependencies']
        for module in args.module:
            command += ['--module', module]
        catalog_source = args.catalog
        if catalog_source is None and not args.core_source:
            relative_catalog = release['core'].get('catalog', 'catalog.json')
            catalog_path = (core / relative_catalog).resolve()
            if core.resolve() not in catalog_path.parents or not catalog_path.is_file():
                raise ValueError('Published Core archive lacks an embedded catalog')
            catalog_source = str(catalog_path)
        if catalog_source:
            command += ['--catalog', catalog_source]
        if args.non_interactive:
            command += ['--non-interactive']
        try:
            os.environ['PATH'] = os.pathsep.join(binaries + [previous_path])
            result = run(command, timeout=600)
        finally:
            os.environ['PATH'] = previous_path
        if result.returncode:
            raise Pending('Core setup is incomplete; run its doctor/status and resume bootstrap')
        receipt['steps']['core-setup'] = {'status': 'completed', 'python': sys.executable}
        if not args.core_source:
            write_json(home / 'state' / 'release-channel.json', {
                'schema_version': 1,
                'metadata_url': 'https://raw.githubusercontent.com/Claude-Code-Academy/genie-ecosystem/main/bootstrap-release.json',
                'gh': str(gh), 'current_sha256': release['core']['sha256'],
                'current_root': str(core), 'current_source_revision': release['core']['source_revision']})
        connection_command = [sys.executable, '-B', str(core / 'genie_cli.py'), '--home', str(home), '--user-home', str(user_home), '--json', 'connections', 'setup']
        if args.non_interactive: connection_command.append('--non-interactive')
        connection_result = run(connection_command, interactive=not args.non_interactive)
        receipt['steps']['connections'] = {'status': 'setup-invoked' if connection_result.returncode == 0 else 'pending-secure-store-or-connection-setup'}
        if args.non_interactive and connection_result.returncode == 0:
            try:
                data = json.loads(connection_result.stdout)
                receipt['steps']['connections']['pending'] = data.get('pending', [])
            except (ValueError, AttributeError):
                receipt['steps']['connections']['status'] = 'pending-diagnostic-check'
        if args.enable_path:
            receipt['steps']['terminal-command'] = enable_command_path(home, user_home, key)
        receipt['status'] = 'pending-native-verification'
        receipt['pending'] = ['Complete native provider login and verify fresh CLI/local desktop sessions for every selected harness']
        write_json(receipt_path, receipt)
        print('Core setup completed. Provider login and fresh-session verification remain pending.')
        print('Resume receipt: ' + str(receipt_path))
        return 0
    except (KeyboardInterrupt, EOFError):
        receipt['status'] = 'pending'
        receipt['pending'] = ['Setup cancelled; rerun the same command to resume']
        write_json(receipt_path, receipt)
        print(receipt['pending'][0], file=sys.stderr)
        return 2
    except (ValueError, OSError, KeyError) as exc:
        receipt['status'] = 'pending' if isinstance(exc, Pending) else 'failed'
        receipt['pending'] = [str(exc)]
        write_json(receipt_path, receipt)
        print(str(exc), file=sys.stderr)
        print('Resume with the same setup arguments. Receipt: ' + str(receipt_path), file=sys.stderr)
        return 2 if isinstance(exc, Pending) else 1

class BootstrapLock:
    """An OS lock automatically releases after crashes; no stale PID guessing."""
    def __init__(self, home: Path):
        self.path = home / 'bootstrap' / 'operation.lock'
        self.stream = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.stream = self.path.open('a+b')
        self.stream.seek(0, 2)
        if self.stream.tell() == 0:
            self.stream.write(b'0'); self.stream.flush()
        self.stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self.stream.close()
            raise Pending('Another bootstrap operation is running for this Genie home') from exc
        return self

    def __exit__(self, *exc):
        if self.stream is not None:
            self.stream.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(), fcntl.LOCK_UN)
            self.stream.close()

def main(argv: list[str] | None = None) -> int:
    early = argparse.ArgumentParser(add_help=False)
    early.add_argument('--home', type=Path, default=Path.home() / '.genie')
    args, _ = early.parse_known_args(argv)
    try:
        with BootstrapLock(args.home.expanduser().resolve()):
            return _main(argv)
    except Pending as exc:
        print(str(exc), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
