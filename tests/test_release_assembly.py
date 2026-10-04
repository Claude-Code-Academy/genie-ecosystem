"""Portable local-only publication provenance regressions."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('release_assembly', ROOT / 'scripts/assemble_bootstrap_release.py')
assembler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assembler)
REVISION = 'a' * 40

class ReleaseAssemblyTests(unittest.TestCase):
    def fixture(self, root, development=False, source_revision=REVISION, record_revision=REVISION):
        source = root / 'source'
        (source / 'src/genie').mkdir(parents=True)
        (source / 'genie_cli.py').write_text('pass', encoding='utf-8')
        (source / 'src/genie/__init__.py').write_text('', encoding='utf-8')
        artifact = root / 'core.zip'
        manifest = {'id': 'core', 'version': '0.1.0-dev.1', 'publisher': 'Example',
                    'source': {'revision': source_revision, 'development': development}}
        with zipfile.ZipFile(artifact, 'w') as bundle:
            bundle.writestr('genie.json', json.dumps(manifest))
        record = {'version': manifest['version'], 'publisher': 'Example', 'source_revision': record_revision,
                  'url': str(artifact), 'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest()}
        catalog = root / 'catalog.json'
        catalog.write_text(json.dumps({'schema_version': 1, 'modules': {'core': {'releases': [record]}}}), encoding='utf-8')
        return source, catalog

    def build(self, root, source, catalog):
        with patch.object(assembler.subprocess, 'check_output', side_effect=[REVISION, '']):
            return assembler.build(source, catalog, root / 'envelope.zip', REVISION)

    def test_clean_release_build_and_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = self.build(root, *self.fixture(root))
            result = assembler.assemble(archive, 'Example/core', 'preview', REVISION, root / 'release.json')
            self.assertEqual(result['core']['source_revision'], REVISION)

    def test_development_package_rejected_by_clean_release(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, 'non-development'):
                self.build(root, *self.fixture(root, development=True))
            self.assertFalse((root / 'envelope.zip').exists())

    def test_catalog_and_core_revision_mismatches_rejected(self):
        for src, record, message in [('b' * 40, REVISION, 'catalog'), ('b' * 40, 'b' * 40, 'envelope')]:
            with self.subTest(message=message), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                with self.assertRaisesRegex(ValueError, message):
                    self.build(root, *self.fixture(root, source_revision=src, record_revision=record))

    def test_remote_artifact_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, catalog = self.fixture(root)
            data = json.loads(catalog.read_text(encoding='utf-8'))
            data['modules']['core']['releases'][0]['url'] = 'https://example.invalid/core.zip'
            catalog.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'inspectable local'):
                self.build(root, source, catalog)

    def test_metadata_revision_or_mode_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = self.build(root, *self.fixture(root))
            for revision, development in [('b' * 40, False), (REVISION, True)]:
                with self.subTest(revision=revision, development=development), self.assertRaisesRegex(ValueError, 'provenance differs'):
                    assembler.assemble(archive, 'Example/core', 'preview', revision, root / 'release.json', development=development)
            self.assertFalse((root / 'release.json').exists())

    def test_explicit_development_build_and_assembly(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, catalog = self.fixture(root, development=True)
            archive = assembler.build(source, catalog, root / 'dev.zip', REVISION, development=True)
            assembler.assemble(archive, 'Example/core', 'preview', REVISION, root / 'release.json', development=True)
            with self.assertRaisesRegex(ValueError, 'provenance differs'):
                assembler.assemble(archive, 'Example/core', 'preview', REVISION, root / 'invalid.json')

if __name__ == '__main__':
    unittest.main()
