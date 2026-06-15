# Strava Coach for Claude

[![Validate skill](https://github.com/srothgan/strava-claude-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/srothgan/strava-claude-skill/actions/workflows/validate.yml)

From raw Strava records to confident training insight.

Strava Coach helps you turn activity feeds into clear next actions: load trends, zone fidelity, interval consistency, and race-readiness signals, with unit handling and interpretation that respects real-world data gaps.

## Built for athletes first

- Ask better questions about your training
- Get interpretations you can use for planning
- Avoid common reading errors across units and missing signals

No dashboards. No reconfiguration. Just conversation and context-aware analysis.

## Quick start

### 1) Install

### Option A — Claude Code marketplace (recommended)

```text
/plugin marketplace add srothgan/strava-claude-skill
/plugin install strava-coach@srothgan-skills
```

```text
/plugin marketplace update srothgan-skills
```

### Option B — `npx skills`

```bash
npx skills add srothgan/strava-claude-skill
```

### Option C — Manual copy

Copy the skill directly when you want full control:

- Global install: `~/.claude/skills/` (macOS/Linux), `%USERPROFILE%\\.claude\\skills\\` (Windows)
- Project install: `<repo>/.claude/skills/`

```bash
git clone https://github.com/srothgan/strava-claude-skill.git
cp -r strava-claude-skill/skills/strava-coach ~/.claude/skills/
mkdir -p .claude/skills
cp -r strava-claude-skill/skills/strava-coach .claude/skills/
```

```powershell
git clone https://github.com/srothgan/strava-claude-skill.git
Copy-Item -Recurse strava-claude-skill\skills\strava-coach "$env:USERPROFILE\.claude\skills\"
New-Item -ItemType Directory -Force -Path .claude\skills | Out-Null
Copy-Item -Recurse strava-claude-skill\skills\strava-coach ".claude\skills\"
```

Restart Claude after a manual install.

### 2) Connect Strava MCP

Use a Strava MCP server that exposes:

- `list_activities`
- `get_activity_performance`
- `get_activity_streams`
- `get_athlete_profile`
- `get_athlete_zones`
- `get_gear`
- `get_club_info`
- `get_training_plan`
- `health`
- `eligibility`

### 3) Ask

You can ask naturally, for example:

- “Summarize my last 5 runs and tell me what to improve.”
- “Am I on track for my upcoming half marathon?”
- “Compare this week and last week by training load using miles.”
- “Are my Tuesday intervals on pace and effort?”

## Why this is different

Strava exports are powerful, but easy to misread:

- Units can vary by athlete setup.
- Speed values may appear as raw m/s.
- Zone boundaries can look like pace, speed, or heart-rate ranges depending on context.
- Missing sensors result in missing fields without clear errors.

Strava Coach applies a coaching lens instead of a naive stats layer:

- Detects and confirms unit system from profile context.
- Converts consistently to km or miles, pace per km or mile.
- Preserves uncertainty when values are estimated or partial.
- Distinguishes measured input from inferred insights.

## What you can ask

### Race preparation

- Pace strategy, taper readiness, and effort distribution checks.
- Last-mile fatigue indicators across long efforts.
- Trend-aware readiness notes before hard days.

### Consistency and load

- Weekly load and fatigue progression checks.
- Recovery-informed recommendations when volume or intensity spikes.
- Missed training pattern detection from activity cadence.

### Quality and form

- Interval stability and target adherence checks.
- Zone adherence and drift analysis.
- Pace-effort mismatches when data suggests over-racing.

## Reliability model

- Always confirms assumptions before translating raw fields into recommendations.
- Applies explicit caveats when a reading is partial, stale, or estimated.
- Prioritizes measurable signals and names uncertainty clearly.
- No health or medical claims; no guaranteed race outcomes.

## What’s inside

```text
strava-claude-skill/
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── skills/
│   └── strava-coach/
│       ├── SKILL.md
│       └── references/
│           ├── tools-and-data.md
│           └── training-interpretation.md
├── scripts/
│   └── validate.py
├── .github/workflows/validate.yml
├── evaluations.md
├── LICENSE
└── README.md
```

`SKILL.md` remains the primary entry point and loads references only when deeper context is needed.

## Requirements

- Claude with skills support (Claude Code, Claude Desktop, or API with skills enabled).
- A Strava MCP server with access to the tools listed above.

## Contributing

Contributions are welcome.

Please see [CONTRIBUTING.md](CONTRIBUTING.md). In short:

- Keep `SKILL.md` focused and concise.
- Move detailed behavior into `references/`.
- Run `python scripts/validate.py`.
- Validate scenarios in [`evaluations.md`](evaluations.md) against a live Strava MCP.

## License

[MIT](LICENSE)

---

Not affiliated with or endorsed by Strava. "Strava" is a trademark of Strava, Inc.
