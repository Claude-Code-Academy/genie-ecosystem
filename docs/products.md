# Products

Deep dives on the four product repos: the personal OS, the two builder OSes, and the white-label catalog. Each section covers **what it is**, **when to use it**, and **how to start**.

> All four are **🔒 members-only**. [Join](https://www.skool.com/claude-code-academy) for access. **Windows:** use `python` instead of `python3`.

---

## genie-aios

**The core personal AI Operating System.** Genie gives Claude Code a persistent identity, memory, your preferences, and a skill library — so one clone becomes your daily driver, and the same template scales to a turnkey deployment for a paying client.

**Use it when** you want Claude to *be your OS*: greet you by name, remember decisions and learnings, run your routines, and reach for your installed skills — every session.

**What's in the box:**

- `CLAUDE.md` — the master instruction file Claude reads at the start of every session.
- `config.yaml` — the **one** file you edit to personalise Genie (name, role, timezone, comms style).
- `memory/` — structured memory read on session start: about-me, decisions, learnings, per-client and per-project files.
- `.claude/commands/` — custom slash commands (`/morning-startup`, `/end-of-day`, `/client-intake`, …).
- `.claude/skills/` — empty on clone; populated by the setup script and `install.py`.
- `vault/` — an Obsidian mount point; your notes live here and Claude reads them.
- `outputs/` — where Claude saves generated artefacts (gitignored).
- `deploy-for-client/` — setup guide, handoff checklist, and pricing guidance for client deployments.

**Set up in one command:**

```bash
gh repo clone Claude-Code-Academy/genie-aios && cd genie-aios && python3 init.py
```

`init.py` is idempotent and interactive — it registers the marketplaces, installs your profile's plugin bundles (default **member**; `--profile maintainer` adds internal tooling), scaffolds skill overlays, regenerates `.env.example`, and walks you through `config.yaml`. Useful flags: `--yes` (skip prompts), `--dry-run` (preview only). Then **restart Claude Code**, add keys to `.env`, and start talking. Prefer chat? Run `/genie-init`.

**Add more skills later:**

```bash
python3 install.py --list            # browse the catalog
python3 install.py skill-scanner     # install one (flat names, no category prefix)
```

Then run `/genie-setup` (or `python3 setup.py`) to scaffold its overlay and refresh `.env.example`.

**Personalise a skill — the overlay contract:** every installed skill gets a gitignored `PERSONAL.md` plus four frozen folders — `references/`, `assets/`, `examples/`, `snippets/`. Write your overrides in `PERSONAL.md`; your private customizations never touch the shared skill.

---

## genie-web-os

**Idea → SaaS → Vercel.** An opinionated Claude Code workspace that takes a web app from a raw idea to a live deployment, end-to-end.

**Use it when** you're building for the browser — a SaaS, a dashboard, a marketing site with auth and payments.

**The pipeline:**

```
idea → discussion → market research → spec → GitHub repo (spec = commit #1)
     → Next.js scaffold → Supabase + Stripe wiring → design system → Playwright E2E
     → Vercel preview → Vercel production
```

Each stage is owned by one skill; the orchestrator (`genie-app-builder`) chains them when you're ready to build, and never reimplements a stage — each skill stays authoritative for its domain.

**Quickstart:**

```bash
git clone git@github.com:Claude-Code-Academy/genie-web-os.git
cd genie-web-os
python3 init.py            # installs the Web OS as a GLOBAL plugin + registers MCP servers
#   python3 init.py --dry-run    # preview, change nothing
#   python3 init.py --skip-mcp   # plugin only
```

Add your keys to the generated `.env` (only the stages you'll hit — see `docs/env-setup-guide.md`), re-run `python3 init.py` to wire the MCP servers (**Supabase, Stripe, Playwright, Context7**), **restart Claude Code**, then from any folder: *"I have an idea for a SaaS…"*

Skills install globally as `genie-web-os:<skill>` (e.g. `genie-web-os:supabase`), so they're always available and never collide with another Genie OS. Tear it all down cleanly with `python3 uninstall.py` (or `/genie-uninstall`) — it leaves your `.env` and built apps untouched.

**Back-half skills:** `nextjs-web-setup` (Next.js 15 + TS + Tailwind + shadcn/ui), `design-system` (tokens, theming, page templates, screenshot-verified via Playwright), `supabase` (auth + Postgres + RLS + storage), `stripe` (checkout, portal, webhooks, subscriptions).

---

## genie-mobile-os

**Idea → mobile app → TestFlight.** The same shape as Web OS, pointed at native mobile.

**Use it when** you're building for phones and want to get to a TestFlight build without leaving the chat.

**The pipeline:**

```
idea → discussion → market research → PRD → Expo scaffold → EAS build → TestFlight
```

**Quickstart:**

```bash
git clone git@github.com:Claude-Code-Academy/genie-mobile-os.git
cd genie-mobile-os
python3 init.py            # installs the Mobile OS as a GLOBAL plugin + wires the RevenueCat MCP
```

Add keys to `.env`, re-run `python3 init.py`, **restart Claude Code**, then from any folder: *"I have an idea for an app…"* Skills install globally as `genie-mobile-os:<skill>`. Clean removal via `python3 uninstall.py` (or `/genie-uninstall`).

**Back-half skills:** `expo-mobile-setup` (Expo Router + NativeWind + Zustand + TanStack Query; app base cloned from the public [expo-revenuecat-claude-starter](https://github.com/Claude-Code-Academy/expo-revenuecat-claude-starter)), `supabase`, `revenuecat` (SDK, paywall, entitlements), `subscription-products` (programmatic IAP in App Store Connect + RevenueCat).

---

## genie-whitelabel

**Finished products, released white-label.** Not starter scaffolds — *real, working apps* the maintainer has built. Members take the code, rebrand it, modify it, and ship it as their own, under each project's own LICENSE (typically MIT).

**Use it when** you'd rather start from a complete product than build from scratch.

This repo is the **index only** — each project lives in its own `whitelabel-*` repo. To take one cleanly (no upstream link):

```bash
git clone git@github.com:Claude-Code-Academy/whitelabel-<name>.git my-product
cd my-product
rm -rf .git && git init -b main
git add . && git commit -m "Initial import from whitelabel-<name>"
git remote add origin <your-repo-url>
git push -u origin main
```

Then modify, rebrand, deploy, and sell. (Want to keep pulling upstream improvements instead? Just `gh repo clone` and skip the detach.) Always check the LICENSE in the specific project before assuming. *Note: the catalog is new — the first projects are on the way.*
