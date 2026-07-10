#!/usr/bin/env python3
"""One-command uninstall for the whole Genie ecosystem.

    cd genie-ecosystem && python3 uninstall.py            # remove installs
    cd genie-ecosystem && python3 uninstall.py --purge    # ...and delete the clones
    (Windows: python uninstall.py)

Reverses everything `install.py` set up, by delegating to the per-OS
`uninstall.py --all` (byte-identical across the OS repos): it reads the
manifests at ~/.claude/genie/<os>-install.json and removes exactly what each
init.py recorded — plugins, marketplaces no longer in use, skills, MCP
servers — while keeping .env files, PERSONAL.md overlays, and built projects.

--purge additionally deletes the OS clones, but ONLY the ones recorded in
~/.claude/genie/ecosystem.json (i.e. clones that install.py itself created —
never a clone you made by hand). A clone is also skipped when it has
uncommitted changes, or when it holds user data the plain uninstall promises
to keep (.env, projects/, outputs/); add --force to delete those anyway.

Flags:
    --purge      also delete the recorded OS clones (see safety rules above)
    --force      with --purge: delete even clones holding .env/projects/outputs
    --dry-run    print every step, change nothing
    -y / --yes   skip confirmation prompts (required for --purge in scripts/CI)
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

GENIE_STATE = Path.home() / ".claude" / "genie"
ECOSYSTEM_MANIFEST = GENIE_STATE / "ecosystem.json"
DEFAULT_CLONES = [
    Path.home() / "genie-aios",
    Path.home() / "genie-web-os",
    Path.home() / "genie-mobile-os",
]
USER_DATA = (".env", "projects", "outputs")
PY = "python" if os.name == "nt" else "python3"

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


def read_manifest() -> dict:
    if ECOSYSTEM_MANIFEST.is_file():
        try:
            loaded = json.loads(ECOSYSTEM_MANIFEST.read_text())
            if isinstance(loaded, dict):
                return loaded
        except (OSError, json.JSONDecodeError):
            warn(f"could not parse {ECOSYSTEM_MANIFEST} — treating as empty")
    return {}


def recorded_clones(manifest: dict) -> list[Path]:
    oses = manifest.get("oses")
    oses = oses if isinstance(oses, dict) else {}
    return [Path(p) for p in oses.values()]


def known_clones(manifest: dict) -> list[Path]:
    """Recorded clones plus the default locations — used ONLY to find a copy of
    the per-OS uninstall.py, never as a deletion list."""
    paths = recorded_clones(manifest)
    for d in DEFAULT_CLONES:
        if d not in paths:
            paths.append(d)
    return [p for p in paths if p.is_dir()]


def find_os_uninstaller(clones: list[Path]) -> Path | None:
    for clone in clones:
        script = clone / "uninstall.py"
        if script.is_file():
            return script
    return None


def git_dirty(clone: Path) -> bool:
    """True when the tree has uncommitted changes — or when we can't tell."""
    try:
        r = subprocess.run(
            ["git", "-C", str(clone), "status", "--porcelain"],
            capture_output=True, text=True, check=False,
        )
    except FileNotFoundError:
        warn("git not found — treating every clone as dirty (nothing deleted)")
        return True
    return r.returncode != 0 or bool(r.stdout.strip())


def user_data_in(clone: Path) -> list[str]:
    found = []
    for name in USER_DATA:
        p = clone / name
        if p.is_file() or (p.is_dir() and any(p.iterdir())):
            found.append(name)
    return found


