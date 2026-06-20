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

This is the **mother repo** for the Genie ecosystem. It owns no product code — it's the map. Everything Genie is published under [Claude Code Academy](https://github.com/Claude-Code-Academy); most of those repos are **🔒 members-only**. This repo is public so anyone can understand the whole picture before joining.

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
| Add **one specific skill** to any Claude Code session | **genie-skills-library** 🔒 | [skills & plugins](docs/skills-and-plugins.md#genie-skills-library) |
| Install a **themed bundle of skills** in one command | **genie-plugin-marketplace** 🔒 | [skills & plugins](docs/skills-and-plugins.md#genie-plugin-marketplace) |
| Add skills inside **Claude Cowork** (desktop, chat-first) | **genie-cowork-plugin-marketplace** 🔒 | [skills & plugins](docs/skills-and-plugins.md#genie-cowork-plugin-marketplace) |
| Install **vetted third-party** tools (SHA-pinned, reviewed) | **genie-curated-marketplace** 🔒 | [skills & plugins](docs/skills-and-plugins.md#genie-curated-marketplace) |
| Just **look up** a skill/plugin by name | **genie-directory** 🔒 | [skills & plugins](docs/skills-and-plugins.md#genie-directory) |

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
| [genie-plugin-marketplace](https://github.com/Claude-Code-Academy/genie-plugin-marketplace) | Themed skill bundles for Claude Code CLI, installable via `/plugin install`. | 🔒 Members |
| [genie-cowork-plugin-marketplace](https://github.com/Claude-Code-Academy/genie-cowork-plugin-marketplace) | The same idea for **Claude Cowork** (desktop knowledge-work mode). | 🔒 Members |
| [genie-curated-marketplace](https://github.com/Claude-Code-Academy/genie-curated-marketplace) | Vetted third-party plugins/skills/MCP servers, pinned to reviewed commits. | 🔒 Members |
| [genie-directory](https://github.com/Claude-Code-Academy/genie-directory) | Reference-only catalog — names, descriptions, when-to-use. No code. | 🔒 Members |

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
