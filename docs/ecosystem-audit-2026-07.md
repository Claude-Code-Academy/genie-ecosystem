# Genie ecosystem audit — 2026-07-02

> Internal working doc (not member-facing). Full-ecosystem investigation: every repo in
> `Claude-Code-Academy` + the local machine state. Ordered by severity; each item names
> the exact file to fix. Companion to the new one-command `install.py` / `uninstall.py`
> at the root of this repo.

## The picture

**16 org repos** + 2 personal (`amirthan/genie-agent-queue`, `amirthan/genie-coach`) + 1 local-only
(`~/genie-task-manager`, no remote). Three layers:

```
ENTRY      genie-ecosystem (public map) ──> install.py / uninstall.py  ← NEW, one command each
OSes       genie-aios · genie-web-os · genie-mobile-os        (clone + python3 init.py each)
CONTENT    genie-skills-library (source of truth, 23 skills)
             └─ publish → genie-plugin-marketplace "genie"      7 first-party plugins
           genie-curated-marketplace "genie-curated"            0 plugins (pipeline built, unused)
           genie-cowork-plugin-marketplace "genie-cowork"       0 plugins
           genie-internal-plugins "genie-internal"              2 maintainer-only plugins
REFERENCE  genie-directory (hand-maintained, drifting) · genie-internal-skills (backup)
KITS       genie-second-brain · genie-task-manager (+ private data: genie-agent-queue)
```

What already works well: per-OS `init.py` is idempotent, manifest-based
(`~/.claude/genie/<os>-install.json`), and `uninstall.py` (byte-identical in all 3 OS repos)
reverses exactly what was recorded while preserving `.env`/overlays/projects.

## Flaws found

### Broken / high

1. **`content-creation@genie` no longer exists** — renamed to `content-os`, rename never propagated.
   A fresh member install failed on its main content bundle.
   - `genie-aios/init-profiles.json` + `init.py` FALLBACK_MANIFEST → **FIXED 2026-07-02** (all profiles now `content-os@genie`)
   - `genie-plugin-marketplace/plugins/content-creation/` — dead folder still in the repo (not in marketplace.json); delete
   - `genie-plugin-marketplace/README.md` — install example still says `content-creation@genie`
   - `genie-directory/PLUGINS.md` — still documents content-creation
2. **No ecosystem-level install/uninstall existed** — only per-OS. → **Drafted 2026-07-02**:
   `install.py` / `uninstall.py` in this repo (thin orchestrators over the per-OS scripts; ecosystem
   manifest at `~/.claude/genie/ecosystem.json` — deliberately NOT `*-install.json`, which the per-OS
   uninstaller globs). Hardened same day via a 27-agent adversarial review (24 confirmed findings
   fixed: manifest-glob collision, purge restricted to recorded clones + user-data/--force guard,
   non-tty confirmation, partial-clone detection, clone-recorded-even-if-init-fails, Windows
   ANSI/Unicode/read-only-.git handling, GITHUB_TOKEN preflight warning).
3. **MCP drift trap** (web/mobile): `scripts/setup_mcp.py` vs `init-profiles.json → mcp_servers` must be
   hand-synced or uninstall orphans MCP servers. CLAUDE.md itself calls it "the easiest one to forget".
   Add a CI check or have setup_mcp.py read the list from init-profiles.json.
4. **Never dogfooded**: this machine has no `~/.claude/genie/` manifests — plugins here were installed
   manually, `init.py` never fully run even by the maintainer. Broken refs (flaw 1) went unnoticed for
   weeks. Run the real install on a clean account/VM per release.

### Structural / medium

5. **Installer code duplicated by convention, guarded only by md5-by-hand**: `init.py` (web=mobile),
   `uninstall.py` (all 3). And the claim in `genie-aios/CLAUDE.md` that *install.py* is shared across
   all three is false — web/mobile don't ship it. Either fix the doc or vendor via a sync script + CI.
6. **Profile manifest duplicated inside code**: `init-profiles.json` AND `FALLBACK_MANIFEST` in
   `genie-aios/init.py` — every plugin change is a two-place edit (this is exactly where flaw 1 hid).
   Consider dropping the fallback or generating it at release time.
