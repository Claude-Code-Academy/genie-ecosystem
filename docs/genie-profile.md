# The Genie Profile

The **owner identity & brand layer** of the Genie ecosystem — one canonical folder that tells every Genie tool *who you are* and *what your brand is*, without that data ever being committed to a product repo.

---

## The problem it solves

Every Genie OS and plugin eventually needs the same two things: personal context ("who is the owner, what are they working on, how do they like to work") and brand context ("positioning, voice, colors, typography"). Without a shared home, that data ends up in the wrong places — committed into a shared plugin as *someone else's* default brand, or written into a version-pinned plugin cache that the next update abandons. The Genie Profile gives it one home that every tool reads and no product repo ever contains.

---

## One stable path

| Piece | Path | What it is |
|---|---|---|
| **Profile folder** | `~/.genie/profile/` | The ONLY path consumers read. A real directory *or* a symlink. |
| **Pointer file** | `~/.genie/profile.json` | Records `{"mode": "default"\|"vault", "root": "<abs path>", "created": "<ISO date>"}`. Fallback for resolving the root where symlinks aren't available (Windows). |

Two homes, one read path:

- **Default mode** — the profile is a real directory at `~/.genie/profile/`. Right choice if you don't keep an Obsidian vault.
- **Vault mode** — the real directory lives anywhere you like (typically inside your Obsidian vault, so Obsidian edits it and the vault's git sync backs it up and carries it across machines), and `~/.genie/profile` is a symlink pointing at it.

Either way, every Genie OS (aios / web-os / mobile-os) and every Genie plugin reads `~/.genie/profile/` — never the directory behind it.

---

## What's inside

Plain markdown + JSON, no machinery:

```
~/.genie/profile/
├── README.md          # what this is, ownership rules, how agents read/write it
├── about-me.md        # role, current focus, how you work best, values, what to avoid, background
├── brand/
│   ├── identity.md    # positioning, audience, pillars, voice & tone, CTA, exclusions
│   ├── visual.md      # colors, typography, logo & imagery rules, per-platform notes
│   ├── palette.json   # machine-readable brand tokens for any skill that renders visuals
│   └── assets/        # logos, fonts, owner photos
└── evolution.md       # append-only learned-facts log (dated bullets)
```

---

## How agents use it

- **Read:** at session start, agents read `about-me.md`; they read `brand/` whenever the task touches content, design, or anything owner-branded. Brand-flavoured output must honour whatever style rules the profile declares.
- **Write:** only the owner and the `/genie-profile` command write profile files. Every *other* agent or session may append (only) to `evolution.md` — one dated bullet per durable fact it learns about the owner. `/genie-profile update` folds those entries into the right files.
- **Never committed:** product repos ship only generic templates with placeholders. The filled-in profile never travels into any repo, and `/genie-uninstall` never deletes it — the profile outlives any OS clone.

---

## Adoption status

| Where | Status | What it means there |
|---|---|---|
| **genie-aios** | **Shipped** (v1, 2026-07-10) | Ships the templates, the `profile.py` scaffolder/linker, and the `/genie-profile` command; reads the profile at the start of every session. |
| **content-os** (plugin) | Planned — P2 | Brand loading will prefer `~/.genie/profile/brand/` over the plugin's bundled brand file; `create-brand-assets` will write to the profile. |
| **genie-web-os** | Planned — P3 | Reads the profile at session start. |
| **genie-mobile-os** | Planned — P3 | Reads the profile at session start. |

The full design and phased plan live in genie-aios's `PRD.md` (🔒 members-only).

---

## Set yours up

From your **genie-aios** clone (🔒 members-only — see [products.md](products.md)):

- **In chat:** run `/genie-profile`. It scaffolds `~/.genie/profile/` if it's missing, then interviews you section by section (about-me, brand identity, colors & typography — it can work from your website or Instagram handle) and writes your answers in.
- **Keep it in your vault:** run `/genie-profile vault <path-to-folder-in-your-vault>` (or `python3 profile.py --vault "<path>"`). Existing content is adopted, never overwritten, and `~/.genie/profile` becomes a symlink to it.
- **From a shell:** `python3 profile.py` scaffolds, `python3 profile.py --status` shows mode, root, and which files are still placeholders.

> **Windows:** use `python` instead of `python3`.
