# Set up Genie with your agent

**This is the single member setup guide for Genie AIOS.** Accept your Academy
GitHub invitation, then paste the prompt below into your agent. You do not need
to clone every Genie repository, install every plugin, or collect every API key.

Genie adds shared skills, context and private preferences to **Claude Code,
Codex and Hermes**. Core is included; Content OS, Mobile OS and Web OS are optional.
The currently published portable release is **v0.1.0-alpha.1**. It is available
to members, with native client/account/desktop qualification still pending.
The agent must verify your selected workflows on your machine before calling
them ready. [Release notes](releases/portable-v0.1.0-alpha.1.md).

## Copy this prompt

```text
Set up Genie AIOS on my computer. Read and follow this canonical guide:
https://github.com/Claude-Code-Academy/genie-ecosystem/blob/main/docs/getting-started.md

Check that you can operate my local machine. Help me choose Claude Code,
Codex and/or Hermes, plus any optional departments. Then carry out the setup,
install missing supported prerequisites, and guide me through sign-ins and
secure credential entry. Preserve my existing configuration and private data.
Continue through verification and tell me exactly which workflows work and
what remains pending. Never ask me to paste secrets into chat. If you cannot
operate my machine, give me the shortest handoff to a local agent that can.
```

A local **Codex app/CLI, Claude Code session, or Hermes session with terminal
and file access** can perform setup. A normal ChatGPT/Claude web conversation,
remote coding container, or cloud task cannot install software on your laptop
merely because you paste this link. It can read this public guide and help you
open a local agent or terminal. Claude Desktop's local **Code** sessions and
Cowork/ordinary chat are different surfaces; this portable installer does not
install a Cowork package. No custom Genie desktop is required.

## Instructions for the setup agent

Follow the stages below in order and continue after each completed user step.
Use the released installer for installation logic. Do not improvise a new
installer, copy skills by hand, or run the legacy `init.py` / `install.py` /
`export-skills.py` route for this request. Source-development flags such as
`--core-source`, `--skip-dependencies` and replacement catalogs are not the member
route. Existing legacy installations can remain in place while inspected;
do not convert or remove them implicitly.

### 1. Check the machine and choose the experience

- Confirm commands run on the member's intended computer and user account,
  with local filesystem access and an interactive terminal for sign-in.
  A desktop UI does not by itself prove the task's execution is local.
- Detect OS/architecture and existing applications. The published bootstrap
  currently offers **Apple Silicon macOS** and **native Windows x64** routes.
  These are alpha provisioning routes, not a completed support certification.
  Intel macOS, Linux, Windows ARM, WSL and hosted execution are outside this
  bootstrap matrix. Explain the exact limitation; do not silently switch hosts.
- Ask only for missing choices: applications (any subset of Claude Code, Codex,
  Hermes), local desktop as well as terminal, and optional departments.
  Suggest the current local application and **Core only** if the member has no
  preference. Add Content OS for content work, Mobile OS for app development,
  Web OS for web/SaaS development. "All three departments" does not mean every
  repository or every native marketplace plugin.
- Reuse working installations. Detect existing Genie storage, custom client
  homes/profiles and owned registrations before changing them. Keep their paths
  and environment active during setup; use the existing Genie data root with
  `--home` when it differs from `~/.genie`. Do not change `HOME` to simulate a
  user: `--user-home` does not isolate native vendor installers.

If `GENIE_HOME` is set, pass its resolved path through `--home`; bootstrap does
not use that variable as its default data root. Core recognizes `CODEX_HOME`
and `HERMES_HOME`, but this alpha bootstrap does **not** automatically redirect
Claude registrations through `CLAUDE_CONFIG_DIR`. A custom Claude directory
requires separately reviewed configuration: confirm the actual target before
running setup and keep that surface pending until verified. Do not replace it
with a default-home installation. Named client/provider profiles also require
checking the member's intended active profile; setup is not a profile selector.

If local execution is unavailable, say so immediately. Help the member open an
already installed local agent and paste the same prompt. If none is installed,
guide them to download the public ZIP below and run the one setup command in a
local terminal; it provisions the selected missing clients. Resume verification
in that local client after sign-in. Do not claim a cloud sandbox is their machine.

### 2. Obtain the public setup folder

