# Getting started

The shortest path from zero to a working Genie setup. Pick the entry point that matches what you're trying to do — you do **not** need to install everything.

> **Want it all in one command?** Clone this repo and run the ecosystem installer — it clones the OSes you pick and runs each one's own setup:
>
> ```bash
> gh repo clone Claude-Code-Academy/genie-ecosystem && cd genie-ecosystem && python3 install.py
> ```
>
> The exact reverse is `python3 uninstall.py` (add `--purge` to delete the clones too). Everything below still works standalone if you'd rather install just one piece.

> **Most repos here are 🔒 members-only.** If a `git clone` or `gh repo clone` fails with "repository not found," you're not yet a member of the `Claude-Code-Academy` org. [Join the community](https://www.skool.com/claude-code-academy) and you'll be added.

---

## Step 0 — Prerequisites

You'll want these on your machine first:

- **[Claude Code](https://docs.claude.com/en/docs/claude-code)** — the CLI everything runs on.
- **Git** and the **[GitHub CLI](https://cli.github.com/)** (`gh`) — for cloning the private repos. Run `gh auth login` once.
- **Python 3** — the OS repos use a `python3 init.py` setup script. (**Windows:** use `python` instead of `python3` everywhere below.)

---

## Step 1 — Pick your entry point

```
Do you want to…

  ├─ Use Claude as your personal daily OS ........... → genie-aios       (A)
  ├─ Build & ship a web app / SaaS ................. → genie-web-os      (B)
  ├─ Build & ship a mobile app .................... → genie-mobile-os   (C)
  └─ Just add a skill or two to plain Claude Code .. → skills & plugins  (D)
```

Not sure? Read **[when-to-use-what.md](when-to-use-what.md)**.

---

## (A) genie-aios — your personal AI Operating System

One clone, one command:

```bash
gh repo clone Claude-Code-Academy/genie-aios && cd genie-aios && python3 init.py
```

`init.py` is interactive and idempotent. It registers the Genie plugin marketplaces, installs the plugin bundles for your profile (default **member**), scaffolds your skill overlays, generates `.env.example`, and walks you through `config.yaml` + `memory/about-me.md`.

Then:

1. **Restart Claude Code** so the freshly installed plugins load.
2. Drop any required API keys into `.env`.
3. Open the folder in Claude Code and just start talking — it greets you by name and you're working.

Prefer to drive it from chat? Clone, open in Claude Code, and run `/genie-init` (or say *"set up Genie for me"*).

➡️ Full walkthrough: [products.md → genie-aios](products.md#genie-aios)

---

## (B) genie-web-os — idea → SaaS → Vercel

```bash
git clone git@github.com:Claude-Code-Academy/genie-web-os.git
cd genie-web-os
python3 init.py            # installs the Web OS as a global plugin + wires MCP servers
```

Add your keys to the generated `.env`, re-run `python3 init.py` to wire the MCP servers (Supabase, Stripe, Playwright, Context7), **restart Claude Code**, then from *any* folder say:

> *"I have an idea for a SaaS…"*

➡️ Full walkthrough: [products.md → genie-web-os](products.md#genie-web-os)

---

## (C) genie-mobile-os — idea → mobile app → TestFlight

```bash
git clone git@github.com:Claude-Code-Academy/genie-mobile-os.git
cd genie-mobile-os
python3 init.py            # installs the Mobile OS as a global plugin + wires the RevenueCat MCP
```

Add your keys to `.env`, re-run `python3 init.py`, **restart Claude Code**, then from any folder:

> *"I have an idea for an app…"*

➡️ Full walkthrough: [products.md → genie-mobile-os](products.md#genie-mobile-os)

---

## (D) Just add skills to plain Claude Code

No OS required. Two ways:

**One specific skill** — from [genie-skills-library](https://github.com/Claude-Code-Academy/genie-skills-library):

```bash
git clone git@github.com:Claude-Code-Academy/genie-skills-library.git
cp -r genie-skills-library/skills/<skill-name> ~/.claude/skills/
# start a new Claude Code session
```

**A themed bundle** — from [genie-plugin-marketplace](https://github.com/Claude-Code-Academy/genie-plugin-marketplace), inside Claude Code:

```
/plugin marketplace add Claude-Code-Academy/genie-plugin-marketplace
/plugin install content-os@genie
```

Then start a new session. ➡️ Full details: [skills-and-plugins.md](skills-and-plugins.md)

---

## Step 2 — Verify it works

- **OS repos:** on your first end-to-end run, follow the smoke-test checklist in each repo's `docs/verification-report.md`.
- **Skills:** open a *new* Claude Code session (skills load at startup) and trigger the skill by its phrase.
- **Plugins:** run `/plugin` to confirm the bundle is installed and enabled.

Stuck? See the **[FAQ](faq.md)**.
