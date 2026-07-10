#!/usr/bin/env python3
"""One-command install for the whole Genie ecosystem.

    gh repo clone Claude-Code-Academy/genie-ecosystem
    cd genie-ecosystem && python3 install.py        (Windows: python install.py)

Picks the Genie OSes you want (genie-aios / genie-web-os / genie-mobile-os),
clones each next to your home directory, and runs each repo's own idempotent
`init.py`. This script adds NO install logic of its own — every marketplace,
plugin, and MCP registration stays in the per-OS init.py, which also records
its own manifest at ~/.claude/genie/<os>-install.json for clean uninstall.

The only thing recorded here is which OS clones this script created and where
they live: ~/.claude/genie/ecosystem.json (deliberately NOT *-install.json —
that pattern belongs to the per-OS manifests). `python3 uninstall.py` reads it
to reverse everything with one command.

Idempotent: existing clones are kept (never re-cloned, never overwritten) and
each init.py already skips whatever is installed. Safe to re-run any time.

Flags:
    --aios / --web / --mobile   choose OSes (any combination)
    --all                       all three
    --profile <name>            genie-aios profile: member | maintainer | client
    --dest <dir>                where clones go (default: ~)
    --skip-mcp                  pass through to web/mobile init.py
    -y / --yes                  non-interactive (default profile, skip prompts)
    --dry-run                   print every step, change nothing
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ORG = "Claude-Code-Academy"
GENIE_STATE = Path.home() / ".claude" / "genie"
ECOSYSTEM_MANIFEST = GENIE_STATE / "ecosystem.json"
PY = "python" if os.name == "nt" else "python3"

OSES = {
    "aios": "genie-aios",
    "web": "genie-web-os",
    "mobile": "genie-mobile-os",
}

# Console setup: enable VT on Windows 10+, never crash on odd encodings,
# and drop colors/glyphs when not writing to a capable terminal.
if os.name == "nt":
    os.system("")
try:
    sys.stdout.reconfigure(errors="replace")
except (AttributeError, ValueError):
    pass
_TTY = sys.stdout.isatty()
BOLD, GREEN, YELLOW, RED, RESET = (
    ("\033[1m", "\033[32m", "\033[33m", "\033[31m", "\033[0m") if _TTY else ("",) * 5
)


def _glyph(fancy: str, plain: str) -> str:
    try:
        fancy.encode(sys.stdout.encoding or "utf-8")
        return fancy
    except (UnicodeEncodeError, LookupError):
        return plain


OK_MARK = _glyph("✓", "OK")
BAD_MARK = _glyph("✗", "X")
DOT_MARK = _glyph("·", "-")


def ok(msg: str) -> None:
    print(f"  {GREEN}{OK_MARK}{RESET} {msg}")


def info(msg: str) -> None:
    print(f"  {DOT_MARK} {msg}")


def warn(msg: str) -> None:
    print(f"  {YELLOW}!{RESET} {msg}")


def fail(msg: str) -> None:
    print(f"  {RED}{BAD_MARK}{RESET} {msg}")


def run(cmd: list[str], dry_run: bool, cwd: Path | None = None) -> bool:
    info("$ " + " ".join(str(c) for c in cmd))
    if dry_run:
        return True
    sys.stdout.flush()
    return subprocess.run([str(c) for c in cmd], cwd=cwd, check=False).returncode == 0


def preflight() -> bool:
    print(f"\n{BOLD}Preflight{RESET}")
    good = True
    if shutil.which("git"):
        ok("git found")
    else:
        fail("git not found — install git first")
        good = False
    if shutil.which("gh"):
        auth = subprocess.run(["gh", "auth", "status"], capture_output=True, check=False)
        if auth.returncode == 0:
            ok("gh authenticated")
        else:
            fail("gh is installed but not authenticated — run `gh auth login` first. "
                 "The Genie repos are private to the Claude-Code-Academy org.")
            good = False
    else:
        fail("GitHub CLI (gh) not found — install it and run `gh auth login`. "
             "The Genie repos are private, so plain git clone needs credentials too.")
        good = False
    if shutil.which("claude"):
        ok("claude CLI found")
    else:
        warn("claude CLI not found — clones will succeed but plugin installs inside "
             "each init.py will be skipped. Install Claude Code, then re-run.")
    if not os.environ.get("GITHUB_TOKEN"):
        warn("GITHUB_TOKEN is not exported — Claude Code's background marketplace "
             "auto-update fails silently without it. Add "
             "`export GITHUB_TOKEN=$(gh auth token)` to your shell profile.")
    return good


WORDS = {"aios": "aios", "web": "web", "mobile": "mobile", "all": "all",
         "1": "aios", "2": "web", "3": "mobile", "4": "all"}


def parse_pick(raw: str) -> list[str] | None:
    picked: list[str] = []
    for token in raw.replace(",", " ").split():
        key = WORDS.get(token.strip().lower())
        if key is None:
            return None
        if key == "all":
            return list(OSES)
        if key not in picked:
            picked.append(key)
    return picked or None


def pick_oses(args: argparse.Namespace) -> list[str]:
    chosen = [k for k in OSES if getattr(args, k)]
    if args.all:
        chosen = list(OSES)
    if chosen:
        return chosen
    if args.yes or not sys.stdin.isatty():
        info("no OS flags given; defaulting to genie-aios (use --all for everything)")
        return ["aios"]
    print(f"\n{BOLD}Which Genie OSes do you want?{RESET}")
    print("  1. genie-aios       — personal AI OS, your daily driver")
    print("  2. genie-web-os     — idea → SaaS on Vercel")
    print("  3. genie-mobile-os  — idea → TestFlight")
    print("  4. all three")
    for _ in range(3):
        raw = input("Pick numbers or names (e.g. 1,3 or aios,mobile) [1]: ").strip() or "1"
        picked = parse_pick(raw)
        if picked:
            return picked
        warn(f"didn't understand {raw!r} — try again")
    info("defaulting to genie-aios")
    return ["aios"]


def clone(repo: str, dest: Path, dry_run: bool) -> bool:
    if (dest / ".git").exists():
        ok(f"{dest} already exists — keeping it (init.py is idempotent)")
        return True
    if dest.is_dir() and any(dest.iterdir()):
        fail(f"{dest} exists but is not a git clone (no .git). Move or delete it, "
             "then re-run. (A previous clone may have been interrupted.)")
        return False
    return run(["gh", "repo", "clone", f"{ORG}/{repo}", dest], dry_run)


def run_init(key: str, clone_dir: Path, args: argparse.Namespace) -> bool:
    init = clone_dir / "init.py"
    if not init.is_file():
        if args.dry_run:
            info(f"would run {init} (not cloned yet in dry-run)")
            return True
        fail(f"{init} missing — clone failed?")
        return False
    cmd: list[str] = [sys.executable, str(init)]
    if key == "aios":
        if args.profile:
            cmd += ["--profile", args.profile]
        if args.yes:
            cmd += ["--yes"]
    else:
        if args.skip_mcp:
            cmd += ["--skip-mcp"]
    if args.dry_run:
        cmd += ["--dry-run"]  # each init.py has its own dry-run; run it for real
    return run(cmd, False, cwd=clone_dir)


def record(cloned: dict[str, str], profile: str | None, dry_run: bool) -> None:
    if dry_run:
        info(f"would record {ECOSYSTEM_MANIFEST}")
        return
    GENIE_STATE.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    existing: dict = {}
    if ECOSYSTEM_MANIFEST.is_file():
        try:
            loaded = json.loads(ECOSYSTEM_MANIFEST.read_text())
            if isinstance(loaded, dict):
                existing = loaded
        except (OSError, json.JSONDecodeError):
            existing = {}
    oses = existing.get("oses")
    oses = oses if isinstance(oses, dict) else {}
    oses.update(cloned)
    manifest = {
        "oses": oses,
        "profile": profile or existing.get("profile") or "member",
        "installed_at": existing.get("installed_at", now),
        "last_updated": now,
    }
    ECOSYSTEM_MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    ok(f"recorded {ECOSYSTEM_MANIFEST}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--aios", action="store_true", help="install genie-aios")
    p.add_argument("--web", action="store_true", help="install genie-web-os")
    p.add_argument("--mobile", action="store_true", help="install genie-mobile-os")
    p.add_argument("--all", action="store_true", help="install all three OSes")
    p.add_argument("--profile", default=None, help="genie-aios profile: member | maintainer | client")
    p.add_argument("--dest", type=Path, default=Path.home(), help="parent dir for clones (default: ~)")
    p.add_argument("--skip-mcp", action="store_true", help="skip MCP registration in web/mobile init")
    p.add_argument("-y", "--yes", action="store_true", help="non-interactive")
    p.add_argument("--dry-run", action="store_true", help="print steps, change nothing")
    args = p.parse_args(argv)
    args.dest = args.dest.expanduser().resolve()

    print(f"{BOLD}Genie ecosystem install{RESET}")
    if not preflight():
        return 1

    chosen = pick_oses(args)
    print(f"\n{BOLD}Installing:{RESET} " + ", ".join(OSES[k] for k in chosen))

    cloned: dict[str, str] = {}
    failures = []
    for key in chosen:
        repo = OSES[key]
        clone_dir = args.dest / repo
        print(f"\n{BOLD}{repo}{RESET}")
        if not clone(repo, clone_dir, args.dry_run):
            fail(f"could not clone {repo} — are you a Claude-Code-Academy member?")
            failures.append(repo)
            continue
        # Record every clone we made, even if init fails below — uninstall.py
        # must be able to find it either way.
        cloned[repo] = str(clone_dir)
        if not run_init(key, clone_dir, args):
            failures.append(repo)

    if cloned:
        print(f"\n{BOLD}Recording{RESET}")
        record(cloned, args.profile, args.dry_run)

    print(f"\n{BOLD}Done{RESET}")
    for repo, path in cloned.items():
        if repo not in failures:
            ok(f"{repo} → {path}")
    for repo in failures:
        fail(f"{repo} did not finish — fix the error above and re-run (idempotent)")
    if cloned and not args.dry_run:
        print("\nNext steps:")
        print("  1. Restart Claude Code so the new plugins load.")
        print("  2. Drop API keys into each OS's .env (see its .env.example).")
        print(f"  3. To remove everything later: {PY} uninstall.py (in this repo).")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
