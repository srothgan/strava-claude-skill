# Strava Skill for Claude

[![Validate skill](https://github.com/srothgan/strava-claude-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/srothgan/strava-claude-skill/actions/workflows/validate.yml)

A [Claude skill](https://docs.claude.com/en/docs/claude-code/skills) that makes
Claude genuinely good at working with your **Strava MCP** data — both *fetching*
it correctly and *interpreting* it like a knowledgeable endurance coach.

It pairs an accurate, field-level understanding of what the Strava MCP returns
(exact shapes, units, and quirks) with practical training-science guidance (zones,
relative effort, weekly load, trends, race readiness) and Claude skills best
practices (a tight `SKILL.md` plus progressively-disclosed reference files).

## Requirements

- Claude with [Skills](https://docs.claude.com/en/docs/claude-code/skills) support
  (Claude Code, Claude Desktop, or the API with skills enabled).
- A connected **Strava MCP** server exposing tools such as `list_activities`,
  `get_activity_performance`, `get_activity_streams`, `get_athlete_profile`,
  `get_athlete_zones`, `get_gear`, `get_club_info`, `get_training_plan`,
  `health`, and `eligibility`. (The skill matches whatever prefix your server
  registers them under.)

## Install

### Option A — Claude Code plugin marketplace (recommended)

This repo is itself a Claude Code marketplace, so installation and updates are
one command each:

```text
/plugin marketplace add srothgan/strava-claude-skill
/plugin install strava-coach@srothgan-skills
```

Update later with `/plugin marketplace update srothgan-skills`. The skill is
namespaced as `strava-coach` once installed.

### Option B — `npx skills` (cross-agent, one command)

The skill follows the open Agent Skills spec, so the
[`skills` CLI](https://github.com/vercel-labs/skills) installs it straight from
this repo into Claude Code and other agents (Cursor, Copilot, Codex, …):

```bash
npx skills add srothgan/strava-claude-skill
```

### Option C — manual copy (any Skills-capable Claude)

Copy the skill folder into your skills directory:

- **macOS / Linux:** `~/.claude/skills/`
- **Windows:** `%USERPROFILE%\.claude\skills\`

```bash
git clone https://github.com/srothgan/strava-claude-skill.git
cp -r strava-claude-skill/skills/strava-coach ~/.claude/skills/
```

```powershell
git clone https://github.com/srothgan/strava-claude-skill.git
Copy-Item -Recurse strava-claude-skill\skills\strava-coach "$env:USERPROFILE\.claude\skills\"
```

You should end up with `~/.claude/skills/strava-coach/SKILL.md`. Restart Claude so it
picks up the new skill.

### Option D — project skill

Drop the `skills/strava-coach/` folder into your project's `.claude/skills/` directory
to ship it with a repo.

## Usage

Two ways to use it once your Strava MCP is connected:

**Just ask naturally** — Claude triggers the skill automatically:

- "Analyze my last run."
- "How did my training load trend over the last 4 weeks? Use miles."
- "What are my heart-rate and pace zones, in min/km?"
- "Am I on track for my goal race?"
- "Were my intervals on Tuesday consistent?"

**Or invoke it explicitly as a slash command:**

```text
/strava-coach              # manual-copy or project install
/strava-coach:strava-coach # plugin install (namespaced plugin:skill)
```

Either way, Claude picks the right tool, confirms the unit system, converts
correctly (km or miles, pace), and interprets the numbers with appropriate caveats.

## Why

Strava MCP responses are easy to misread. Values come back as raw numbers —
speeds as m/s, run-pace zones as *speed* boundaries, distances and elevation as
bare figures — and **you can't safely assume which measurement system they're in**:
it tracks the athlete's account/server settings, so one user's data may be metric
and another's imperial. The MCP also silently omits missing data (no HR monitor →
no heart-rate fields). This skill teaches Claude to **confirm the unit system from
the athlete's profile**, sanity-check magnitudes, convert correctly (km **or**
miles, pace per km/mile), and never guess — so it interprets the numbers like a
coach instead of mislabeling them.

## What's inside

```
strava-claude-skill/
├── .claude-plugin/
│   ├── marketplace.json                  # makes this repo an installable Claude Code marketplace
│   └── plugin.json                        # the "strava-coach" plugin manifest
├── skills/
│   └── strava-coach/
│       ├── SKILL.md                       # entry point: tool map, gotchas, conversions, workflows
│       └── references/
│           ├── tools-and-data.md          # every tool: params, output fields, units, quirks
│           └── training-interpretation.md # zones, load, trends, race readiness, honesty checklist
├── scripts/validate.py                    # stdlib-only validator (frontmatter, links, manifests)
├── .github/workflows/validate.yml         # CI: runs the validator on push/PR
├── evaluations.md                         # test scenarios for maintainers (not loaded at runtime)
├── LICENSE
└── README.md
```

Claude reads `SKILL.md` first and pulls in a reference file only when a task needs
the detail — keeping context lean. The structure follows Anthropic's
[skill-authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
(concise entry point, one-level-deep references, third-person description,
shipped evaluations).

## Design principles

- **Grounded:** built from the Strava MCP's actual responses — real fields, real
  units, real edge cases — not assumptions.
- **Progressive disclosure:** lean `SKILL.md`, deep detail on demand.
- **Honest coaching:** separates measured from estimated data, names the analysis
  window, and avoids medical claims or race-result guarantees.

## Contributing

Issues and PRs welcome — especially corrections if your Strava MCP build returns
fields not documented here. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full
guide. In short: keep `SKILL.md` tight, push detail into `references/`, run
`python scripts/validate.py` (must pass), and sanity-check against the scenarios
in [`evaluations.md`](evaluations.md) with a live Strava MCP.

## License

[MIT](LICENSE)

---

*Not affiliated with or endorsed by Strava. "Strava" is a trademark of Strava, Inc.*