7. **Two empty member-facing marketplaces registered by default** (`genie-curated`, `genie-cowork`).
   Members get marketplaces with zero plugins — looks broken. Don't register them in the member
   profile until they have ≥1 plugin (the curation pipeline in genie-curated is complete: checklist,
   SHA-pin contract, validator, tags `verified` / `reviewed-YYYY-MM` / `client-deploy:*` — just unused).
8. **Trust tiers exist but are invisible**: nothing member-facing explains first-party (`genie`) vs
   curated/verified (`genie-curated`) vs maintainer-only (`genie-internal`). One TRUST.md here (or a
   section in skills-and-plugins.md) + a `tier` line per marketplace README would close it.
9. **genie-directory is hand-maintained and already wrong**: says 14 library skills (real: 23) and
   4 plugins (its own PLUGINS.md lists 6; real: 7). SKILLS.md misses elevenlabs-voice,
   obs-descript-elevenlabs, report-issue. Generate it from the sources in the `_publish-skills` flow
   instead of editing by hand; same for the skills-library README table (lists 16 of 23).
10. **genie-task-manager has no git remote** and 6 uncommitted files (the whole Linear bridge:
    `bin/linear-bridge.sh` + hooks in metis/dispatcher/install). One crash loses the feature.
    Commit, create `Claude-Code-Academy/genie-task-manager` (or personal), push. Note: it's all
    `.sh` — house rule says Python; decide before publishing to members.
11. **GITHUB_TOKEN silent failure**: background marketplace auto-update needs `GITHUB_TOKEN` exported;
    if absent it fails silently. Preflight-check it in init.py/install.py and say so.

### Cruft / low

12. `~/plugins/` — empty stray dir in home; delete or document.
13. `genie-coach` sits on branch `codex/implementation-ready-plan` with `main` behind it; merge or
    document the branch strategy. Also unreferenced by the rest of the ecosystem — decide in/out.
14. Versioning is cosmetic: plugin.json versions (0.0.1–0.3.0) never surface anywhere; no changelog;
    update story ("git pull + re-run init.py") undocumented. Document `/plugin update` + bump-on-release.
    > **2026-07-12 status: addressed.** genie-aios ships `VERSION` + `update.py` / `/genie-update`
    > (fetch, fast-forward pull, re-run setup); the update story (repo update vs `/plugin update` for
    > bundles) is now documented in this repo's README, `docs/getting-started.md`, and `docs/faq.md`.
