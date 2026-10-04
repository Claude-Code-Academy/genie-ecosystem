import contextlib
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import bootstrap
spec = importlib.util.spec_from_file_location('assemble_bootstrap_release', ROOT / 'scripts' / 'assemble_bootstrap_release.py')
assembler = importlib.util.module_from_spec(spec); spec.loader.exec_module(assembler)

class BootstrapTests(unittest.TestCase):
    def test_published_gate_before_auth_or_installer(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(bootstrap, 'ensure_gh') as gh, patch.object(bootstrap, 'provision_client') as client:
            with contextlib.redirect_stderr(io.StringIO()):
                code = bootstrap.main(['--home', directory, '--harness', 'codex', '--non-interactive'])
            self.assertEqual(code, 2)
            gh.assert_not_called(); client.assert_not_called()
            receipt = json.loads((Path(directory) / 'bootstrap' / 'receipt.json').read_text())
            self.assertEqual(receipt['status'], 'pending')
            self.assertNotIn('token', json.dumps(receipt).lower())
    def test_local_bootstrap_runs_copied_entrypoint_without_gh(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source'; (source / 'src' / 'genie').mkdir(parents=True)
            (source / 'src' / 'genie' / '__init__.py').write_text('')
            (source / 'portable').mkdir(); (source / 'portable' / 'fixture.json').write_text('{}')
            output = root / 'invocation.json'
            (source / 'genie_cli.py').write_text('import json,sys\nfrom pathlib import Path\nwith Path(' + repr(str(output)) + ').open(\"a\") as stream: stream.write(json.dumps(sys.argv) + \"\\n\")\n')
            client = {'name': 'codex', 'executable': '/fixture/bin/codex', 'installation': 'existing', 'authentication': 'unverified', 'desktop': 'unverified'}
            with patch.object(bootstrap, 'platform_key', return_value='macos-arm64'), patch.object(bootstrap, 'provision_client', return_value=client), patch.object(bootstrap, 'authenticate_client', return_value={'status': 'pending-native-login'}), patch.object(bootstrap, 'ensure_gh') as gh, contextlib.redirect_stdout(io.StringIO()):
                code = bootstrap.main(['--home', str(root / 'home'), '--user-home', str(root / 'user'), '--core-source', str(source), '--harness', 'codex', '--module', 'content-os', '--non-interactive'])
            self.assertEqual(code, 0); gh.assert_not_called()
            args = json.loads(output.read_text().splitlines()[0])
            self.assertNotEqual(Path(args[0]).parent, source)
            self.assertIn('--module', args); self.assertIn('content-os', args)
            self.assertTrue((Path(args[0]).parent / 'portable' / 'fixture.json').exists())
            receipt = json.loads((root / 'home' / 'bootstrap' / 'receipt.json').read_text())
            self.assertEqual(receipt['status'], 'pending-native-verification')
            self.assertEqual(receipt['steps']['core-source']['provenance'], 'development')
    def test_auth_separates_identity_and_entitlement(self):
        results = [subprocess.CompletedProcess([], 0), subprocess.CompletedProcess([], 1)]
        with patch.object(bootstrap, 'run', side_effect=results) as run:
            with self.assertRaisesRegex(bootstrap.Pending, 'repository access'):
                bootstrap.authenticate(Path('/fake/gh'), 'Example/private', True)
            self.assertEqual(run.call_args_list[1].args[0][-1], '--silent')
        with patch.object(bootstrap, 'run', return_value=subprocess.CompletedProcess([], 1)) as run:
            with self.assertRaisesRegex(bootstrap.Pending, 'login required'):
                bootstrap.authenticate(Path('/fake/gh'), 'Example/private', True)
            self.assertEqual(run.call_count, 1)
    def test_download_checks_digest_and_preserves_original(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'archive'; target.write_bytes(b'original')
            with patch('urllib.request.urlopen', return_value=io.BytesIO(b'payload')):
                with self.assertRaisesRegex(ValueError, 'checksum'):
                    bootstrap.download('https://github.com/example/archive', target, '0' * 64)
            self.assertEqual(target.read_bytes(), b'original')
            self.assertFalse(list(Path(directory).glob('*.part')))
    def test_archive_traversal_and_symlink_parent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); archive = root / 'archive.zip'
            with zipfile.ZipFile(archive, 'w') as bundle: bundle.writestr('../escape', 'bad')
            with self.assertRaises(ValueError): bootstrap.safe_extract(archive, root / 'zip')
            archive = root / 'archive.tar.gz'
            with tarfile.open(archive, 'w:gz') as bundle:
                link = tarfile.TarInfo('link'); link.type = tarfile.SYMTYPE; link.linkname = 'safe'; bundle.addfile(link)
                entry = tarfile.TarInfo('link/file'); entry.size = 3; bundle.addfile(entry, io.BytesIO(b'bad'))
            with self.assertRaises(ValueError): bootstrap.safe_extract(archive, root / 'tar')
    def test_development_portable_content_affects_pin(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / 'source'; (source / 'src' / 'genie').mkdir(parents=True)
            (source / 'genie_cli.py').write_text('pass')
            (source / 'portable').mkdir(); file = source / 'portable' / 'catalog.json'; file.write_text('{}')
            home = root / 'home'; (home / 'bootstrap').mkdir(parents=True)
            first = bootstrap.materialize_core(home, source=source, release={}, gh=None)
            file.write_text('{"changed":true}')
            second = bootstrap.materialize_core(home, source=source, release={}, gh=None)
            self.assertNotEqual(first, second)
    def test_interactive_defaults_choose_core_and_desktop(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / 'source'; (source / 'src' / 'genie').mkdir(parents=True)
            (source / 'src' / 'genie' / '__init__.py').write_text(''); (source / 'genie_cli.py').write_text('pass')
            client = {'name': 'codex', 'executable': '/fixture/codex', 'installation': 'existing'}
            with patch('builtins.input', side_effect=['codex', '', '']), patch.object(bootstrap, 'platform_key', return_value='macos-arm64'), patch.object(bootstrap, 'provision_client', return_value=client), patch.object(bootstrap, 'authenticate_client', return_value={'status':'native-login-present'}), patch.object(bootstrap, 'provision_desktop', return_value={'installation':'pending'}), patch.object(bootstrap, 'run', return_value=subprocess.CompletedProcess([],0,'{}','')), contextlib.redirect_stdout(io.StringIO()):
                code = bootstrap.main(['--home', str(root / 'home'), '--user-home', str(root / 'user'), '--core-source', str(source)])
            self.assertEqual(code, 0)
            receipt = json.loads((root / 'home' / 'bootstrap' / 'receipt.json').read_text())
            self.assertEqual(receipt['selection'], {'harnesses':['codex'],'modules':[],'desktop':True})
            self.assertEqual(receipt['steps']['connections']['status'], 'setup-invoked')

    def test_owned_path_block_preserves_user_text_and_modified_block(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict('os.environ', {'SHELL':'/bin/zsh'}):
            root = Path(directory); user = root / 'user'; user.mkdir()
            profile = user / '.zprofile'; profile.write_text('export MY_SETTING=personal\n')
            first = bootstrap.enable_command_path(root / 'home', user, 'macos-arm64')
            self.assertEqual(first['status'], 'user-shell-PATH-enabled')
            self.assertIn('export MY_SETTING=personal', profile.read_text())
            unchanged = profile.read_bytes(); bootstrap.enable_command_path(root / 'home', user, 'macos-arm64')
            self.assertEqual(profile.read_bytes(), unchanged)
            profile.write_text(profile.read_text().replace('export PATH=', 'export USER_CHANGED_PATH='))
            changed = profile.read_bytes()
            with self.assertRaisesRegex(ValueError, 'User-modified'): bootstrap.enable_command_path(root / 'home', user, 'macos-arm64')
            self.assertEqual(profile.read_bytes(), changed)

    def test_published_cache_modification_and_marker_spoof_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); envelope = root / 'envelope.zip'
            with zipfile.ZipFile(envelope, 'w') as bundle:
                bundle.writestr('genie_cli.py', 'pass')
                bundle.writestr('src/genie/__init__.py', '')
                bundle.writestr('catalog.json', '{}')
            digest = hashlib.sha256(envelope.read_bytes()).hexdigest()
            release = {'core': {'repo':'Claude-Code-Academy/genie-aios','tag':'v1','asset':'envelope.zip','sha256':digest,'source_revision':'a'*40}}
            home = root / 'home'; (home / 'bootstrap').mkdir(parents=True)
            def run(command, **kwargs):
                target = Path(command[command.index('--dir')+1]) / 'envelope.zip'
                target.write_bytes(envelope.read_bytes()); return subprocess.CompletedProcess(command,0,'','')
            with patch.object(bootstrap, 'run', side_effect=run):
                core = bootstrap.materialize_core(home, source=None, release=release, gh=Path('/fixture/gh'))
                (core / 'genie_cli.py').write_text('modified')
                bootstrap.write_json(core / '.genie-envelope.json', {'files':bootstrap.core_inventory(core)})
                with self.assertRaisesRegex(ValueError, 'modified'):
                    bootstrap.materialize_core(home, source=None, release=release, gh=Path('/fixture/gh'))

    def test_real_upstream_pin_shapes_and_launcher_consistency(self):
        registry = bootstrap.load_json(ROOT / 'bootstrap-registry.json')
        launcher = (ROOT / 'setup.sh').read_text()
        for key, platform in registry['platforms'].items():
            for kind in ('python', 'gh'):
                self.assertRegex(platform[kind]['sha256'], r'^[0-9a-f]{64}$')
                self.assertTrue(platform[kind]['url'].startswith('https://github.com/'))
        self.assertIn(registry['platforms']['macos-arm64']['python']['sha256'], launcher)
        self.assertIn(registry['platforms']['macos-arm64']['python']['url'], launcher)
    def test_release_assembler_hashes_actual_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); archive = root / 'core.zip'
            with zipfile.ZipFile(archive, 'w') as bundle:
                bundle.writestr('genie_cli.py', 'pass')
                bundle.writestr('src/genie/__init__.py', '')
                bundle.writestr('bootstrap-provenance.json', json.dumps({'source_revision': 'a' * 40, 'development': True}))
            data = assembler.assemble(archive, 'Example/core', 'v1', 'a' * 40, root / 'release.json', development=True)
            self.assertEqual(data['core']['sha256'], hashlib.sha256(archive.read_bytes()).hexdigest())
            self.assertEqual(data['status'], 'assembled-not-published')
    def test_envelope_builder_embeds_verified_relative_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / 'source'; (source / 'src' / 'genie').mkdir(parents=True)
            (source / 'genie_cli.py').write_text('pass')
            (source / 'src' / 'genie' / '__init__.py').write_text('')
            artifact = root / 'core-package.zip'; artifact.write_bytes(b'verified fixture artifact')
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            catalog = root / 'catalog.json'
            catalog.write_text(json.dumps({'schema_version': 1, 'modules': {'core': {'releases': [{'version': '0.1.0', 'url': str(artifact), 'sha256': digest}]}}}))
            archive = assembler.build(source, catalog, root / 'envelope.zip', 'a' * 40, development=True)
            with zipfile.ZipFile(archive) as bundle:
                embedded = json.loads(bundle.read('catalog.json'))
                path = embedded['modules']['core']['releases'][0]['url']
                self.assertTrue(path.startswith('artifacts/'))
                self.assertEqual(bundle.read(path), artifact.read_bytes())
                self.assertIn('genie_cli.py', bundle.namelist())
            artifact.write_bytes(b'modified')
            with self.assertRaisesRegex(ValueError, 'digest'):
                assembler.build(source, catalog, root / 'invalid.zip', 'a' * 40, development=True)

    def test_vendor_script_real_command_and_desktop_pending(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); cli = root / 'claude'; cli.write_bytes(b'fixture')
            registry = {'clients': {'claude': {'macos-arm64': {'kind': 'vendor-script', 'filename': 'install.sh', 'url': 'https://claude.ai/install.sh', 'sha256': None}}}, 'desktop': {'claude': {'macos-arm64': {'filename': 'Claude.dmg', 'url': 'https://claude.ai/download', 'sha256': None}}}}
            def download(url, path, expected): path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(b'fixture'); return 'a' * 64
            with patch.object(bootstrap, 'find_executable', side_effect=[None, cli]), patch.object(bootstrap, 'download', side_effect=download), patch.object(bootstrap, 'run', return_value=subprocess.CompletedProcess([], 0)) as run:
                client = bootstrap.provision_client('claude', root / 'home', root / 'user', registry, 'macos-arm64', True)
                desktop = bootstrap.provision_desktop(client, root / 'home', registry, 'macos-arm64', True)
            self.assertEqual(run.call_args_list[0].args[0][0], '/bin/bash')
            self.assertEqual(desktop['installation'], 'downloaded-pending-native-prompts')
            self.assertEqual(desktop['verification'], 'pending')

    def test_os_lock_releases_and_rejects_concurrent_operation(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            with bootstrap.BootstrapLock(home):
                with self.assertRaises(bootstrap.Pending):
                    with bootstrap.BootstrapLock(home): pass
            with bootstrap.BootstrapLock(home): pass

    def test_native_auth_does_not_select_api_billing(self):
        client = {'name': 'claude', 'executable': '/fixture/claude', 'installation': 'existing'}
        with patch.object(bootstrap, 'run', return_value=subprocess.CompletedProcess([], 1)) as run:
            pending = bootstrap.authenticate_client(client, True)
        self.assertEqual(pending['status'], 'pending-native-login')
        self.assertEqual(pending['next_command'], ['/fixture/claude', 'auth', 'login'])
        self.assertEqual(run.call_count, 1)
        with patch.object(bootstrap, 'run') as run:
            result = bootstrap.authenticate_client({'name': 'hermes', 'executable': '/fixture/hermes', 'installation': 'existing'}, False)
        run.assert_not_called()
        self.assertEqual(result['status'], 'unverified-existing-provider')

    def test_binary_provisioner_uses_downloaded_artifact_and_probe(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = {'clients': {'codex': {'windows-x64': {'kind': 'binary', 'filename': 'codex.exe', 'url': 'https://github.com/example/codex.exe', 'sha256': 'a' * 64}}}}
            def download(url, path, expected): path.write_bytes(b'fixture'); return expected
            with patch.object(bootstrap, 'find_executable', return_value=None), patch.object(bootstrap, 'download', side_effect=download), patch.object(bootstrap, 'run', return_value=subprocess.CompletedProcess([], 0)):
                data = bootstrap.provision_client('codex', root / 'home', root / 'user', registry, 'windows-x64', True)
            self.assertEqual(Path(data['executable']).read_bytes(), b'fixture')
            self.assertEqual(data['authentication'], 'unverified')

if __name__ == '__main__': unittest.main()
