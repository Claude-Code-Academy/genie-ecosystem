# genie-ecosystem — the public front door

## Member onboarding authority

For any new member setup request, follow **[docs/getting-started.md](docs/getting-started.md)**.
That guide owns the copy/paste prompt and agent procedure. It applies even if the
member arrived through `genie-aios` or an optional department repository. Do not
replace it with old `init.py`, native plugin installation or skill-export recipes.
Existing installations can retain the legacy route when explicitly selected.

Genie is a shared capability and context layer for Claude Code, Codex and Hermes.
The portable alpha installs Core plus selected Content OS, Mobile OS and Web OS
packages. It uses shared resources and private scoped personalization. Other
native plugins are optional products, not implicitly portable departments.
The local machine, intended accounts and each selected terminal/desktop workflow
must be verified; a cloud container or a successful installer exit is insufficient.

Read the canonical guide before asking the member for technical details. Reuse
existing choices, perform authorized setup, and guide native login/secret prompts
without requesting secrets in chat. Use the same guide for resumption and diagnosis.

## Repository purpose and read order

This is the public map, guide and bootstrap for the Genie ecosystem. Private
product lifecycle code stays in `genie-aios`; departments retain their own source
repositories. No private product source, credentials, member data or client data
belongs here. All Genie repositories are under `Claude-Code-Academy`.

For repository development: this file → [README.md](README.md) → the relevant
[documentation](docs/getting-started.md) and [CONTRIBUTING.md](CONTRIBUTING.md).
There is no root PRD. Do not invent one. The latest onboarding inventory and
qualification boundaries are in [the ecosystem map](docs/member-ecosystem-map.md).

## Product ownership

| Need | Source |
|---|---|
| New member setup | This repository's canonical guide and launcher |
| Shared Core, lifecycle, context, adapters | `genie-aios` |
| Content OS and nine first-party native plugins | `genie-plugin-marketplace` |
| Mobile department and mobile pipeline | `genie-mobile-os` |
| Web department and web pipeline | `genie-web-os` |
| Curated external native tools | `genie-curated-marketplace` |
| Separate Obsidian/Git sync kit | `genie-second-brain` |

The `second-brain` native plugin provides skills; the standalone second-brain
repository provides sync plumbing and course material. Do not conflate them.
Maintainer-only repositories are excluded from member onboarding.

## Implementation routes

- `setup.sh` / `setup.ps1` reach a verified Python runtime and start `bootstrap.py`.
  These minimal transport launchers are the approved narrow exception to the
  Python-only tooling rule. Product logic remains stdlib Python in private Core.
- Published setup uses the reviewed `bootstrap-registry.json` and the private
  release envelope pinned by `bootstrap-release.json`. Never bypass verification
  or relabel a development build as published/qualified.
- Portable lifecycle uses `genie install`, `genie update`, `genie uninstall` and
  the shared Core operations. Private data is retained. Native managers remain
  relevant to separately installed legacy/native plugins.
- `install.py`, `uninstall.py` and `export-skills.py` remain legacy tools. The
  [legacy reference](docs/legacy-getting-started.md) describes their use. They are
  not fallback onboarding merely because an alpha workflow is pending.
- Preserve existing personalizations, instructions, profiles, credentials and
  generated projects. Do not resolve conflicts by blindly deleting registrations.

## Editing and validation

Keep one authoritative onboarding guide; other entry documents link to it. Update
[the ecosystem map](docs/member-ecosystem-map.md) when manifests or release scope
change. The native marketplace has nine first-party plugins; only Content OS is
currently its portable module. Curated entries are live; Cowork and whitelabel
catalog availability must be checked rather than assumed.

Keep member access, public visibility and [license](LICENSE) boundaries accurate.
A private repository grant gates future downloads, not copies already obtained.
Do not recommend shell-profile token exports from older optional native guides.

Run `python3 scripts/check_markdown_links.py` and `git diff --check` for document
changes. Run the bootstrap tests for provisioning changes. Unit/fixture tests do
not establish native sign-in, service access or desktop workflow certification.
