#!/usr/bin/env python3
"""Export installed Genie skills to other agents: Codex (via ~/.agents/skills)
and Hermes.

    python3 export-skills.py                 # export to every agent found on this machine
    python3 export-skills.py --agents        # just ~/.agents/skills/
    python3 export-skills.py --hermes        # just ~/.hermes/skills/
    python3 export-skills.py --list          # show what would be exported, change nothing

If a newer implementation of this exact job is installed as part of the
`genie-add` skill (genie-essentials plugin), this script steps aside and
delegates to it instead of running its own copy logic — same behavior, kept
up to date by `/plugin update genie-essentials@genie` instead of by editing
this file. When no such skill is installed, the fallback logic below does
the same job on its own.

Claude skills, Codex skills, and Hermes skills all use the same SKILL.md folder
format (agentskills.io), so no conversion is needed — this script copies each
skill from your installed Genie plugins (~/.claude/plugins/cache/...) into the
target agent's skills directory and stamps it with a marker file so re-runs
refresh cleanly and never touch skills you installed there yourself.

Codex officially scans ~/.agents/skills (not ~/.codex/skills) for skills, so
that's the fallback's target — same as the genie_sync.py it defers to.

Credentials: Genie skills read keys from .env (walking up from cwd) and fall
back to the user-level ~/.claude/genie/.env. Fill THAT file once (genie-aios's
setup.py links it for you) and the same keys work in Codex and Hermes too.

Notes:
- Restart Codex after exporting; skills load at startup.
- Skills whose SKILL.md references ${CLAUDE_PLUGIN_ROOT} may need their scripts
  invoked relative to the skill folder on non-Claude agents — the export warns.
"""

from __future__ import annotations

import argparse
import glob
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CACHE = Path.home() / ".claude" / "plugins" / "cache"
MARKER = ".genie-export.json"
TARGETS = {
    "agents": Path.home() / ".agents" / "skills",
    "hermes": Path.home() / ".hermes" / "skills",
}

# Where genie_sync.py (the genie-add skill's implementation of this same job)
# is cached once installed. Newest version dir wins.
GENIE_SYNC_GLOB = str(
    CACHE / "genie" / "genie-essentials" / "*" / "skills" / "genie-add"
    / "scripts" / "genie_sync.py"
)

BOLD, GREEN, YELLOW, RED, RESET = (
    ("\033[1m", "\033[32m", "\033[33m", "\033[31m", "\033[0m")
    if sys.stdout.isatty() else ("",) * 5
)


def ok(msg: str) -> None:
    print(f"  {GREEN}+{RESET} {msg}")


def info(msg: str) -> None:
    print(f"  - {msg}")


def warn(msg: str) -> None:
    print(f"  {YELLOW}!{RESET} {msg}")


def _version_key(name: str) -> tuple[int, ...]:
    try:
        return tuple(int(p) for p in name.split("."))
    except ValueError:
        return (-1,)


def find_genie_sync() -> Path | None:
    """Newest cached copy of genie_sync.py, if the genie-add skill is installed."""
    candidates = [Path(p) for p in glob.glob(GENIE_SYNC_GLOB) if Path(p).is_file()]
    if not candidates:
        return None

    def version_of(p: Path) -> tuple[int, ...]:
        parts = p.parts
        try:
            idx = parts.index("genie-essentials")
            return _version_key(parts[idx + 1])
        except (ValueError, IndexError):
            return (-1,)

    return max(candidates, key=version_of)


def delegate(script: Path, argv: list[str]) -> int:
    forwarded = argv if argv else ["--all"]
    print(f"{BOLD}Genie skill export{RESET}")
    info(f"delegating to {script} (genie-add skill) -- run "
         f"`claude plugin update genie-essentials@genie` to get the newest version")
    cmd = [sys.executable, str(script), *forwarded]
    sys.stdout.flush()
    return subprocess.run(cmd, check=False).returncode


