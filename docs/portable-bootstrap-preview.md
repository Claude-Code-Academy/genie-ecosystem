# Portable Genie bootstrap preview

> **Member installation:** use [the canonical setup guide](getting-started.md). This page is a developer/provisioning reference; its `--core-source` examples are not the published member path.

This guide describes the opt-in `v0.1.0-alpha.1` prerelease. The client/platform matrix has not passed real machine qualification. Existing `install.py` remains the legacy installation route. Product archives stay in private member repositories; only the launcher and release pins are public. See [release notes](releases/portable-v0.1.0-alpha.1.md).

The preview makes Genie the lifecycle owner for Core and selected departments across Claude Code, Codex, and Hermes. Departments are optional. Native plugins, where necessary, are adapter details managed by Genie. The launcher works from a clone or a downloaded ZIP; Git is not a prerequisite.

Run from the extracted public repository:

```sh
./setup.sh --harness codex --core-source /absolute/path/to/genie-aios --skip-dependencies
```

On native Windows x64:

```powershell
.\setup.ps1 --harness codex --core-source C:\path\to\genie-aios --skip-dependencies
```

The `--core-source` route is for isolated source development; ordinary members use the published digest-pinned envelope. It copies the portable entrypoint, Python package, and portable package data into the managed Genie home. Later execution does not depend on retaining the original clone. It does not obtain private release credentials unnecessarily.

For published setup, a maintainer assembles `bootstrap-release.json` from a real built Core release archive and exact source commit, publishes that exact artifact, and verifies member access. Without the release pin, ordinary setup stops before client installation or GitHub authentication. It never guesses a release URL or silently falls back to the current repository branch.

```sh
python scripts/assemble_bootstrap_release.py --core-archive /path/core.zip \
  --repo ORGANIZATION/REPOSITORY --tag ACTUAL_TAG \
  --source-revision EXACT_40_CHARACTER_COMMIT --output /path/bootstrap-release.json
```

Alternatively, pass `--core-source /path/to/genie-aios --catalog /path/to/catalog.json` instead of `--core-archive` to build the bootstrap envelope from a clean exact source commit and already-built, digest-verified local package artifacts. It embeds `catalog.json` with relative artifact paths; the published bootstrap selects it automatically. `--development` explicitly skips the clean Git requirement for isolated fixture testing and does not establish release provenance.

That command writes metadata; it does not publish or establish release approval. The Core archive must contain `genie_cli.py`, `src/genie/`, an embedded `catalog.json`, and the referenced built package artifacts. Publication and authenticated asset verification must precede setting the release pin. Alpha publication does not establish clean-machine qualification; a stable release still requires that evidence.

## What setup provisions

