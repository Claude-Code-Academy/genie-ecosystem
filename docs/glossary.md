# Glossary

Plain-English definitions of the terms used across the Genie ecosystem.

| Term | Means |
|---|---|
| **Genie** | A personal AI Operating System built on Claude Code — Claude with identity, memory, preferences, and a skill library. |
| **Claude Code** | Anthropic's official CLI for Claude. Everything in this ecosystem runs on it. ([docs](https://docs.claude.com/en/docs/claude-code)) |
| **Claude Cowork** | Claude Desktop's chat-first "knowledge-work" mode — a different surface from the CLI, with its own plugin marketplace. |
| **AI Operating System (AIOS)** | The framing for `genie-aios`: Claude as the layer you live in day-to-day, not a one-off chat. |
| **Skill** | A self-contained capability (a `SKILL.md` + supporting files) that Claude loads and triggers on specific phrases. |
| **SKILL.md** | The file that defines a skill — its description, trigger phrases, and instructions. |
| **Plugin / bundle** | A group of related skills packaged to install together in one command. |
| **Marketplace** | A repo Claude Code can install plugins from, via `/plugin marketplace add`. |
| **Library** | A flat collection of skills you copy by hand (one folder at a time), with no plugin machinery — i.e. `genie-skills-library`. |
| **Directory** | The reference-only catalog (`genie-directory`) — names, descriptions, when-to-use. No code. |
| **Bundle** | A themed set of skills inside a marketplace (e.g. `content-creation`). |
| **MCP (Model Context Protocol)** | The standard that lets Claude talk to external services (Supabase, Stripe, RevenueCat, Playwright, …). OS repos wire these up for you. |
| **Orchestrator** | A skill that chains other skills in order without reimplementing them — e.g. `genie-app-builder` runs the build pipeline. |
| **Overlay / PERSONAL.md** | Your private, gitignored customization layer for a skill. You edit `PERSONAL.md` (+ the `references/`, `assets/`, `examples/`, `snippets/` folders); the shared skill is never touched. |
| **Profile** | Which set of plugin bundles `init.py` installs — `member` (default) or `maintainer` (adds internal tooling). |
| **init.py** | The one-command setup script in the OS repos. Idempotent and interactive; supports `--dry-run` and `--yes`. |
| **genie-setup / setup.py** | Re-scaffolds skill overlays and regenerates `.env.example`. Run it after installing or updating skills inside a Genie repo. |
| **White-label** | A finished, working product released so members can rebrand and sell it as their own (`genie-whitelabel`). |
| **SHA pin** | In `genie-curated-marketplace`, every third-party entry is locked to a specific reviewed commit SHA, so you only ever get vetted code. |
| **env.example** | A file listing the API keys a skill needs. Copied/merged into your `.env` (which is always gitignored). |
| **Vault** | The Obsidian mount point in `genie-aios` (`vault/`) where your notes live and Claude reads them. |
| **🔒 members-only** | A repo accessible only to members of the `Claude-Code-Academy` GitHub org. [Join here](https://www.skool.com/claude-code-academy). |
| **Claude Code Academy** | The organization that builds and teaches the whole Genie ecosystem. |
