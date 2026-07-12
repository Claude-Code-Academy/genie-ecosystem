# Skills & plugins

How to add capabilities to Claude Code — and have them follow you into every other AI harness on the machine. Everything here works in a **vanilla Claude Code session**; none of it requires an OS to be installed.

> Repos here are **🔒 members-only**. [Join](https://www.skool.com/claude-code-academy) for access.

**Quick primer:** a **skill** is a self-contained capability (`SKILL.md` + supporting files) Claude loads when its trigger phrase appears. A **plugin** is a group of related skills installed together. A **marketplace** is a repo Claude Code installs plugins from.

The Genie marketplaces (`init.py` registers `genie` + `genie-curated` + `genie-cowork` for members; `genie-internal` is added only with `--profile maintainer`):

| Marketplace | What's in it |
|---|---|
| **`genie`** | 9 first-party plugins authored by Claude Code Academy. Home: [genie-plugin-marketplace](https://github.com/Claude-Code-Academy/genie-plugin-marketplace). |
| **`genie-curated`** | Vetted third-party plugins/skills/MCP servers, each SHA-pinned. Home: [genie-curated-marketplace](https://github.com/Claude-Code-Academy/genie-curated-marketplace). **Live.** |
| **`genie-internal`** | Maintainer-only admin tooling (not registered for members). Home: [genie-internal-plugins](https://github.com/Claude-Code-Academy/genie-internal-plugins). |
| **`genie-cowork`** | Plugins packaged for Claude Cowork — see [below](#genie-cowork-plugin-marketplace). Home: [genie-cowork-plugin-marketplace](https://github.com/Claude-Code-Academy/genie-cowork-plugin-marketplace). |

Anthropic's own official marketplace complements these.

---

## genie-plugin-marketplace — the `genie` bundles

**Themed bundles for Claude Code**, installed in one command and auto-updating. Two moves: **(1) add the marketplace once, then (2) install the bundle.** The marketplace name is `genie`.

### In the terminal (Claude Code CLI)

```
/plugin marketplace add Claude-Code-Academy/genie-plugin-marketplace
/plugin install genie-essentials@genie
```

Or run `/plugin` (note: **singular**) to open the plugin manager — tabs **Discover · Installed · Marketplaces · Errors** (move with `Tab` / `Shift+Tab`): add the marketplace under **Marketplaces**, install from **Discover**, then run **`/reload-plugins`** (or start a new session) to activate.

### In the Claude Code desktop app (Code tab)

Same thing via GUI: click the **`+`** next to the prompt box → **Plugins** → **Add plugin**, add `Claude-Code-Academy/genie-plugin-marketplace`, find the bundle, install. Use **Manage plugins** to enable/disable/uninstall.

> The `+` → **Plugins** option appears in **local and SSH sessions only**, not cloud sessions.

### Manage & update

`/plugin update <bundle>` (or `/plugin update` for all), `/plugin uninstall <bundle>`, `/plugin list`, `/plugin marketplace list`.

> Slash commands must be typed by **you** — Claude can't fire `/plugin` on your behalf. But it can print the exact commands and help you fill in `.env` after.

> **This updates the bundle, not Genie itself.** If you're inside a Genie OS clone (genie-aios etc.), `/plugin update` refreshes the *plugins* only — the repo (config, memory, `init.py`/`setup.py` logic) updates separately via `python3 update.py` (or `/genie-update`). See the README's "Keep it updated" section.

### The 9 bundles

| Bundle | What it does |
|---|---|
| `genie-essentials` | Baseline utilities every member should have: `genie-find-skills`, `genie-goalify` (ramble → one paste-ready goal), `genie-setup-lite` (wire API keys), and `genie-add` (install a plugin **and** sync it to every harness). |
| `content-os` | The content plugin: turns moments captured in your Content OS vault into on-brand IG posts, carousels, reel scripts, LinkedIn/X posts & threads, YouTube/TikTok scripts & metadata, and repurpose packs — with Descript editing, Blotato publishing, and a competitor-intel + web-scan loop. |
| `coaching` | 1-to-1 Claude Code coaching plans and Excalidraw diagrams. |
| `google-workspace` | Google Drive/Docs auth setup and Markdown → Google Doc conversion. |
| `skill-authoring` | Meta-tools for building and sanitizing your own Claude Code skills. |
| `second-brain` | Create and maintain a self-maintaining Obsidian knowledge vault an AI agent keeps current. **Not the same thing as the standalone [genie-second-brain](https://github.com/Claude-Code-Academy/genie-second-brain) repo** — that repo is the Git-sync kit + Second Brain course companion; this plugin is the skills that create/maintain the vault from inside Claude Code. |
| `skool-os` | Skool community owner toolkit: study winning Skool communities, distill what works on the cover + About page, build your own cover image + About page + positioning, then monitor competitors and your own page on a cadence so the loop never goes stale. |
| `ios-app-pipeline` | Verified iOS app pipeline: Xcode setup, Simulator runtime repair, SwiftUI smoke-test build, install/launch, and screenshot proof. |
| `website-analytics` | Behaviour analytics for any site via Microsoft Clarity: bundles Clarity's official MCP plus `clarity-connect` (install + verify the tag) and `clarity-insights` (query funnel drop-off / what to fix). |

Install as many as you want — no overlap, and a bundle only adds context for the skills it contains (progressive disclosure loads a skill's full body only when triggered).

---

## Install once, use everywhere

Installing a `genie` plugin in Claude Code also makes its skills available in **Codex** (CLI, desktop app, IDE — one shared `~/.codex`), **Gemini CLI**, **Cursor**, **OpenCode**, and **Hermes** — without reinstalling per tool. This is done by `genie_sync.py`, the engine behind the **`genie-add`** skill in `genie-essentials`:

- Skills fan out to **`~/.agents/skills`** (the open [agentskills.io](https://agentskills.io) directory, scanned by Codex/Cursor/OpenCode) and **`~/.hermes/skills`**, each stamped with a `.genie-export.json` provenance marker so a sync never touches a skill you wrote by hand.
- Plugins that bundle an **MCP server** additionally register as real Codex plugins (a local marketplace at `~/.genie/codex-marketplace` + `codex plugin add`).
- **Restart the other harness** (Codex / a fresh Hermes session) to pick up changes. Claude Code already has them.

**Lifecycle — when sync runs:**

| Event | What happens |
|---|---|
| Fresh clone (`init.py` / `/genie-init`) | Runs `genie_sync.py --all --prune` as its last step (8/8) — best-effort: needs `genie-essentials@genie` installed, prints a hint if skipped. |
| Add a plugin | `/genie-add <plugin>` wraps install **and** sync in one move. |
| Uninstall a plugin | `uninstall.py` runs sync `--all --prune`, removing orphaned exported copies. |
| After `/plugin update` | Re-run the sync for that plugin (`/genie-add` or `genie_sync.py --plugin <name>@genie`). |

**Claude Desktop:** the **Code tab** shares your CLI installs automatically. **Cowork does not** — it's a separate Anthropic-managed store (a known limitation). Use the Code tab; the cross-harness sync can also feed Cowork-side agents via `~/.agents/skills`.

**Credentials once:** every Genie skill checks the current folder's `.env` (walking up), then falls back to `~/.claude/genie/.env`. Fill that one file and skills work from any folder and any surface.

---

## Per-skill install (just one skill)

Want a single skill, not a whole bundle — or you're a non-genie harness user? Use the `skills` CLI (**requires Node**):

```bash
npx skills add Claude-Code-Academy/genie-plugin-marketplace --skill <skill-name>
```

It installs that one skill across every detected harness via `~/.agents/skills` symlinks. If `command -v node` prints nothing, install the plugin bundle instead (no Node needed).

> The flat [genie-skills-library](https://github.com/Claude-Code-Academy/genie-skills-library) repo remains the internal source of truth for skill content. Members don't need to clone it — the `npx skills` path above (or a bundle install) is the supported way in. Clone it only if you want to read or tweak a skill's source.

---

## genie-curated-marketplace — vetted third-party tools

**Live.** Plugins, standalone skills, and MCP servers authored by *other people*, re-published by reference with attribution — currently ~a dozen entries (e.g. `mattpocock-skills`, `paper-search`, `mermaid`, `kanban`, `cloudflare-api`). Each entry is a pointer pinned to a specific **reviewed commit SHA**, not a re-hosted copy.

```
/plugin marketplace add Claude-Code-Academy/genie-curated-marketplace
/plugin install <plugin>@genie-curated
```

**The SHA pin is the contract:** when an upstream pushes new commits, you keep the previously-reviewed commit until a maintainer re-vets and bumps the pin. No surprise updates. Kept deliberately separate from `genie-plugin-marketplace` (which holds CCA's *own* skills). Full curation rules live in that repo's `CLAUDE.md` / `README.md`.

---

## genie-cowork-plugin-marketplace

The same idea, packaged for **Claude Cowork** (the chat-first desktop mode that does not share CLI installs). Register once in the CLI —

```
/plugin marketplace add Claude-Code-Academy/genie-cowork-plugin-marketplace
```

— then in **Cowork**: **Directory → Plugins → Code**, click the **`genie-cowork`** chip, hit **+** on the plugin you want, and restart Cowork. *(Catalog is filling in; for CLI/Code-tab work the `genie` marketplace above is the primary path.)*

---

## Setting credentials

Skills that need API keys ship an `env.example` naming the keys.

1. **Vanilla Claude Code / Cowork (no Genie):** install `genie-essentials@genie` and say *"set up my keys"* (the `genie-setup-lite` skill) — it aggregates every installed plugin's declared keys into `~/.claude/genie/.env.example`, seeds `~/.claude/genie/.env`, and `--check` shows what's still missing.
2. **Inside a Genie repo:** run `/genie-setup` (`python setup.py`). Same aggregation into the repo-root `.env`, plus personal overlays, and it links `~/.claude/genie/.env` to the repo's `.env` so both stay one file. Re-run after every install/update.

Always gitignore your `.env`.
