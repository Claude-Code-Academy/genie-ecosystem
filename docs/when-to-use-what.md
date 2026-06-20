# When to use what

A decision guide for the Genie ecosystem. Start with the goal table, then read the head-to-head comparisons if you're torn between two options.

---

## "I want to…" → use this

| Goal | Use | Why |
|---|---|---|
| Use Claude as my **personal daily driver** — it knows me, remembers context, runs my routines | **genie-aios** | It's the OS layer: identity, memory, custom commands, your installed skills, an Obsidian vault. |
| Ship a **web app or SaaS** to production | **genie-web-os** | A full idea→Vercel pipeline (Next.js + Supabase + Stripe + Playwright), one skill per stage. |
| Ship a **mobile app** to TestFlight | **genie-mobile-os** | A full idea→TestFlight pipeline (Expo + RevenueCat), one skill per stage. |
| **Rebrand and sell** something already built | **genie-whitelabel** | Finished, working apps released white-label (typically MIT) — take, modify, ship as your own. |
| Add **one capability** to a vanilla Claude Code session | **genie-skills-library** | Copy a single self-contained skill folder; no plugin machinery, no OS needed. |
| Add **several related skills** in one command, auto-updating | **genie-plugin-marketplace** | Themed bundles installed via `/plugin install`, versioned and updatable. |
| Add skills inside **Claude Cowork** (desktop, chat-first) | **genie-cowork-plugin-marketplace** | Cowork is a different surface; these plugins suit the no-terminal flow. |
| Use **other people's** Claude Code tools, safely | **genie-curated-marketplace** | Vetted third-party plugins/skills/MCP, pinned to specific reviewed commits. |
| Just **find** the right skill/plugin by name | **genie-directory** | Reference-only catalog — descriptions and when-to-use, links to the real source. |

---

## OS vs OS: which Genie do I clone?

All three are "Genie," but they solve different jobs and **install differently**.

| | genie-aios | genie-web-os | genie-mobile-os |
|---|---|---|---|
| **Job** | Personal operating system | Build & ship web apps / SaaS | Build & ship mobile apps |
| **Output** | A daily driver you talk to | A SaaS live on Vercel | An app on TestFlight |
| **Install shape** | Clone *is* your workspace | Installs as a **global plugin**; you build in any folder | Installs as a **global plugin**; you build in any folder |
| **Skill namespace** | `<skill>` (in `.claude/skills/`) | `genie-web-os:<skill>` | `genie-mobile-os:<skill>` |
| **Key services (MCP)** | Whatever your skills need | Supabase, Stripe, Playwright, Context7 | RevenueCat |
| **Start phrase** | *"set up Genie for me"* / `/genie-init` | *"I have an idea for a SaaS…"* | *"I have an idea for an app…"* |

**Can I run more than one?** Yes. Web OS and Mobile OS namespace their skills (`genie-web-os:`, `genie-mobile-os:`) precisely so they never collide and are active in *every* project. genie-aios is your home base; the builder OSes are tools you reach for when it's time to ship.

**Rule of thumb:** Live in **genie-aios**. Add **genie-web-os** when you're building for the browser and **genie-mobile-os** when you're building for phones.

---

## Library vs marketplace: how should I install skills?

Same skills, different delivery.

| | genie-skills-library | genie-plugin-marketplace |
|---|---|---|
| **Unit** | One skill folder | A themed bundle of skills |
| **Install** | `cp -r skills/<name> ~/.claude/skills/` | `/plugin install <bundle>@genie` |
| **Updates** | Manual (`git pull` + re-copy) | `/plugin update` |
| **Best when** | You want exactly one skill, or to read/tweak the source | You want a use-case set in one shot, auto-updating |
| **Needs the OS?** | No | No |

> Both work in plain Claude Code — you don't need Genie installed. Inside a Genie repo, run `/genie-setup` after installing so credentials get wired into `.env.example`.

**CLI vs Cowork:** `genie-plugin-marketplace` is for the **Claude Code CLI**. If you're in **Claude Cowork** (Claude Desktop's knowledge-work mode), use `genie-cowork-plugin-marketplace` instead — same plugin format, tuned for the chat-first desktop flow.

---

## Our skills vs other people's

| | genie-plugin-marketplace / genie-skills-library | genie-curated-marketplace |
|---|---|---|
| **Authored by** | Claude Code Academy | Third parties (external authors) |
| **What you get** | Genie's own skills & bundles | Vetted external plugins/skills/MCP servers |
| **Safety model** | Maintained in-house | Pinned to a specific **reviewed commit SHA** — you only ever get commits CCA has reviewed |

Use the curated marketplace when you want the broader Claude Code community's tools but want someone to have vetted them first.

---

## Still unsure?

- Browse every skill and plugin by name in **[genie-directory](https://github.com/Claude-Code-Academy/genie-directory)** 🔒.
- Read the per-product deep dives in **[products.md](products.md)** and **[skills-and-plugins.md](skills-and-plugins.md)**.
- Ask in the **[community](https://www.skool.com/claude-code-academy)**.
