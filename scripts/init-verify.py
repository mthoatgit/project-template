#!/usr/bin/env python
"""Post-write verify for /init-project — enforce MUSTs that agent free-form
fill rounds keep glossing.

Invoked by /init-project step 6 (after CLAUDE.md, README.md, item 001, and
docs/backlog/index.md have been written by the agent). Two jobs:

1. AUTOFIX four known scaffold-time misses whose correct value is knowable:
   - CLAUDE.md ``--test-cmd "<test-cmd>"`` -> ``--test-cmd "python scripts/test.py"``
   - item 001 ``priority: P<n>`` -> ``priority: P1`` (per /init-project step 5 MUST)
   - item 001 date-only ``created`` / ``updated`` -> ``YYYY-MM-DD 00:00``
   - docs/backlog/index.md row 001 Stage cell bare ``1`` -> ``1 - Concept``
     plus date-only timestamps and Priority in the same row

2. HARD-FAIL on residual template markers or missing structural content
   the agent must have written by hand:
   - ``status: template`` frontmatter or ``**Template file.**`` banner
   - Unfilled ``<Project Name>`` / ``<One or two sentences ...>`` placeholders
   - item 001 missing ``stage: 1`` / ``stage_attempt: 1`` / ``## Artefacts``

Exit codes:
  0 - all MUSTs satisfied (with or without autofixes)
  1 - hard errors remain; /init-project must stop and report to the user

Usage:
  python <path-to-project-template>/scripts/init-verify.py <project-root>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def verify(target: Path) -> int:
    fixes: list[str] = []
    errors: list[str] = []

    _check_claude(target, fixes, errors)
    _check_readme(target, fixes, errors)
    item = _find_item_001(target, errors)
    if item is not None:
        _check_item_001(item, fixes, errors)
    _check_index(target, fixes, errors)

    if fixes:
        print("AUTOFIXED:")
        for f in fixes:
            print(f"  - {f}")
    if errors:
        print("\nERRORS (require manual fix before /init-project can finish):")
        for e in errors:
            print(f"  - {e}")
        return 1
    if not fixes:
        print("post-write verify: no misses detected")
    return 0


def _check_claude(target: Path, fixes: list[str], errors: list[str]) -> None:
    f = target / "CLAUDE.md"
    if not f.exists():
        errors.append("CLAUDE.md: file missing")
        return
    txt = f.read_text(encoding="utf-8")
    orig = txt

    # Autofix: <test-cmd> placeholder
    new = re.sub(
        r'--test-cmd\s+"<test-cmd>"',
        '--test-cmd "python scripts/test.py"',
        txt,
    )
    if new != txt:
        fixes.append('CLAUDE.md: --test-cmd "<test-cmd>" -> "python scripts/test.py"')
        txt = new

    # Hard-fail on residual template markers
    if "status: template" in txt:
        errors.append("CLAUDE.md: still has `status: template` frontmatter")
    if "**Template file.**" in txt:
        errors.append("CLAUDE.md: still has template banner")
    if "<Project Name>" in txt:
        errors.append("CLAUDE.md: `<Project Name>` placeholder in title still unfilled")
    if "<One or two sentences" in txt:
        errors.append("CLAUDE.md: `<One or two sentences ...>` placeholder unfilled")

    if txt != orig:
        f.write_text(txt, encoding="utf-8")


def _check_readme(target: Path, fixes: list[str], errors: list[str]) -> None:
    f = target / "README.md"
    if not f.exists():
        errors.append("README.md: file missing")
        return
    txt = f.read_text(encoding="utf-8")

    if "status: template" in txt:
        errors.append("README.md: still has `status: template` frontmatter")
    if "**Template file.**" in txt:
        errors.append("README.md: still has template banner")
    if "<Project Name>" in txt:
        errors.append("README.md: `<Project Name>` placeholder still unfilled")


def _find_item_001(target: Path, errors: list[str]) -> Path | None:
    backlog = target / "docs" / "backlog"
    items = sorted(backlog.glob("001-*.md"))
    if not items:
        errors.append("item 001: docs/backlog/001-*.md not found")
        return None
    if len(items) > 1:
        errors.append(
            f"item 001: multiple 001-*.md files found ({[p.name for p in items]}); "
            "keep exactly one"
        )
    return items[0]


def _check_item_001(item: Path, fixes: list[str], errors: list[str]) -> None:
    txt = item.read_text(encoding="utf-8")
    orig = txt

    # Autofix: priority P<n> -> P1
    new = re.sub(r"^priority: P\d+\s*$", "priority: P1", txt, flags=re.MULTILINE)
    if new != txt:
        fixes.append(f"{item.name}: priority -> P1 (init-project step 5 MUST)")
        txt = new

    # Autofix: date-only created/updated -> YYYY-MM-DD 00:00
    def _add_time(m: re.Match[str]) -> str:
        return f"{m.group(1)}: {m.group(2)} 00:00"

    new = re.sub(
        r"^(created|updated): (\d{4}-\d{2}-\d{2})\s*$",
        _add_time,
        txt,
        flags=re.MULTILINE,
    )
    if new != txt:
        fixes.append(f"{item.name}: appended `00:00` to date-only created/updated")
        txt = new

    # Structural MUSTs — hard-fail on missing
    if not re.search(r"^stage: 1\s*$", txt, flags=re.MULTILINE):
        errors.append(f"{item.name}: missing `stage: 1` in frontmatter")
    if not re.search(r"^stage_attempt: 1\s*$", txt, flags=re.MULTILINE):
        errors.append(f"{item.name}: missing `stage_attempt: 1` in frontmatter")
    if "## Artefacts" not in txt:
        errors.append(f"{item.name}: missing `## Artefacts` section")
    else:
        # Verify all 5 stage bullets present
        for stage in (
            "Stage 1 (Concept)",
            "Stage 2 (Requirements + Epic-Birth)",
            "Stage 3 (Architecture)",
            "Stage 4 (Task-Breakdown)",
            "Stage 5 (Tests)",
        ):
            if f"**{stage}:** pending" not in txt:
                errors.append(
                    f"{item.name}: `## Artefacts` missing `**{stage}:** pending` bullet"
                )
    if "## Core" not in txt:
        errors.append(f"{item.name}: missing `## Core` section")

    if txt != orig:
        item.write_text(txt, encoding="utf-8")


def _check_index(target: Path, fixes: list[str], errors: list[str]) -> None:
    f = target / "docs" / "backlog" / "index.md"
    if not f.exists():
        errors.append("docs/backlog/index.md: file missing")
        return
    txt = f.read_text(encoding="utf-8")
    orig = txt
    lines = txt.split("\n")

    for i, line in enumerate(lines):
        # Header expected: ID | Type | Prio | Title | Status | Stage | Created | Updated | File
        # 001 row (leading `|`) — split gives ['', ' 001 ', ' idea ', ...]
        if not re.match(r"^\|\s*001\s*\|", line):
            continue
        parts = line.split("|")
        if len(parts) < 10:
            errors.append(
                f"docs/backlog/index.md: 001 row has {len(parts)} pipe-fields, "
                f"expected 10 (leading + trailing empties + 9 columns)"
            )
            continue

        # Positions: parts[0]='', [1]=ID, [2]=Type, [3]=Prio, [4]=Title, [5]=Status,
        #            [6]=Stage, [7]=Created, [8]=Updated, [9]=File, [10]=''
        # Priority -> P1
        if parts[3].strip() != "P1":
            parts[3] = " P1 "
            fixes.append("docs/backlog/index.md: 001 row Priority -> P1")

        # Stage cell -> `1 - Concept`
        stage_cell = parts[6].strip()
        if stage_cell != "1 - Concept":
            if stage_cell in ("1", "1 -", "1 Concept"):
                parts[6] = " 1 - Concept "
                fixes.append('docs/backlog/index.md: 001 row Stage -> "1 - Concept"')
            else:
                errors.append(
                    f'docs/backlog/index.md: 001 row Stage cell is `{stage_cell}`, '
                    f'expected `1 - Concept`'
                )

        # Timestamps -> YYYY-MM-DD HH:MM
        for idx, label in ((7, "Created"), (8, "Updated")):
            cell = parts[idx].strip()
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", cell):
                parts[idx] = f" {cell} 00:00 "
                fixes.append(
                    f"docs/backlog/index.md: 001 row {label} -> `{cell} 00:00`"
                )

        lines[i] = "|".join(parts)

    txt = "\n".join(lines)
    if txt != orig:
        f.write_text(txt, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: init-verify.py <project-root>", file=sys.stderr)
        sys.exit(2)
    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        sys.exit(2)
    sys.exit(verify(root))
