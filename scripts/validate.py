#!/usr/bin/env python3
"""Validate this repo's Claude skill(s) and plugin/marketplace manifests.

Self-contained (Python 3 stdlib only) so CI needs no third-party action.
Checks, per Anthropic's skill-authoring rules:
  - every skills/*/SKILL.md has valid YAML-ish frontmatter with name + description
  - name is kebab-case, 1-64 chars, starts with a letter, no reserved words
  - description is 20-1024 chars
  - reference links in SKILL.md resolve to files that exist
  - .claude-plugin/marketplace.json and plugin.json are valid JSON with required fields
Exits non-zero on any error. Run locally: python scripts/validate.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors: list[str] = []
warnings: list[str] = []

NAME_RE = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
RESERVED = {"anthropic", "claude"}
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Minimal frontmatter parser: top-level `key: value`, supports YAML `>-` folding."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end].strip("\n")
    data: dict[str, str] = {}
    key: str | None = None
    buf: list[str] = []

    def flush() -> None:
        if key is not None:
            data[key] = " ".join(p.strip() for p in buf if p.strip())

    for line in block.splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m and not line.startswith((" ", "\t")):
            flush()
            key, rest = m.group(1), m.group(2).strip()
            buf = []
            if rest and rest not in (">-", ">", "|", "|-"):
                buf = [rest]
        else:
            buf.append(line)
    flush()
    return data


def check_skill(skill_md: Path) -> None:
    rel = skill_md.relative_to(ROOT)
    text = skill_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is None:
        err(f"{rel}: missing or malformed YAML frontmatter")
        return

    name = fm.get("name", "")
    desc = fm.get("description", "")

    if not name:
        warn(f"{rel}: no `name` (allowed for plugin skills; folder name is used)")
    else:
        if not NAME_RE.match(name):
            err(f"{rel}: name '{name}' must be kebab-case, start with a letter, <=64 chars")
        if name.lower() in RESERVED:
            err(f"{rel}: name '{name}' uses a reserved word")

    if not desc:
        err(f"{rel}: missing `description`")
    else:
        if len(desc) < 20:
            err(f"{rel}: description too short ({len(desc)} chars; need >=20)")
        if len(desc) > 1024:
            err(f"{rel}: description too long ({len(desc)} chars; max 1024)")

    # Reference links must point at existing files (skip URLs/anchors).
    for target in LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        path = (skill_md.parent / target.split("#", 1)[0]).resolve()
        if not path.exists():
            err(f"{rel}: broken reference link -> {target}")


def check_json(path: Path, required: list[str]) -> dict | None:
    rel = path.relative_to(ROOT)
    if not path.exists():
        err(f"{rel}: missing")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"{rel}: invalid JSON ({e})")
        return None
    for field in required:
        if field not in data:
            err(f"{rel}: missing required field '{field}'")
    return data


def main() -> int:
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    if not skills:
        err("no skills found under skills/*/SKILL.md")
    for s in skills:
        check_skill(s)

    check_json(ROOT / ".claude-plugin" / "plugin.json", ["name", "description"])
    mkt = check_json(ROOT / ".claude-plugin" / "marketplace.json", ["name", "owner", "plugins"])
    if mkt and not isinstance(mkt.get("plugins"), list):
        err(".claude-plugin/marketplace.json: 'plugins' must be an array")

    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        print(f"\nValidation FAILED with {len(errors)} error(s).")
        return 1
    print(f"\nValidation passed ({len(skills)} skill(s) checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
