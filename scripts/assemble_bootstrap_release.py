#!/usr/bin/env python3
"""Create publication metadata from a real built Core archive. Does not publish."""
import argparse
import hashlib
import json
import sys
import tempfile
import re
import subprocess
import zipfile
import io
from pathlib import Path

def _verify_package(content: bytes, module: str, record: dict, revision: str) -> None:
    """Verify publication identity against the bytes being embedded."""
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as bundle:
            manifest = json.loads(bundle.read('genie.json'))
        source = manifest['source']
        if source.get('development') is not False:
            raise ValueError('Release packages must explicitly declare non-development provenance')
        if not re.fullmatch('[0-9a-f]{40}', source.get('revision', '')):
            raise ValueError('Release package requires an exact source revision')
        if (manifest['id'] != module or manifest['version'] != record.get('version')
                or manifest['publisher'] != record.get('publisher')
                or source['revision'] != record.get('source_revision')):
            raise ValueError('Release package identity/provenance differs from catalog')
        if module == 'core' and source['revision'] != revision:
            raise ValueError('Core package provenance differs from envelope revision')
    except (KeyError, TypeError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        raise ValueError('Release package lacks a valid publisher manifest') from exc


def assemble(archive: Path, repo: str, tag: str, revision: str, output: Path, *, development: bool = False) -> dict:
    if not archive.is_file() or not re.fullmatch(r'[\w.-]+/[\w.-]+', repo):
        raise ValueError('Existing archive and valid repository are required')
    if not re.fullmatch('[0-9a-f]{40}', revision) or not tag or tag.startswith('-'):
        raise ValueError('Exact source commit and release tag are required')
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from bootstrap import safe_extract
    with tempfile.TemporaryDirectory() as directory:
        stage = Path(directory)
        safe_extract(archive, stage)
        if not (stage / 'genie_cli.py').is_file() or not (stage / 'src' / 'genie' / '__init__.py').is_file():
            raise ValueError('Core archive lacks source entrypoint and Python package')
        try:
            provenance = json.loads((stage / 'bootstrap-provenance.json').read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError('Core archive lacks valid envelope provenance') from exc
        if provenance.get('source_revision') != revision or provenance.get('development') is not development:
            raise ValueError('Core archive provenance differs from publication metadata/mode')
        if not development:
            catalog = json.loads((stage / 'catalog.json').read_text(encoding='utf-8'))
            _verify_catalog(stage, catalog, revision, embedded=True)
        for path in stage.rglob('*'):
            if path.name.startswith('.env') and path.name != '.env.example':
                raise ValueError('Core archive contains private credentials file')
    digest = hashlib.sha256()
    with archive.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    data = {'schema_version': 1, 'status': 'assembled-not-published', 'core': {
        'repo': repo, 'tag': tag, 'asset': archive.name, 'sha256': digest.hexdigest(),
        'source_revision': revision, 'catalog': 'catalog.json'}}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    return data


def _verify_catalog(base: Path, catalog: dict, revision: str, *, embedded: bool = False) -> None:
    if catalog.get('schema_version') != 1 or not isinstance(catalog.get('modules'), dict) or 'core' not in catalog['modules']:
        raise ValueError('Catalog must include a built Core release')
    for module, entry in catalog['modules'].items():
        releases = entry.get('releases', []) if isinstance(entry, dict) else entry
        if not isinstance(releases, list) or not releases:
            raise ValueError('Release catalog modules require package records')
        for record in releases:
            url = record.get('url', '')
            if '://' in url:
                raise ValueError('Release assembly requires inspectable local package artifacts')
            artifact = Path(url)
            if embedded and (artifact.is_absolute() or not (base / artifact).resolve().is_relative_to(base.resolve())):
                raise ValueError('Envelope catalog artifact must remain inside the archive')
            if not artifact.is_absolute():
                artifact = base / artifact
            if artifact.is_symlink() or not artifact.is_file():
                raise ValueError('Local catalog artifact unavailable')
            content = artifact.read_bytes()
            if hashlib.sha256(content).hexdigest() != record.get('sha256'):
                raise ValueError('Catalog artifact digest mismatch')
            _verify_package(content, module, record, revision)

def build(source: Path, catalog_path: Path, output: Path, revision: str, *, development: bool = False) -> Path:
    """Build a clone-independent envelope around already-built verified packages."""
    source = source.resolve()
    if not re.fullmatch('[0-9a-f]{40}', revision):
        raise ValueError('An exact source revision is required')
    if not development:
        observed = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
        dirty = subprocess.check_output(['git', '-C', str(source), 'status', '--porcelain'], text=True).strip()
        if observed != revision or dirty:
            raise ValueError('Release envelope requires a clean source at the exact revision')
    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    if catalog.get('schema_version') != 1 or 'core' not in catalog.get('modules', {}):
        raise ValueError('Catalog must include a built Core release')
    if not development:
        _verify_catalog(catalog_path.resolve().parent, catalog, revision)
    payload = {}
    entrypoint = source / 'genie_cli.py'
    if not entrypoint.is_file() or not (source / 'src' / 'genie' / '__init__.py').is_file():
        raise ValueError('Portable Core source missing')
    for path in [entrypoint, *sorted((source / 'src' / 'genie').rglob('*.py'))]:
        if path.is_symlink():
            raise ValueError('Core source symlinks are unsupported')
        payload[path.relative_to(source).as_posix()] = path.read_bytes()
    if (source / 'LICENSE').is_file():
        payload['LICENSE'] = (source / 'LICENSE').read_bytes()
    for module, entry in catalog['modules'].items():
        releases = entry.get('releases', []) if isinstance(entry, dict) else entry
        for record in releases:
            url = record.get('url', '')
            if url.startswith('https://'):
                continue
            if '://' in url:
                raise ValueError('Unsupported package transport in publication catalog')
            artifact = Path(url)
            if not artifact.is_absolute():
                artifact = catalog_path.resolve().parent / artifact
            if not artifact.is_file() or artifact.is_symlink():
                raise ValueError('Local catalog artifact unavailable')
            content = artifact.read_bytes()
            if hashlib.sha256(content).hexdigest() != record.get('sha256'):
                raise ValueError('Catalog artifact digest mismatch')
            relative = 'artifacts/' + record['sha256'] + '-' + artifact.name
            payload[relative] = content
            record['url'] = relative
    payload['catalog.json'] = (json.dumps(catalog, indent=2) + '\n').encode()
    payload['bootstrap-provenance.json'] = (json.dumps({'source_revision': revision, 'development': development}) + '\n').encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as stream, zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for name, content in sorted(payload.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, content)
    return output

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    route = parser.add_mutually_exclusive_group(required=True)
    route.add_argument('--core-archive', type=Path)
    route.add_argument('--core-source', type=Path)
    parser.add_argument('--catalog', type=Path)
    parser.add_argument('--development', action='store_true')
    parser.add_argument('--repo', required=True)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--source-revision', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    archive = args.core_archive
    if args.core_source:
        if args.catalog is None:
            parser.error('--core-source requires --catalog with built package artifacts')
        archive = args.output.parent / 'genie-core-bootstrap.zip'
        build(args.core_source, args.catalog, archive, args.source_revision, development=args.development)
    assemble(archive, args.repo, args.tag, args.source_revision, args.output, development=args.development)

if __name__ == '__main__':
    main()
