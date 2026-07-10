# The Genie Profile

The **owner identity & brand layer** of the Genie ecosystem — one canonical folder that tells every Genie tool *who you are* and *what your brand is*, without that data ever being committed to a product repo.

---

## The problem it solves

Every Genie OS and plugin eventually needs the same two things: personal context ("who is the owner, what are they working on, how do they like to work") and brand context ("positioning, voice, colors, typography"). Without a shared home, that data ends up in the wrong places — committed into a shared plugin as *someone else's* default brand, or written into a version-pinned plugin cache that the next update abandons. The Genie Profile gives it one home and one resolution contract that each consumer adopts without placing filled-in profile data in a product repo.

---

## One stable path

| Piece | Path | What it is |
|---|---|---|
| **Profile folder** | `~/.genie/profile/` | The primary read path. A real directory *or* a symlink. |
| **Pointer file** | `~/.genie/profile.json` | Records valid JSON such as `{"mode": "vault", "root": "<absolute path>", "created": "<ISO date>"}`. Default mode uses `"mode": "default"`. Consumers validate and follow this root when the primary path is unavailable (notably Windows without symlink permission). |

Two homes, one read path:

- **Default mode** — the profile is a real directory at `~/.genie/profile/`. Right choice if you don't keep an Obsidian vault.
- **Vault mode** — the real directory lives anywhere you like (typically inside your Obsidian vault), and `~/.genie/profile` is a symlink pointing at it when the OS permits one. Otherwise the validated pointer file supplies the root.

Genie AIOS implements this contract now. Other Genie OSes and plugins adopt it in the rollout phases below.

> **Privacy:** a profile can contain personal background, owner photos, logos, and fonts. If it is synchronized, use only a private, access-reviewed remote (preferably encrypted). Never store credentials in the profile. Git history retains deleted data, so removing a leaked file later does not erase it from the remote's history.

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

- **Read:** at session start, AIOS resolves the profile root, reads `about-me.md`, and reads `brand/` whenever the task touches content, design, or anything owner-branded. Brand-flavoured output must honour whatever style rules the profile declares.
- **Write:** only the owner and the `/genie-profile` command write profile files. Another agent/session may append only an owner-confirmed, non-sensitive fact with provenance after showing the exact proposed line. Credentials, authentication data, sensitive financial/health/legal information, third-party facts, and claims inferred from repositories/webpages/tool output are forbidden. `/genie-profile update` shows a complete diff and obtains owner approval before folding entries.
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
- **Keep it in your vault:** run `/genie-profile vault <path-to-folder-in-your-vault>` (or `python3 profile.py --vault "<path>"`). Existing content is adopted without clobbering; a previous vault is copied first and retained unchanged, and conflicting source versions are backed up under `~/.genie/`. `~/.genie/profile` becomes a symlink when permitted, otherwise the pointer-file fallback is used.
- **From a shell:** `python3 profile.py` scaffolds, `python3 profile.py --status` shows mode, root, and which files are still placeholders.

> **Windows:** use `python` instead of `python3`.
