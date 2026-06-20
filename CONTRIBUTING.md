# Contributing & maintenance

This repo is the **map** of the Genie ecosystem — it holds no product code. Its only job is to stay accurate as the rest of the ecosystem changes.

## For members

This is a documentation hub, not a product. The org doesn't accept external PRs into its product repos — if something here is wrong, out of date, or confusing, raise it in the **[Claude Code Academy community](https://www.skool.com/claude-code-academy)** and it'll get fixed.

## For maintainers — keeping the map current

Update this repo whenever the ecosystem shape changes:

- **A repo is added, renamed, or archived** → update the repo tables in [README.md](README.md) and any affected doc.
- **A product's setup command or pipeline changes** → update [docs/products.md](docs/products.md), [docs/getting-started.md](docs/getting-started.md), and [docs/workflows.md](docs/workflows.md).
- **A marketplace bundle is added/removed** → update the bundle table in [docs/skills-and-plugins.md](docs/skills-and-plugins.md). (Per-skill detail lives in `genie-directory`, not here — link, don't duplicate.)
- **A new term enters circulation** → add it to [docs/glossary.md](docs/glossary.md).

### Guardrails

- **Public repo.** Keep secrets, tokens, and sensitive maintainer-only workflows out. Describe member-facing capability; don't document internal plumbing.
- **Link, don't copy.** This repo points at canonical sources. The detailed per-skill catalog is `genie-directory`'s job; product internals live in each product repo. Avoid duplicating content that will drift.
- **Mark access honestly.** Tag members-only repos with 🔒 so public readers aren't surprised by 404s.
- **Keep commands real.** Quote setup commands from the source repo's actual README so they don't rot.
