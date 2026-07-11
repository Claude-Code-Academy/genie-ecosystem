# genie-ecosystem — the public front door

This is the **public map and front door** for the Genie ecosystem. It owns no product code. It exists so a new human or a fresh agent can answer three questions fast: *what is this, what do I install first, and which repo do I go to for X.*

Everything Genie is published under the [Claude-Code-Academy](https://github.com/Claude-Code-Academy) GitHub org. Most product repos are members-only; this one is public, so **nothing private (keys, member-only internals, client data) belongs here.**

> **Read order for agents:** this `CLAUDE.md` → [`README.md`](README.md) → [`docs/`](docs/). **There is no PRD** — README plus the `docs/` set are the source of truth. Don't invent one; if vision-level context is needed, it lives in README's "What is Genie?" section.

## What Genie is

Genie is a plug-and-play AI OS ecosystem built on Claude Code by Claude Code Academy. The core promise: one `git clone` + `python3 init.py` turns Claude Code into a personal operating system with identity, memory, your preferences, and a curated library of skills — and the same skills follow you into every other AI harness on the machine (Codex, Gemini CLI, Cursor, OpenCode, Hermes).

## The new-user story (say this when someone asks "how do I start")

Prereqs: membership in the `Claude-Code-Academy` GitHub org, `gh` CLI authed (`gh auth login`), plus `git`, `python3`, and the `claude` CLI on PATH. Then:

```bash
gh repo clone Claude-Code-Academy/genie-aios && cd genie-aios && python3 init.py
```

Restart Claude Code → put API keys in `.env` → done. `init.py` registers the marketplaces, installs the member plugin bundle, scaffolds overlays + `.env`, personalizes config, and fans skills out to the other harnesses (step 7/7). Full walkthrough: [`docs/getting-started.md`](docs/getting-started.md).

## Repo map — "if the user wants X, go to repo Y"

| The user wants to… | Send them to |
|---|---|
| Run Claude as their personal daily OS | **genie-aios** — the OS members clone; THE entry point |
| Build & ship a web app / SaaS (→ Vercel) | **genie-web-os** |
| Build & ship a mobile app (Expo → TestFlight) | **genie-mobile-os** |
| Understand the whole ecosystem / find a repo | **genie-ecosystem** (this repo) |
| Add a themed bundle of Genie skills | **genie-plugin-marketplace** (the `genie` marketplace: 8 first-party plugins; also the authoring home) |
| Add a vetted third-party plugin/skill/MCP | **genie-curated-marketplace** (the `genie-curated` marketplace: SHA-pinned catalog, live) |
| Maintainer-only admin tooling | **genie-internal-plugins** (`genie-internal` marketplace) |

Anthropic's own official marketplace complements these. Deep dives live in [`docs/products.md`](docs/products.md) and [`docs/skills-and-plugins.md`](docs/skills-and-plugins.md).

## What lives in this repo

- **`install.py`** — one-command multi-OS installer: clones the OSes you pick and runs each one's own idempotent setup. `--all --yes`, `--dry-run`, `--aios`, etc.
- **`uninstall.py`** — the exact reverse (`--purge` also deletes installer-created clones). Byte-identical to the canonical copy in genie-aios.
- **`export-skills.py`** — the cross-harness bridge: copies installed Genie skills into `~/.agents/skills/` (Codex/Cursor/OpenCode) and `~/.hermes/skills/`. It **delegates to `genie_sync.py`** (the `genie-add` skill in genie-essentials) when that's installed — same job, kept current by `/plugin update`. See README's install-once section.
- **`docs/`** — getting-started, when-to-use-what, skills-and-plugins, products, faq, glossary, workflows, genie-profile.

## Editing rules

- Keep it **public-safe**: no secrets, no member-only internals, no client data.
- Keep facts consistent with the canonical narrative: the `genie` marketplace has **8** first-party plugins (genie-essentials, content-os, coaching, google-workspace, ios-app-pipeline, second-brain, skill-authoring, website-analytics); `genie-curated` is **live** with vetted SHA-pinned entries; skills install once and fan out to every harness.
- Don't duplicate the manuals — this repo links to the product repos' own READMEs; keep those links resolving.
- Scripts are Python 3, stdlib only, cross-platform (Windows uses `python`). See [`CONTRIBUTING.md`](CONTRIBUTING.md).
