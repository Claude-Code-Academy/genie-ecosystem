<p align="center">
  <a href="https://www.skool.com/claude-code-academy">
    <img src="https://raw.githubusercontent.com/Claude-Code-Academy/genie-public-assets/main/assets/banner.png" alt="Genie — Claude Code Academy" width="100%">
  </a>
</p>

<h1 align="center">The Genie Ecosystem</h1>

<p align="center">
  <em>The starting point for everything Genie — a personal AI Operating System built on <a href="https://claude.com/claude-code">Claude Code</a>.<br>
  What each repo is, when to use it, how to use it, and where to go next.</em>
</p>

<p align="center">
  <a href="https://www.skool.com/claude-code-academy"><img src="https://img.shields.io/badge/Community-Skool-4F46E5?style=for-the-badge" alt="Skool community"></a>
  <a href="https://docs.claude.com/en/docs/claude-code"><img src="https://img.shields.io/badge/Built%20on-Claude%20Code-D97706?style=for-the-badge" alt="Claude Code"></a>
</p>

---

> **New here? Start with [docs/getting-started.md](docs/getting-started.md).**
> **Not sure which tool you need? Jump to [docs/when-to-use-what.md](docs/when-to-use-what.md).**

This is the **mother repo** for the Genie ecosystem. It owns no product code — it's the map **and the front door**. Everything Genie is published under [Claude Code Academy](https://github.com/Claude-Code-Academy); most of those repos are **🔒 members-only**. This repo is public so anyone can understand the whole picture before joining.

---

## Install everything in one command

**Prerequisites:** membership in the `Claude-Code-Academy` GitHub org, the `gh` CLI authenticated (`gh auth login`), plus `git`, `python3`, and the `claude` CLI on your PATH.

**Just want the personal OS?** That's the common path — clone genie-aios and run its setup:

```bash
gh repo clone Claude-Code-Academy/genie-aios && cd genie-aios && python3 init.py
```

Then restart Claude Code, put your API keys in `.env`, and you're working. See [docs/getting-started.md](docs/getting-started.md).

**Want several OSes at once?** Clone this repo, run one script, and pick what you want — it clones the OSes you choose and runs each one's own idempotent setup.

```bash
gh repo clone Claude-Code-Academy/genie-ecosystem && cd genie-ecosystem && python3 install.py
```

- `python3 install.py --all --yes` — everything, no questions asked.
- `python3 install.py --aios --profile member` — just the personal OS.
- `python3 install.py --dry-run --all` — preview every step, change nothing.

And the exact reverse, also one command:

```bash
python3 uninstall.py            # removes every plugin/marketplace/MCP server Genie installed
python3 uninstall.py --purge    # ...and deletes the clones the installer created
```

Your `.env` files, `PERSONAL.md` overlays, and built projects always survive an uninstall. `--purge` only ever deletes clones the installer itself created, and refuses to touch any clone with uncommitted changes or user data (`.env`, `projects/`, `outputs/`) unless you add `--force`. Before it touches anything, each OS's own uninstall now backs up your `.env`, `config.yaml`, `memory/`, `vault/`, and skill overlays to `~/.genie/backups/<os>-<timestamp>/` — after that, the clone is genuinely safe to delete by hand too (note: `outputs/` is **not** backed up, since it can be huge). Restore happens automatically the next time you run `python3 init.py` on a fresh clone (it offers to restore from the latest backup; `--yes` auto-restores). After installing, add plugins à la carte any time: `/plugin install <name>@genie`.