15. Two things named "second-brain" (marketplace plugin = skills; `genie-second-brain` repo = sync
    kit + course companion). Intentional, but say so in both READMEs to kill the ambiguity.
    > **2026-07-12 status: addressed.** README's repo map and `docs/skills-and-plugins.md` now each
    > carry a one-line disambiguation next to the `second-brain` plugin and the `genie-second-brain`
    > repo. (Following up in the product repos' own READMEs is still open.)
16. Plaintext `.env` secrets — already on `genie-aios/ROADMAP.md` (age/SOPS or Infisical), still open.

## Target architecture (the contract)

- **One front door**: genie-ecosystem = map + `install.py` + `uninstall.py`. Everything else reachable
  from here in ≤2 clicks. Per-OS `init.py` stays the only place with real install logic.
- **One source of truth per artifact**: skills → genie-skills-library; bundles → generated copies in
  genie-plugin-marketplace; catalog (genie-directory) → generated, never hand-edited; profile lists →
  `init-profiles.json` only.
- **Three visible trust tiers**: `genie` (first-party, CCA-authored) → `genie-curated` (third-party,
  SHA-pinned, reviewed, tagged) → everything else (discovery-only via CURATED-SKILLS.md, install at
  your own risk). `genie-internal` stays maintainer-only and out of member docs.
- **Marketplaces register only when non-empty**; plugins install à la carte via `/plugin install`.
- **Every release dogfooded**: clean-machine `install.py --all --yes --dry-run` + real run in CI or a
  throwaway account before announcing.

## Out-of-box credential chain + cross-surface trace (added 2026-07-02, second pass)

Promised UX: install → copy `.env.example` → fill keys → skills work, on CLI / Desktop / Codex / Hermes.
Traced end-to-end by 4 parallel investigators. Verdict: **was broken at 4 links; now fixed at 3 of them.**

**Fixed (verify, commit, publish):**
- `genie-aios/setup.py` scanned ONLY `cache/genie` and ONLY skill-level `env.example` → most content-os
  keys (REPLICATE_API_TOKEN, OPENAI_API_KEY, APIFY_API_TOKEN…) could never reach a member's
  `.env.example`. → Now scans every marketplace + plugin-root master catalogs, dedupes keys, APPENDS
  new keys to an existing `.env` after plugin updates, adds `--check` doctor mode, and links
  `~/.claude/genie/.env` → genie-root `.env`. Live-tested here: 34 keys aggregated, doctor works.
- Runtime `.env` discovery only walked up from cwd (breaks in any random project folder; competitor-intel
  had NO loader at all; auto_capture_run.sh's GENIE_ROOT resolves to the marketplace clone). → All four
  loaders (blotato.py, render.mjs, apify_intel.py, auto_capture_run.sh) now fall back to the user-level
  `~/.claude/genie/.env`. Edited in the content-os working repo (marketplace clone, branch
  add-content-os-plugin, uncommitted).
- 3 content-os skills used keys with no skill-level `env.example` (instagram-carousel, competitor-intel,
  auto-capture) → files added. NOTE: instagram-carousel's AI covers use Replicate (Google Imagen 4) with
  OpenAI fallback; NANO_BANANA/GEMINI keys in the catalog are future placeholders no code reads.
- `genie-web-os/.env.example` was missing SUPABASE_PERSONAL_ACCESS_TOKEN (its own Supabase MCP needs it;
  the docs guide already documented it) → added.
- Cross-surface: Codex (`~/.codex/skills/`) and Hermes (`~/.hermes/skills/`) natively consume the same
  SKILL.md format → new `export-skills.py` in this repo copies installed Genie skills to both (marker-file
  guarded). Ran here: 27 skills exported to each. Claude Desktop needs nothing — it shares ~/.claude/plugins.

**Closed same day (third pass — committed locally, 6181b62 on add-content-os-plugin):**
- 7 script-backed skills rewritten from `${CLAUDE_PLUGIN_ROOT}` to the portable `${SKILL_DIR}`
  convention (definition line at the top of each SKILL.md maps it per agent) — verified in the
  refreshed cache and in the exported Codex/Hermes copies.
- `genie-setup-lite` skill added to genie-essentials 0.1.0 — vanilla/Desktop/Codex/Hermes users
  aggregate every installed plugin's keys into `~/.claude/genie/.env{,.example}` with a `--check`
  doctor; tested (30 keys).
- genie marketplace README credentials section rewritten around `~/.claude/genie/.env` +
  genie-setup-lite; stale `content-creation` install examples fixed; deprecated
  `plugins/content-creation/` bundle removed. Cowork README fix committed in the audit clone and
  exported as `genie-ecosystem/patches/0001-*.patch` (apply with `git am`).
- content-os bumped 0.1.0 → 0.2.0, local cache updated via the real member flow
  (`claude plugin update content-os@genie`), genie-aios `.env.example` regenerated (7 sections),
  all 29 skills re-exported to `~/.codex/skills/` + `~/.hermes/skills/` with zero warnings.

**Remaining (needs the owner):** `git push` the add-content-os-plugin branch (+ merge to main) so
members receive 0.2.0; then they run `/plugin update content-os` + `/genie-setup` (or
genie-setup-lite). Longer-term: commands/agents/hooks don't port to Codex/Hermes (only skills do);
keep skill descriptions <1024 chars for claude.ai.

## Runbook (suggested order)

1. Review + commit the drafts in this repo (`install.py`, `uninstall.py`, README/getting-started edits).
2. Commit the genie-aios fix (content-os + second-brain profile changes already in the working tree).
3. genie-plugin-marketplace: delete `plugins/content-creation/`, fix README example, bump.
4. Regenerate/fix genie-directory + skills-library README counts (then automate in `_publish-skills`).
5. Push genie-task-manager (commit Linear bridge or stash it; add remote).
6. Stop registering empty marketplaces in member profile (edit `init-profiles.json` marketplaces list),
   or seed genie-curated with its first 1–2 vetted plugins.
7. Add TRUST.md / trust-tier section + document the update flow (`/plugin update`, git pull, re-init).
8. Delete `~/plugins/`; settle genie-coach branch.