def installed_skills() -> list[tuple[str, Path]]:
    """[(plugin@marketplace, skill_dir), ...] from the latest cached version of
    every installed plugin, across every marketplace."""
    out: list[tuple[str, Path]] = []
    if not CACHE.is_dir():
        return out
    for market in sorted(p for p in CACHE.iterdir() if p.is_dir()):
        for plugin in sorted(p for p in market.iterdir() if p.is_dir()):
            versions = [v for v in plugin.iterdir() if v.is_dir()]
            if not versions:
                continue
            latest = max(versions, key=lambda v: _version_key(v.name))
            skills_root = latest / "skills"
            if not skills_root.is_dir():
                continue
            for skill in sorted(skills_root.iterdir()):
                if skill.is_dir() and any(
                    f.name.lower() == "skill.md" for f in skill.iterdir() if f.is_file()
                ):
                    out.append((f"{plugin.name}@{market.name}", skill))
    return out


def uses_plugin_root(skill_dir: Path) -> bool:
    """True only for REAL ${CLAUDE_PLUGIN_ROOT} path usages — lines that also
    mention SKILL_DIR are the portable-convention definition, not a usage."""
    for md in skill_dir.glob("*.md"):
        try:
            for line in md.read_text(encoding="utf-8", errors="replace").splitlines():
                if "${CLAUDE_PLUGIN_ROOT}" in line and "SKILL_DIR" not in line:
                    return True
        except OSError:
            pass
    return False


def export_to(agent: str, dest_root: Path, skills: list[tuple[str, Path]], dry: bool) -> None:
    print(f"\n{BOLD}{agent}: {dest_root}{RESET}")
    if not dest_root.parent.is_dir() and not dry:
        dest_root.parent.mkdir(parents=True, exist_ok=True)
    exported = skipped = 0
    for spec, skill in skills:
        dest = dest_root / skill.name
        marker = dest / MARKER
        if dest.exists() and not marker.is_file():
            warn(f"{skill.name}: already exists in {agent} and wasn't exported by "
                 "this script — skipping (yours)")
            skipped += 1
            continue
        if dry:
            info(f"would export {skill.name}  (from {spec})")
            continue
        if dest.exists():
            shutil.rmtree(dest)
        dest_root.mkdir(parents=True, exist_ok=True)
        shutil.copytree(skill, dest)
        marker_data = {
            "source": str(skill),
            "plugin": spec,
            "exported_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        (dest / MARKER).write_text(json.dumps(marker_data, indent=2) + "\n")
        ok(f"{skill.name}  (from {spec})")
        exported += 1
        if uses_plugin_root(skill):
            warn(f"{skill.name}: references ${{CLAUDE_PLUGIN_ROOT}} — on {agent}, "
                 "run its scripts relative to the skill folder instead")
    if not dry:
        print(f"  = {exported} exported, {skipped} kept")


def fallback_main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Fallback copier (genie-add skill not installed)")
    p.add_argument("--agents", action="store_true", help="export to ~/.agents/skills")
    p.add_argument("--hermes", action="store_true", help="export to ~/.hermes/skills")
    p.add_argument("--list", action="store_true", help="preview only, change nothing")
    args = p.parse_args(argv)

    skills = installed_skills()
    print(f"{BOLD}Genie skill export{RESET} — {len(skills)} skill(s) installed via Genie plugins")
    if not skills:
        info("no Genie plugins installed — run install.py (or /plugin install) first")
        return 0

    chosen = [k for k in TARGETS if getattr(args, k)] or list(TARGETS)
    for agent in chosen:
        export_to(agent, TARGETS[agent], skills, args.list)

    if not args.list:
        print(f"\n{BOLD}Done{RESET}")
        print("  Keys: skills fall back to ~/.claude/genie/.env — fill it once, works everywhere.")
        print("  Codex loads skills at startup from ~/.agents/skills — restart it. "
              "Hermes picks them up as slash commands.")
        print("  Re-run this script after installing or updating Genie plugins.")
        print("  Tip: install genie-essentials@genie for the genie-add skill, a newer, "
              "more capable version of this same job (also handles MCP registration).")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    script = find_genie_sync()
    if script is not None:
        return delegate(script, argv)

    return fallback_main(argv)


if __name__ == "__main__":
    sys.exit(main())
