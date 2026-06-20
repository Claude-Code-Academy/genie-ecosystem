# Skills & plugins

How to add capabilities to Claude Code (and Cowork). Four delivery channels plus a reference catalog — all work in a vanilla session; **none require an OS to be installed**.

> All repos here are **🔒 members-only**. [Join](https://www.skool.com/claude-code-academy) for access.

**Quick primer:** a **skill** is a self-contained capability Claude loads when its trigger phrase appears. A **plugin / bundle** is a group of related skills installed together. A **marketplace** is a repo Claude Code can install plugins from. A **library** is a flat folder of skills you copy by hand.

---

## genie-skills-library

**The flat, copy-one-skill-at-a-time catalog.** Each skill is self-contained under `skills/<name>/`. Drop a folder into `~/.claude/skills/` (global) or `<project>/.claude/skills/` (project-scoped) and it works in any session — no plugin machinery.

**Manual install — one skill:**

```bash
git clone git@github.com:Claude-Code-Academy/genie-skills-library.git
cp -r genie-skills-library/skills/<skill-name> ~/.claude/skills/
# open a NEW Claude Code session — skills load at startup
```

**Everything at once:** `cp -r genie-skills-library/skills/* ~/.claude/skills/` — every folder is independent.
**Update:** `git pull`, then re-copy the skill(s) you use.
**Uninstall:** `rm -rf ~/.claude/skills/<skill-name>`.

**Or just ask Claude:** *"Install the `<skill>` skill from `Claude-Code-Academy/genie-skills-library` — clone to a temp folder, copy it into `~/.claude/skills/`, and tell me if it needs any API keys."*

**Use it when** you want exactly one skill, or you want to read/tweak the source before installing.

---

## genie-plugin-marketplace

**Themed bundles for the Claude Code CLI**, installed in one command and auto-updating. Skill content is identical to the library — the marketplace just ships them grouped, versioned, and updatable.

**Install a bundle** (inside Claude Code):

```
/plugin marketplace add Claude-Code-Academy/genie-plugin-marketplace
/plugin install content-creation@genie
```

Then **start a new session**. Update with `/plugin update content-creation` (or `/plugin update` for all). Remove with `/plugin uninstall content-creation`.

> Slash commands have to be typed by you — Claude can't fire `/plugin` on your behalf. But you can ask Claude to *print the exact commands* and help you fill in `.env` afterward.

**Available bundles:**

| Bundle | Skills |
|---|---|
| `content-creation` | `youtube-script`, `youtube-metadata`, `tiktok-metadata`, `instagram-reels-script`, `instagram-reels-metadata`, `transcript-cleanup`, `descript` |
| `coaching` | `coaching-plan`, `excalidraw` |
| `google-workspace` | `google-workspace-setup`, `md-to-gdoc` |
| `skill-authoring` | `skill-scanner`, `get-experience` |

Install as many as you want — no overlap, and a bundle only adds context for the skills it contains (progressive disclosure loads a skill's full body only when triggered).

**Use it when** you want a use-case set in one shot, kept up to date automatically.

---

## genie-cowork-plugin-marketplace

**The same idea, for Claude Cowork** (Claude Desktop's chat-first knowledge-work mode). Same plugin format, tuned for the no-terminal desktop flow (outputs folder, drag-and-drop, the Directory UI).

**Install:** register the marketplace once in the **Claude Code CLI** —

```
/plugin marketplace add Claude-Code-Academy/genie-cowork-plugin-marketplace
```

— then in **Cowork**: open **Directory → Plugins → Code**, click the **`genie-cowork`** chip, hit **+** on the plugin you want, and restart Cowork. *(First plugins are on the way.)*

**Use it when** you're working in Cowork rather than the CLI.

---

## genie-curated-marketplace

**Vetted third-party tools** — plugins, standalone skills, and MCP servers authored by *other people*, re-published with permission and attribution. Each entry is a pointer pinned to a specific **reviewed commit SHA**, not a re-hosted copy.

**The SHA pin is the contract:** when an upstream pushes new commits, you keep using the previously-reviewed commit until a maintainer re-vets and bumps the pin. No surprise updates. Members install **one** marketplace and get the whole curated set.

**Use it when** you want the broader community's tools but want them vetted first. Kept deliberately separate from `genie-plugin-marketplace` (which holds CCA's *own* skills).

---

## genie-directory

**Reference-only.** No code, no copies, no manifests — just names, descriptions, and "when to use it" notes so you can find the right thing fast and install it from its real home.

- **SKILLS.md** — every individual skill, what it does, where it lives.
- **PLUGINS.md** — every bundle and which skills it contains.
- **MARKETPLACES.md** — each marketplace and its install command.

**Use it when** you know you want *something* but need to look up the exact name or source.

---

## Setting credentials

Skills that need API keys ship an `env.example` showing exactly which keys.

1. **Vanilla Claude Code / Cowork (no Genie):** copy the keys you need into your project's `.env`, or export them in your shell. Skills read from the process environment.
2. **Inside a Genie repo:** run `python setup.py` (or `/genie-setup` mid-session). It scans every installed plugin's `env.example`, concatenates them into one labeled `.env.example` at the repo root, and seeds `.env`. Re-run after every install/update.

Always gitignore your `.env`.