Use an existing clean, current checkout if available. Otherwise download and
extract the [public setup ZIP](https://github.com/Claude-Code-Academy/genie-ecosystem/archive/refs/heads/main.zip)
into a fresh folder, or clone
`https://github.com/Claude-Code-Academy/genie-ecosystem.git` if Git already exists.
Git is not required for the ZIP route. Do not reset a member's modified checkout.

The extracted folder must contain `setup.sh`, `setup.ps1`, `bootstrap.py`,
`bootstrap-registry.json` and `bootstrap-release.json`. Read the release metadata
and keep the published private repository, tag and checksum unchanged. Work from
this folder. The public folder contains the launcher and guide; it does not grant
access to private Genie packages.

### 3. Run setup and help with the prompts

On Apple Silicon macOS, from the setup folder:

```sh
sh ./setup.sh
```

On native Windows x64, from the setup folder in PowerShell:

```powershell
.\setup.ps1
```

If Windows blocks a downloaded script, inspect the source and its origin before
using the member's permitted per-file unblocking procedure. Do not disable
machine-wide policy or bypass an organization's restrictions.

The interactive flow asks for applications, departments (Enter keeps Core only),
and desktop setup. If those choices are already known, pass them directly:

```sh
sh ./setup.sh --harness codex --module content-os --desktop
```

```powershell
.\setup.ps1 --harness codex --module content-os --desktop
```

`--harness claude,codex,hermes` selects all three; use a comma-separated subset
without spaces. Repeat `--module` for `content-os`, `mobile-os` and `web-os` as
selected. Use `--no-desktop` for terminal only. There is no `--all` or `--yes` flag.
For Core only, omit `--module` and answer the departments prompt with Enter.

Setup reuses compatible Python 3.11+ or provisions its pinned runtime, provisions
GitHub CLI when absent, and then:

1. Guides the member's own GitHub browser sign-in and checks access to the exact
   private Core repository. A successful login alone does not prove entitlement.
   If access fails, check the accepted invitation, intended account, repository
   grant and any organization SSO authorization. Request the maintainer's help
   for access; do not borrow their token.
2. Downloads and verifies the published Core envelope. The current envelope
   includes the four portable modules, installing only the selected departments.
3. Reuses or installs the selected official clients and guides their native
   provider sign-in. Let the member choose account/provider and billing mode;
   do not silently switch to API billing. Existing Hermes provider settings
   remain intact and need their own workflow check.
4. Installs Core, selected departments, declared helper dependencies and client
   registrations. Requested desktop installation follows native vendor prompts.
5. Offers secure connection setup and registers the terminal command on PATH
   by default (`--no-enable-path` retains only the absolute launcher).

Use a terminal the member can interact with for browser sign-ins, hidden secret
input and OS prompts. If an agent tool cannot provide interactive stdin, open the
member's local terminal with the exact setup command and resume when it finishes.
Do not stream or record credential entry. `--non-interactive` can stage selected
steps, but it defers authentication/secret entry and is not completed onboarding.

For a connection needed now, help the member obtain its key from the provider and
enter it in the installer's hidden terminal prompt. New Genie-managed secrets go
to macOS Keychain or Windows Credential Manager; native OAuth stays native.
Never request secret values in chat, command arguments, shell profiles or Git.
Leave existing `.env` files intact. Unneeded integrations can be explicitly
deferred; do not ask for every key in the ecosystem.
After a deferred prompt or secure-store failure, resume with
`genie connections setup --module content-os` (use the intended installed module).

### 4. Resume safely when a step needs attention

The non-secret progress receipt is `<Genie home>/bootstrap/receipt.json` (normally
`~/.genie/bootstrap/receipt.json`). Inspect the receipt and concise errors, without
dumping environment files or native authentication output.

| Situation | Next action |
|---|---|
| Login cancelled, EOF, incomplete native prompt | Complete the local prompt and rerun the same setup command with the same selections and home. |
| Repository not found / no private access | Check GitHub account, accepted invitation, repository grant and SSO. A public guide does not grant membership. |
| Installer checksum mismatch | Stop that download; obtain reviewed publisher metadata. Never remove or bypass checksum verification. |
| Modified registration or duplicate legacy skill | Inspect ownership and preserve the member's version. Use the migration inventory; resolve the specific conflict before retirement. |
| Interrupted Core operation | Run `genie status`, inspect the reported operation, and use `genie resume <operation-id>` as appropriate; do not delete state or locks. |
| Optional dependency/connection unavailable | Report the affected workflow as blocked or deliberately deferred. Continue independent setup. |
| Unsupported OS/client surface | State the exact unsupported combination. Do not substitute a cloud/WSL install and label it local readiness. |

Keep the setup folder until verification is complete. A registered installed
launcher works independently of the original source clone. If the current shell
has not reloaded PATH, use the absolute launcher at `<Genie home>/bin/genie`
(macOS) or `<Genie home>\bin\genie.cmd` (Windows), or reopen the terminal.

### 5. Verify the result in each selected application

After sign-in and native prompts, use the installed launcher:

```text
genie status
genie --json doctor
genie connections list
genie context resolve core/welcome
```

When diagnosing a particular project, also run
`genie --json doctor --workspace /absolute/path/to/project` with the real path.
Check active profile/home, package integrity, instruction precedence,
registrations, helper dependencies, pending operations and connection blockers.
Do not infer readiness from the process exit code or a count of installed files.

**The current alpha deliberately reports `pending-native-verification` in its
bootstrap receipt, `qualified: false` from setup and `release_qualified: false`
from doctor.** Authentication and desktop checks remain unverified there even
after local success. Do not edit these records to turn them green. Maintain a
separate concise verification report of what was actually observed.

For every selected terminal and desktop surface separately:

1. Start a **fresh local session outside the setup clone**. Check that the Genie
   instruction bridge is effective and the `core-welcome` skill is discoverable.
   Ask the agent to use it to list installed departments and explain where your
   private preferences live. Compare with `genie status`.
2. Run a harmless representative workflow for each chosen department, using its
   registered skill and resolved private context. Examples: a draft content
   outline, a mobile idea brief, or a web project brief. Save drafts locally;
   onboarding does not authorize publishing, deployments or paid external jobs.
3. For any integration required by that workflow, complete native OAuth/key setup
   and perform a **read-only** service check. Key presence and MCP registration
   alone do not prove usable access. Unqualified required capabilities must stay
   visibly blocked with the next action identified.
4. Record application/version, OS/architecture, local surface, invoked workflow,
   result and remaining blockers. A terminal result cannot certify a desktop.
   If you cannot observe a fresh desktop session, ask the member to perform the
   exact small check and wait for its result; record it as member-reported evidence.

Finish with a short handoff: installed departments and versions, tested surfaces
and workflows, private data location, deferred connections, and the next exact
action for anything pending. Say **"ready for these tested workflows"** only when
those checks actually pass. Do not claim every skill or every application works
because one draft succeeded.

### 6. Show the member the everyday commands

```text
genie install content-os
genie personalize content-os --skill instagram-carousel --open
genie connections setup --module content-os
genie update --check
genie update
genie uninstall content-os
genie doctor
```

Use `mobile-os` or `web-os` to add those departments. Restart affected agent
sessions after changes. Updates apply to installed modules and respect holds;
removal retains private data. For portable installations, Genie owns department
lifecycle—do not also install the same department through a native marketplace.

Preferences and assets belong under the private `<Genie home>/personal/`
hierarchy, scoped to root, department, skill or mapped workspace. They do not
belong in immutable packages or the publisher's repositories. Explicit preferences
take precedence over shipped defaults within the harness's own instruction and
permission rules. Keep existing profile/vault pointers; Obsidian captures append
new `raw/inbox/` files and leave `wiki/` to the Librarian.

## Optional ecosystem tools and membership

The [ecosystem map](member-ecosystem-map.md) distinguishes the four portable modules
from native plugins, curated tools, the skill library and the separate second-brain
kit. Install those only for a requested use case with their own compatibility and
authentication checks. They are not prerequisites for portable Core. Owner-only
repositories are excluded from member installation.

Private updates use the member's own GitHub access. Removing all effective access
prevents future private downloads; it does not remotely delete existing clones,
installed packages or cached artifacts. See [member access and updates](member-access.md)
for the exact boundary and repository license links.

Existing legacy installations can use the [legacy setup reference](legacy-getting-started.md).
Developers can use the [bootstrap implementation reference](portable-bootstrap-preview.md).
Neither replaces this guide for new member onboarding.