**Install once, use everywhere.** Installing a Genie plugin in Claude Code also makes its skills available in **Codex** (CLI + desktop + IDE), **Gemini CLI**, **Cursor**, **OpenCode**, and **Hermes** — no reinstall per tool. `init.py` does the fan-out on a fresh clone (step 7/7 — best-effort: it needs the `genie-essentials` plugin installed and prints a hint if the step was skipped); afterwards the `genie-add` skill (in the `genie-essentials` plugin) keeps it in sync, and `python3 export-skills.py` here is the standalone bridge that does the same job. Skills land in `~/.agents/skills/` (the open [agentskills.io](https://agentskills.io) dir, which Codex/Cursor/OpenCode scan) and `~/.hermes/skills/`; plugins that bundle an MCP server also register in Codex. **Restart the other harness** to pick up changes. Keys live once in `~/.claude/genie/.env` and every surface finds them. Claude Desktop's **Code tab** shares CLI installs automatically; **Cowork** does not (a known Anthropic limitation — use the Code tab, or let the sync feed Cowork via `~/.agents/skills`). Full detail: [docs/skills-and-plugins.md](docs/skills-and-plugins.md#install-once-use-everywhere).

---

## Keep it updated

**Genie itself** (the OS repo) updates from inside each clone:

```bash
python3 update.py            # fetch + fast-forward pull + re-run setup, in one step
python3 update.py --check    # just check whether an update is available — changes nothing
```

Or from chat: `/genie-update`. If your tree has local edits that conflict with the pull, `update.py` tells you exactly which files and how to stash/pull/pop — it never force-resets your changes.

**Plugin bundles** update separately, since they come from the marketplace, not the repo: `/plugin marketplace update genie` refreshes the catalog, then `/plugin update <bundle>` (or `/plugin update` for all installed bundles).

---

## What is Genie?

**Genie is a personal AI Operating System built on Claude Code.** Instead of treating Claude as a chat box, Genie gives it a persistent identity, memory, your preferences, and a library of skills — so one `git clone` becomes a daily driver you talk to in plain English, and the same template scales to a turnkey deployment you can set up for a paying client.

The ecosystem fans out from that core idea into three layers:

| Layer | What lives here | You're here to… |
|---|---|---|
| 🧠 **The OS** | `genie-aios` | Run Claude as your personal operating system — memory, daily commands, your installed skills. |
| 🚀 **The Builders** | `genie-web-os`, `genie-mobile-os`, `genie-whitelabel` | Ship real products — SaaS to Vercel, mobile apps to TestFlight, or rebrand a finished app. |
| 🧩 **The Capabilities** | `genie-skills-library`, `genie-plugin-marketplace`, `genie-cowork-plugin-marketplace`, `genie-curated-marketplace` | Add individual skills or themed plugin bundles to any Claude Code / Cowork session. |

---

## When to use what (the 30-second version)

| If you want to… | Reach for | Docs |
|---|---|---|
| Use Claude as your **daily personal OS** (memory, routines, your skills) | **genie-aios** 🔒 | [products](docs/products.md#genie-aios) |
| Build & ship a **web app / SaaS** (Next.js + Supabase + Stripe → Vercel) | **genie-web-os** 🔒 | [products](docs/products.md#genie-web-os) |
| Build & ship a **mobile app** (Expo → TestFlight) | **genie-mobile-os** 🔒 | [products](docs/products.md#genie-mobile-os) |
| Take a **finished app**, rebrand it, and sell it | **genie-whitelabel** 🔒 | [products](docs/products.md#genie-whitelabel) |
| Install a **themed bundle of skills** in one command | **genie-plugin-marketplace** (the `genie` marketplace) 🔒 | [skills & plugins](docs/skills-and-plugins.md) |
| Add **one specific skill** across every harness | `npx skills add Claude-Code-Academy/genie-plugin-marketplace --skill <name>` | [skills & plugins](docs/skills-and-plugins.md) |
| Install **vetted third-party** tools (SHA-pinned, reviewed) | **genie-curated-marketplace** 🔒 | [skills & plugins](docs/skills-and-plugins.md) |
| Add skills inside **Claude Cowork** (desktop, chat-first) | **genie-cowork-plugin-marketplace** 🔒 | [skills & plugins](docs/skills-and-plugins.md) |

Full decision guide, including head-to-head comparisons (AIOS vs Web OS vs Mobile OS, library vs marketplace): **[docs/when-to-use-what.md](docs/when-to-use-what.md)**.

---

## The full map

### Products — the OSes & builders

| Repo | What it is | Access |
|---|---|---|
| [genie-aios](https://github.com/Claude-Code-Academy/genie-aios) | The core personal AI Operating System. One clone → your daily driver; scales to a client deployment. | 🔒 Members |
| [genie-web-os](https://github.com/Claude-Code-Academy/genie-web-os) | Idea → SaaS → Vercel. Next.js + Supabase + Stripe + Playwright pipeline, one skill per stage. | 🔒 Members |
| [genie-mobile-os](https://github.com/Claude-Code-Academy/genie-mobile-os) | Idea → mobile app → TestFlight. Expo + RevenueCat pipeline, one skill per stage. | 🔒 Members |
| [genie-whitelabel](https://github.com/Claude-Code-Academy/genie-whitelabel) | Catalog of finished, production-ready apps published white-label. Take, rebrand, ship, sell. | 🔒 Members |

### Capabilities — skills, plugins & marketplaces

| Repo | What it is | Access |
|---|---|---|
| [genie-skills-library](https://github.com/Claude-Code-Academy/genie-skills-library) | Flat, copy-one-skill-at-a-time library. Drop a folder into `~/.claude/skills/`. | 🔒 Members |
| [genie-plugin-marketplace](https://github.com/Claude-Code-Academy/genie-plugin-marketplace) | The `genie` marketplace: **9 first-party plugins** (genie-essentials, content-os, coaching, google-workspace, ios-app-pipeline, second-brain, skill-authoring, skool-os, website-analytics). Also the authoring home for all of them. | 🔒 Members |
| [genie-cowork-plugin-marketplace](https://github.com/Claude-Code-Academy/genie-cowork-plugin-marketplace) | The same idea for **Claude Cowork** (desktop knowledge-work mode). | 🔒 Members |
| [genie-curated-marketplace](https://github.com/Claude-Code-Academy/genie-curated-marketplace) | **Live** catalog (~a dozen entries) of vetted third-party plugins/skills/MCP servers, each pinned to a reviewed commit SHA. | 🔒 Members |
| [genie-directory](https://github.com/Claude-Code-Academy/genie-directory) | Reference-only catalog — names, descriptions, when-to-use. No code. | 🔒 Members |
| [genie-second-brain](https://github.com/Claude-Code-Academy/genie-second-brain) | Setup kit + reference spec for a self-syncing, self-maintaining Obsidian "second brain" shared across your devices and AI agents — companion to the Second Brain course. **Not the same thing as the `second-brain` plugin** above: that plugin is the *skills* (create/maintain the vault from inside Claude Code); this repo is the Git-sync plumbing + course material underneath it. | 🔒 Members |

### Public — open to everyone

| Repo | What it is | Access |
|---|---|---|
| [expo-revenuecat-claude-starter](https://github.com/Claude-Code-Academy/expo-revenuecat-claude-starter) | Expo + RevenueCat starter with a CLAUDE.md ruleset for the full Expo → TestFlight workflow. | 🌐 Public |
| [genie-public-assets](https://github.com/Claude-Code-Academy/genie-public-assets) | Shared icons, banners, and images used across Genie public content. | 🌐 Public |

> **🔒 = members-only.** The links resolve only for members of the `Claude-Code-Academy` GitHub org. [Join the community](https://www.skool.com/claude-code-academy) to get access. There is also a small set of maintainer-only internal repos (backups + an admin marketplace) that aren't part of the member-facing surface.

---

## Documentation

| Doc | Read it when… |
|---|---|
| **[Getting started](docs/getting-started.md)** | You're new and want the shortest path from zero to a working setup. |
| **[When to use what](docs/when-to-use-what.md)** | You're deciding between two tools and want a clear call. |
| **[Products](docs/products.md)** | You want the deep dive on the OSes and the white-label catalog. |
| **[Skills & plugins](docs/skills-and-plugins.md)** | You want to add capabilities — library vs marketplace vs Cowork vs curated. |
| **[Workflows](docs/workflows.md)** | You want end-to-end recipes (ship a SaaS, run your day, deliver to a client). |
| **[Genie Profile](docs/genie-profile.md)** | You want to understand or configure the shared owner identity and brand layer. |
| **[FAQ](docs/faq.md)** | You have a specific question. |
| **[Glossary](docs/glossary.md)** | A term (OS, skill, plugin, overlay, MCP, Cowork…) isn't clicking. |

---

## Get access

Most of the ecosystem is built and taught inside the **[Claude Code Academy community](https://www.skool.com/claude-code-academy)**. Join to:

- Get access to the private repos and templates above
- Follow walkthroughs and live builds for Genie, Web OS, and Mobile OS
- Ship your own apps end-to-end with Claude Code — and learn to deliver them to real clients

<p align="center">
  <a href="https://www.skool.com/claude-code-academy"><img src="https://img.shields.io/badge/Join%20Claude%20Code%20Academy-Skool-4F46E5?style=for-the-badge" alt="Join Claude Code Academy"></a>
</p>

---

<p align="center"><sub>Maintained by <a href="https://github.com/Claude-Code-Academy">Claude Code Academy</a>. This repo is the map; each linked repo is the territory. See <a href="CONTRIBUTING.md">CONTRIBUTING.md</a> for how it stays current.</sub></p>
