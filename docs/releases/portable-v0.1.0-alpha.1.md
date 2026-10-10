# Portable Genie v0.1.0-alpha.1

This is an opt-in alpha for members who want to try shared Genie capabilities
across Claude Code, Codex and Hermes. It is not a certified stable release.

## Included

- Small Core and optional Content OS, Mobile OS and Web OS: 69 namespaced skills.
- One shared package store with native discovery adapters and scoped private preferences.
- Guided shell/PowerShell setup, department install/update/remove, rollback,
  recovery, knowledge interfaces and private custom skills.
- Native secure-store interfaces and isolated mapped-workspace credential scopes.
- Six managed Content helper operations; a real carousel render verified private
  colors, SVG logo and fonts without modifying publisher packages.

After cloning or downloading the public setup repository, run `./setup.sh` on
macOS or `.\setup.ps1` on Windows. Sign in to GitHub with a member account and
complete the selected providers' native login. Setup never silently changes a
subscription login to API billing. Core is selected unless departments are added.
See [the canonical member setup guide and prompt](../getting-started.md).

## Qualification limits

The corrected local release gate passed 203 Core tests, 22 bootstrap tests and 14
Content regression tests; one Content test was skipped for an absent optional
dependency. The [Core CI matrix](https://github.com/Claude-Code-Academy/genie-aios/actions/runs/37221616937)
passed on macOS, Windows and Linux with Python 3.11/3.12, and the
[bootstrap matrix](https://github.com/Claude-Code-Academy/genie-ecosystem/actions/runs/37221173242)
passed on all three operating systems. Single-repository CI explicitly skips
checks needing sibling product sources; those passed in the complete local
release workspace. Automated tests do not certify native account, desktop or
Windows workflow behavior.

Real fresh/existing machine installation, native desktop skill invocation,
secure-store/provider authentication and migration pilots remain pending. Some
optional media and platform helpers, including complete Remotion, WhisperX,
pyCapCut and EAS routes, remain unqualified or blocked. There is no universal native
hook enforcement or custom desktop/orchestration engine in this release.

Prefer a separate pilot profile. Preserve existing native integrations during
migration; unknown customizations are not automatically retired. Report the
selected harness, version and `genie doctor` output with secrets removed.

## Distribution

The public setup repository contains launchers, documentation and non-secret
release pins. Complete packages and the bootstrap envelope remain in their
existing private product repositories. GitHub membership is still required.
Native plugin versions and portable package versions are separate: Content's
native plugin is 0.17.0; portable department manifests are 0.1.0-alpha.1.