def rmtree(path: Path) -> None:
    """shutil.rmtree that also handles Windows read-only .git files."""
    def _onerror(func, p, _exc):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    shutil.rmtree(path, onerror=_onerror)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--purge", action="store_true", help="also delete the recorded OS clones")
    p.add_argument("--force", action="store_true",
                   help="with --purge: delete even clones holding .env/projects/outputs")
    p.add_argument("--dry-run", action="store_true", help="print steps, change nothing")
    p.add_argument("-y", "--yes", action="store_true", help="skip confirmations")
    args = p.parse_args(argv)

    print(f"{BOLD}Genie ecosystem uninstall{RESET}")
    manifest = read_manifest()

    if args.purge and not shutil.which("claude"):
        fail("claude CLI not found — plugins and marketplaces can't be unregistered, "
             "and purging the clones would orphan the ones registered from them. "
             "Install Claude Code (or run without --purge).")
        return 1

    # 1. Manifest-based teardown via the per-OS uninstaller (they're identical).
    print(f"\n{BOLD}Removing installed plugins / marketplaces / MCP servers{RESET}")
    script = find_os_uninstaller(known_clones(manifest))
    if script is None:
        recorded = [f for f in GENIE_STATE.glob("*-install.json")]
        if recorded:
            fail("no Genie OS clone with uninstall.py found, but install manifests "
                 f"exist in {GENIE_STATE}. Re-clone any OS repo (e.g. genie-aios) "
                 "and re-run, or run its uninstall.py --all directly.")
            return 1
        info("nothing recorded — no per-OS install manifests found")
    else:
        cmd = [sys.executable, str(script), "--all"]
        if args.dry_run:
            cmd.append("--dry-run")
        if args.yes:
            cmd.append("--yes")
        info("$ " + " ".join(cmd))
        sys.stdout.flush()
        rc = subprocess.run(cmd, cwd=script.parent, check=False).returncode
        if rc != 0:
            fail(f"{script} exited {rc} — fix the error above and re-run")
            return rc

    # 2. Optionally delete the clones install.py created (never hand-made ones).
    kept: list[Path] = []
    if args.purge:
        print(f"\n{BOLD}Purging clones{RESET}")
        targets = [c for c in recorded_clones(manifest) if c.is_dir()]
        if not targets:
            info("no clones recorded in ecosystem.json — clones you made by hand "
                 "are yours to delete (or re-run install.py first so they're recorded)")
        for clone in targets:
            if git_dirty(clone):
                warn(f"{clone} has uncommitted changes — NOT deleting (inspect it yourself)")
                kept.append(clone)
                continue
            data = user_data_in(clone)
            if data and not args.force:
                warn(f"{clone} holds user data ({', '.join(data)}) — NOT deleting. "
                     "Re-run with --force to delete anyway.")
                kept.append(clone)
                continue
            if not args.yes:
                if not sys.stdin.isatty():
                    warn(f"non-interactive without --yes — keeping {clone}")
                    kept.append(clone)
                    continue
                if not args.dry_run:
                    answer = input(f"Delete {clone}? [y/N] ").strip().lower()
                    if answer != "y":
                        info(f"keeping {clone}")
                        kept.append(clone)
                        continue
            if args.dry_run:
                info(f"would delete {clone}")
            else:
                rmtree(clone)
                ok(f"deleted {clone}")

    # 3. Remove the ecosystem manifest — but only when it no longer records
    # anything on disk. It is the sole record of custom-path clones.
    if ECOSYSTEM_MANIFEST.is_file():
        remaining = [c for c in recorded_clones(manifest) if c.is_dir()]
        if args.dry_run:
            if args.purge and not kept:
                info(f"would remove {ECOSYSTEM_MANIFEST}")
            else:
                info(f"would keep {ECOSYSTEM_MANIFEST} (still records clone locations)")
        elif not remaining:
            ECOSYSTEM_MANIFEST.unlink()
            ok(f"removed {ECOSYSTEM_MANIFEST}")
        else:
            info(f"keeping {ECOSYSTEM_MANIFEST} — it records where your clones live")

    print(f"\n{BOLD}Done{RESET}")
    if not args.dry_run:
        print("Restart Claude Code so it drops the removed plugins and skills.")
        if not args.purge:
            print("Clones were kept (your .env, overlays, and projects live there).")
            print(f"Run `{PY} uninstall.py --purge` to delete them too.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
