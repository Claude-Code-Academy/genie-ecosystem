# FAQ

Quick answers. For terms you don't recognise, see the [glossary](glossary.md).

---

### What *is* Genie, in one sentence?

A personal AI Operating System built on Claude Code — Claude with a persistent identity, memory, your preferences, and a library of skills, so one clone becomes a daily driver and the same template scales to a client deployment.

### What's the difference between this repo and `genie-directory`?

This repo (`genie-ecosystem`) is the **mother repo / map** — what each thing is, when to use it, how to use it, and how the pieces fit. `genie-directory` is the **catalog** — a flat, reference-only list of every individual skill and plugin by name. Use this to orient; use the directory to look something up.

### Why do most links 404 for me?

Almost everything is **🔒 members-only** — the links resolve only for members of the `Claude-Code-Academy` GitHub org. [Join the community](https://www.skool.com/claude-code-academy) and you'll be added. Only `genie-public-assets` and `expo-revenuecat-claude-starter` are public.

### Do I need to install Genie to use the skills?

No. Both the skills library and the plugin marketplaces work in a **vanilla Claude Code session**. Genie (the OS) adds memory, personalisation, and credential wiring on top — it's optional for skills.

### genie-aios vs genie-web-os vs genie-mobile-os — which do I clone?

- **genie-aios** = your personal daily OS.
- **genie-web-os** = build & ship web apps / SaaS.
- **genie-mobile-os** = build & ship mobile apps.

They install differently (aios is your workspace; the builders install as global plugins) and don't conflict. See [when-to-use-what.md](when-to-use-what.md#os-vs-os-which-genie-do-i-clone).

### Can I run more than one Genie OS at once?

Yes. The builder OSes namespace their skills (`genie-web-os:`, `genie-mobile-os:`) so they're active in every project and never collide. Live in genie-aios; reach for a builder when it's time to ship.

### Single skill or bundle — which way should I install?

Both come from the `genie` marketplace. **One skill:** `npx skills add Claude-Code-Academy/genie-plugin-marketplace --skill <name>` (needs Node) — installs it across every harness. **A whole use-case set:** `/plugin install <bundle>@genie`. See [when-to-use-what.md](when-to-use-what.md#single-skill-vs-bundle-how-should-i-install-skills).

### Do my Genie skills work in Codex / Gemini CLI / Cursor / Hermes too?

Yes. Installing a Genie plugin in Claude Code fans its skills out to `~/.agents/skills` (Codex, Cursor, OpenCode, Gemini CLI) and `~/.hermes/skills` (Hermes) — `init.py` does it automatically, and the `genie-add` skill keeps it in sync. Restart the other harness to pick up changes. See [skills-and-plugins.md](skills-and-plugins.md#install-once-use-everywhere).

### Why won't Claude run the `/plugin` commands for me?

`/plugin` slash commands have to be typed by **you** — Claude can't fire them on your behalf. Claude *can* print the exact commands and help you set up `.env` afterward.

### A skill I installed isn't triggering. Why?

Skills load at **session start**. Open a **new** Claude Code session after installing or copying one. Then trigger it with the phrase listed in its `SKILL.md`. For plugins, run `/plugin` to confirm it's installed and enabled.

### Where do API keys go?

Each skill ships an `env.example` listing the keys it needs. In a vanilla session, put them in your project's `.env` (or your shell). Inside a Genie repo, run `python setup.py` / `/genie-setup` to collect every installed skill's keys into one `.env.example`. Always gitignore `.env`.

### CLI vs Cowork — does it matter?

Yes. `genie-plugin-marketplace` targets the **Claude Code CLI** (and Claude Desktop's **Code tab**, which shares CLI installs automatically). **Cowork** is a separate Anthropic-managed store that does **not** share CLI installs — a known limitation. Use the Code tab, or install Cowork-specific plugins from `genie-cowork-plugin-marketplace`. The cross-harness sync can also surface skills to Cowork-side agents via `~/.agents/skills`.

### What does "white-label" mean here?

`genie-whitelabel` publishes finished, working apps you can take, rebrand, and sell as your own — under each project's LICENSE (typically MIT). Not starter templates — real products.

### Are these tools safe / where does third-party code come from?

Genie's own skills are maintained in-house. Third-party tools live in `genie-curated-marketplace`, where every entry is pinned to a specific **reviewed commit SHA** — you only get commits that have been vetted.

### I'm on Windows — anything different?

Use `python` instead of `python3` in every command. Everything else is the same.

### How do I get help or report something?

Ask in the **[Claude Code Academy community](https://www.skool.com/claude-code-academy)**. The org doesn't take external PRs back into product repos — fix things in your own copy, or raise it in the community.

### Who maintains all this?

Claude Code Academy. This repo is the front door; see [CONTRIBUTING.md](../CONTRIBUTING.md) for how it's kept current.