The launchers reuse compatible Python 3.11+; otherwise they fetch a digest-pinned standalone Python runtime from the upstream [Python build standalone release](https://github.com/astral-sh/python-build-standalone/releases/tag/20261003). Managed runtime provisioning currently targets Apple Silicon macOS and native Windows x64. Missing GitHub CLI comes from the pinned [GitHub CLI release](https://github.com/cli/cli/releases/tag/v2.102.0). The initial registry contains actual upstream SHA-256 values observed on 4 October 2026, not guessed checksums. These pins still require native-machine qualification.

Published setup uses native `gh auth login`, then verifies access to the exact private Core repository separately from identity. Organization SSO or membership issues remain guided pending steps. Tokens are not exported into shell profiles or saved in receipts. The current published envelope embeds all four portable module artifacts, so its download is gated by private Core access; it does not enforce separate department-repository entitlement. Optional source clones and native marketplaces require their own access grants.

Selected missing CLIs use explicit vendor routes:

- Claude: the official [native installer](https://code.claude.com/docs/en/setup), downloaded before invocation. The moving vendor script uses vendor HTTPS and its native payload verification; this is deliberately identified separately from Genie's digest-pinned runtime tools. The endpoint returned HTTP 403 in the development environment, so successful installation here is unverified.
- Codex: the [official release](https://github.com/openai/codex/releases/tag/rust-v0.160.0) at an exact upstream artifact digest. Windows sandbox companion executables are included. Native functionality and platform trust prompts remain qualification work. For Claude/Codex, setup checks native login status and guides their native sign-in when interactive; it never selects the API billing flag. A new Hermes installation uses its provider wizard, while an existing provider configuration remains unchanged and explicitly unverified.
- Hermes: the official [installer](https://hermes-agent.nousresearch.com/docs/getting-started/installation), with a fetched script digest recorded in the registry. If the moving vendor endpoint changes, the checksum fails and needs a reviewed registry update. Vendor installation owns its runtime/dependency and updater behavior.

Interactive setup asks which optional departments to add (Enter keeps Core only) and whether to install local desktops (default yes). Noninteractive setup provisions only explicitly selected surfaces; add `--desktop` for desktop setup. Desktop provisioning uses vendor routes: Hermes builds its desktop without launching it, Codex's vendor `app` path guides its installation, and Claude's official native installer download opens for OS/user prompts. Noninteractive Codex/Claude desktop installation remains pending native prompts. Downloading a desktop artifact or a successful build never marks the GUI verified. Setup does not silently switch to WSL, remote execution, or API billing.

## Options and recovery

`--harness claude,codex,hermes` selects any subset. `--module` can repeat; omitting it installs Core without adding every department. `--catalog` selects the Core catalog. Dependencies are provisioned by default. `--skip-dependencies` is an explicit development-only opt-out with `--core-source`; it is not available for published member setup. `--home` controls Genie storage, `--user-home` controls Core's user configuration scope, and `--non-interactive` makes missing sign-in or required prompts precise pending steps. Vendor installers still use their native account/home conventions; `--user-home` does not sandbox vendor installation.

`GENIE_BOOTSTRAP_HOME` controls where a launcher provisions a missing runtime; use matching `--home` for the full setup. Managed executable paths are passed to Core through only the setup subprocess's discovery environment; Core stores explicit executable paths. The terminal PATH step separately owns its small shell/registry registration.

Setup invokes Core connection setup so required API keys can be entered with hidden input and stored in the native secure store. Noninteractive or deferred credentials remain pending; values never enter bootstrap arguments or receipts. It adds an owned, fingerprinted PATH block for macOS zsh/bash, or the native Windows user PATH, while preserving unrelated entries and backing up prior values. Use `--no-enable-path` to retain the absolute launcher only; reopen the terminal after PATH setup.

Published setup saves a non-secret trusted release-channel record with the absolute GitHub CLI path and current artifact digest. `genie update` fetches fresh publisher-origin metadata, verifies and stages a complete engine plus embedded catalog, activates the new engine, and executes the update cohort through it. `--check` keeps install state unchanged. Core holds defer engine replacement. Engine/config backups and a durable `core_update.json` support retry and rollback; already-published module changes use forward recovery rather than falsely claiming restoration. Cached engine files are revalidated against retained digest-pinned proof archives, so editing a marker cannot redefine trusted contents. No new runtime executable is overwritten in use.

Rerun the same command to resume. An OS lock serializes bootstrap operations. A non-secret receipt at `<Genie home>/bootstrap/receipt.json` records selected harnesses/modules and actual completed/pending steps. Authentication, discovered executables, desktop installation, and fresh local-session verification remain distinct. Failure retains source code, private data and previous receipts. Incomplete derived runtime/tool directories are preserved for explicit repair rather than automatically deleted.

The shell and PowerShell launchers are a narrow, approved exception to the old Python-only rule: they exist solely to reach Python on a fresh machine. All orchestration and lifecycle code remains stdlib Python. No daemon or new Genie desktop is required.

## Validation before community release

Temporary-home tests cover release gating, local source transport, digest rejection, unsafe archives, private entitlement failures, selected client invocation, and pending verification. They do not establish vendor installation, desktop discovery, provider login, or actual workflows on macOS/Windows. Test those on clean and existing member machines before claiming support. Preserve vendor update ownership, trust prompts and user choices.
