# Composio connections (the "connect an external tool" pattern)

How Genie skills read and act on your external accounts — Instagram, Gmail, Slack, Notion, and 1000+ others — through [Composio](https://composio.dev), which brokers the OAuth and exposes each app as callable tools.

This is the ecosystem's standard answer to *"let an agent use my accounts"*: connect once, and any skill that needs that account works. It lives in the **`content-os`** plugin as two skills:

- **`composio-connect`** — the plug-and-play onboarding primitive. Installs the Composio CLI, logs you in, links a toolkit (browser OAuth), verifies. Toolkit-agnostic.
- **`instagram-dms`** — the first capability that uses it: read and triage your Instagram DMs (full inbox, or just the threads awaiting a reply). Read-only.

Both ship automatically with `content-os@genie` — no separate install. Just `/plugin install content-os@genie` (or `claude plugin update`), then say *"connect my instagram"* or *"check my instagram DMs"*.

## Two credentials, two jobs — which to set up

Composio can be reached two ways. Pick by what the skill needs:

| Path | Auth | Best for | Set up with |
|------|------|----------|-------------|
| **CLI** (recommended) | `composio login` browser token — **no API key** | read/act skills (`instagram-dms`); the easiest, most plug-and-play path | `composio-connect` |
| **REST API** | `COMPOSIO_API_KEY` in `~/.claude/genie/.env` | headless/async flows (`composio-publish`) | that skill's `doctor` |

**Recommendation: default to the CLI.** One browser login links an account, and every CLI-based skill then works with nothing in `.env`. The REST key is only worth setting up for the async publish flow — and note that publishing in Content OS is primarily handled by **Blotato**, with Composio-publish as an optional secondary. So for most people, `composio-connect` + the CLI is the whole story.

> **Gotcha:** the CLI login and the REST `COMPOSIO_API_KEY` must be the **same Composio workspace**. If a REST-based skill "sees no connected accounts" while the CLI clearly does, the API key was generated in a different project — regenerate it in the workspace where you ran `composio link`.

## Why a CLI integration (and not just an MCP / API key)?

For interactive OAuth (linking an Instagram/Gmail account), a browser login flow is the natural fit and the CLI drives it in one command — an API key alone can't perform the user-consent step, and an MCP server adds a registration/restart cycle. So the ecosystem's pattern for **connecting** a tool is the CLI (`composio-connect`), while individual skills **execute** through whichever transport suits them (CLI token for reads, REST key for headless posting). This mirrors the existing onboarding precedents (e.g. Firecrawl's CLI auth living inside its skill) rather than putting interactive auth into `init.py`.

## Reusing the primitive

Other plugins (web-os, mobile-os, …) that need a Composio-brokered account should invoke `content-os`'s `composio-connect` (or copy `skills/composio-connect/scripts/connect.sh`) rather than reimplementing tool onboarding. `connect.sh` exposes `doctor | install | login | link <toolkit> | verify <toolkit> | keyhint` and is safe to re-run.
