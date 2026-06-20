# Workflows

End-to-end recipes that combine the pieces. Each one names the repos involved and the order to do things in.

> Most repos are **🔒 members-only**. **Windows:** use `python` instead of `python3`.

---

## Run your day with Genie

**Goal:** Claude as a personal OS that knows you and runs your routines.
**Repos:** `genie-aios` (+ skills from `genie-plugin-marketplace` / `genie-skills-library`).

1. `gh repo clone Claude-Code-Academy/genie-aios && cd genie-aios && python3 init.py`
2. Fill in `config.yaml` and `memory/about-me.md` (the script walks you through it).
3. Restart Claude Code, add any keys to `.env`, open the folder.
4. Day-to-day: run `/morning-startup`, work, capture notes in `vault/`, run `/end-of-day`.
5. Need a new capability? `python3 install.py <skill>` → `/genie-setup` → restart.

---

## Ship a SaaS from scratch

**Goal:** idea → live on Vercel.
**Repos:** `genie-web-os` (creates the app's own repo as it goes).

1. `git clone … genie-web-os && cd genie-web-os && python3 init.py`
2. Add keys to `.env` for the stages you'll hit (Supabase, Stripe), re-run `python3 init.py` to wire MCP, restart.
3. From any folder, say *"I have an idea for a SaaS…"* → idea brief.
4. *"research the market"* → market research. *"write the PRD"* → `spec.md`.
5. *"build the app"* → `genie-app-builder` creates the GitHub repo (spec = commit #1) and chains scaffold → Supabase → Stripe → design system → Playwright → Vercel.
6. Follow `docs/verification-report.md` for the smoke test before you invest heavily.

---

## Ship a mobile app from scratch

**Goal:** idea → TestFlight.
**Repos:** `genie-mobile-os` (app base from the public `expo-revenuecat-claude-starter`).

1. `git clone … genie-mobile-os && cd genie-mobile-os && python3 init.py`
2. Add keys to `.env`, re-run to wire the RevenueCat MCP, restart.
3. *"I have an idea for an app…"* → idea brief → market research → PRD.
4. *"build the app"* → scaffold (Expo) → Supabase (if cloud data) → RevenueCat (if paid) → EAS build → TestFlight.

---

## Add content-creation superpowers to any session

**Goal:** YouTube/TikTok/Reels scripts & metadata, transcript cleanup, Descript edits — no OS needed.
**Repos:** `genie-plugin-marketplace`.

```
/plugin marketplace add Claude-Code-Academy/genie-plugin-marketplace
/plugin install content-creation@genie
```

Start a new session, then trigger by phrase (e.g. *"write a YouTube script about…"*). Update with `/plugin update`.

---

## Deliver Genie to a paying client

**Goal:** stand up Genie for someone else as a service.
**Repos:** `genie-aios` (`deploy-for-client/`).

1. Set up genie-aios for the client with their `config.yaml` and memory.
2. Install the skills their workflow needs (`install.py` / plugin bundles).
3. Use the resources in `deploy-for-client/` — setup guide, handoff checklist, pricing guidance.
4. Hand off; they personalise skills via each skill's `PERSONAL.md` overlay.

---

## Start from a finished product instead of scratch

**Goal:** rebrand and sell something already built.
**Repos:** `genie-whitelabel` → a `whitelabel-*` project repo.

1. Browse the catalog in `genie-whitelabel`.
2. Clone the project, detach git, push to your own remote (see [products.md → genie-whitelabel](products.md#genie-whitelabel)).
3. Rebrand, modify, deploy, sell — under that project's LICENSE (typically MIT).

---

## Use a vetted third-party tool

**Goal:** install community tooling that's been reviewed.
**Repos:** `genie-curated-marketplace`.

Add the curated marketplace once, then install entries from it like any plugin. You only ever get the commit SHAs Claude Code Academy has reviewed — see [skills-and-plugins.md → genie-curated-marketplace](skills-and-plugins.md#genie-curated-marketplace).
