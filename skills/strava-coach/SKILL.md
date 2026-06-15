---
name: strava-coach
description: >-
  Accesses and interprets an athlete's Strava data via the Strava MCP, with a
  coach's perspective. Use whenever the user asks about their runs, rides, swims,
  or workouts, training load, heart-rate/power/pace zones, segments, PRs, gear,
  clubs, race readiness, or wants analysis, trends, or training advice from their
  Strava history. Covers which tool to call, the exact data shapes and units
  returned, the metric-to-km/miles/pace conversions the data requires, and how to
  interpret the numbers (zones, relative effort, weekly load, timelines) without
  over-claiming.
---

# Strava: data access + coaching interpretation

This skill makes you effective with the Strava MCP. It has two jobs:
1. **Get the right data** with the right tool, and read its exact shape/units correctly.
2. **Interpret it responsibly** — like a knowledgeable coach, not a hype machine.

Strava MCP tools are typically prefixed `mcp__claude_ai_Strava__` (the exact
prefix depends on how the server is registered; match the available tool names).
There is usually an auth pair (`authenticate` / `complete_authentication`) used
only when the MCP is not yet connected.

## First moves

- If you're unsure access works, call `health` (returns `{"ok": true}`) or
  `eligibility`. If `eligibility` says you only see the eligibility tool, tell
  the user to start a new chat — the full toolset can load per-session.
- **Always read the athlete profile early** for any analysis. `get_athlete_profile`
  gives `measurement_preference` (Metric/Imperial), plus identity, body metrics,
  and `current_focus` (a stated training goal + an `expires_at_local` date when
  present). Tailor units and advice to these.
- **Don't assume the unit system — confirm it.** Read `measurement_preference`
  (Metric/Imperial) from the profile; it reflects the athlete's account settings
  and is your closest source of truth for how values come back. Do not hardcode
  "it's metric": sanity-check magnitudes, and **convert to whatever unit the user
  asks for** (km or miles), defaulting to the athlete's preference when unspecified.

## Tool map — pick the right one

| Need | Tool |
|------|------|
| List/scan workouts, date ranges, totals | `list_activities` |
| Deep stats for ONE activity (HR, watts, laps, segments, PRs, best efforts) | `get_activity_performance` |
| Raw time-series for ONE activity (charts, splits, pacing, HR drift) | `get_activity_streams` |
| Athlete identity, units, body metrics, goal | `get_athlete_profile` |
| HR / power / run-pace zones, FTP | `get_athlete_zones` |
| Bikes & shoes, mileage, retirement | `get_gear` |
| Clubs & upcoming events | `get_club_info` |
| A real coached plan | `get_training_plan` (⚠ may return a partner referral link, not data) |
| Connectivity / access | `health`, `eligibility` |

## Critical gotchas (read before trusting numbers)

- **Don't hardcode the unit system; confirm it per athlete.** Values are raw
  numbers whose unit system tracks the athlete's account settings, so it can be
  metric for one user and imperial for another — never assume. Check
  `measurement_preference`, sanity-check magnitudes, and convert to the unit the
  user asked for (km **or** miles). Typical metric forms are `distance`/
  `elevation` in metres, `*_speed` and run-zone bounds in m/s, `temp` in °C; an
  imperial account may surface miles/feet/°F — verify rather than trust the label.
- **Speed is not pace.** Speed values (e.g. m/s) read backwards from pace: faster =
  higher speed but *lower* (faster) pace. For runs, always convert speed to pace
  before showing — never show a runner a raw speed like "2.47 m/s".
- **Non-distance sports** (WeightTraining, Elliptical, Yoga, etc.) return
  `distance:0`, `avg_speed:0`, `elevation_gain:0`. Don't compute pace/speed for them.
- **IDs are strings.** Pass `activity_id` as a string.
- **Streams are index-aligned arrays.** `time[i]`, `heart_rate[i]`, `distance[i]`
  all describe the same sample. **Missing streams are silently omitted** and
  unknown stream names are silently ignored — check which keys actually came back
  (e.g. cadence/watts are absent if the device didn't record them).
- **`resolution`** downsamples streams (higher integer = more points; omit for
  max granularity). Use a low value (e.g. 20–100) for trend/shape; full only when
  you truly need every sample.
- **Pagination is cursor-based.** `list_activities` → `has_next_page` +
  `end_cursor`; pass it back as `after`. `get_club_info` uses `clubs_after`.
- **HR/effort fields require a HR signal.** `relative_effort`, `average_heartrate`,
  etc. are absent/zero without a monitor. `get_activity_performance` exposes
  `has_heartrate` / `has_device_watts` (inferred from stream presence).
- **`ftp_is_estimated` / `is_estimated`** — when true, treat FTP, power zones, and
  any sample race pace as rough. Say so; don't build precise prescriptions on them.
- **`get_training_plan` may be a referral**, not data. Don't pretend it returned a
  plan; if the user wants a plan, build one from their data (see
  `references/training-interpretation.md`) or surface the link.

## Conversions cheat sheet

Always state which unit you used. These formulas assume **metric** raw values (the
common case); if you've confirmed an imperial account or a magnitude looks off,
adjust the source unit accordingly before converting.

- **Pace min/km** from speed (m/s): `sec_per_km = 1000 / speed`; format `m:ss`.
  e.g. `2.473 m/s → 6:44 /km`.
- **Pace min/mile** from speed (m/s): `sec_per_mile = 1609.34 / speed`.
  e.g. `2.473 m/s → 10:51 /mi`.
- **Distance**: km = metres / 1000; miles = metres / 1609.34.
- **Elevation**: feet = metres × 3.281.
- **Speed (cycling display)**: km/h = m/s × 3.6; mph = m/s × 2.237.
- **Run-zone bounds** are m/s → convert each to a pace range (per km and/or mile).
- **`best_efforts[].value`** (runs) = **seconds** → format `m:ss` (e.g. 1914 → 31:54).
- **Times** (`moving_time`, `elapsed_time`, and the per-lap/effort times) = seconds.
- **`start_local`** = naive local-time ISO (already the athlete's local clock).
- **Weight** is kg; convert to lb = kg × 2.205 if Imperial.

## Core workflows

**Analyze one workout** → `get_activity_performance` (laps, HR, segments, PRs,
best efforts) + optionally `get_activity_streams` for pacing/HR-drift detail.
Cross-reference HR against `get_athlete_zones` to label intensity per lap/segment.

**Weekly / load review** → `list_activities` with `range_start`/`range_end`
(ISO LocalDateTime). Sum distance & moving_time, track `relative_effort` as the
load proxy, and check the easy/hard balance against zones. See interpretation ref.

**Race readiness for a goal** → read `current_focus` + `expires_at_local`, pull
recent activities, compare current `best_efforts`/paces to the target, and
sanity-check the timeline. Be honest about gaps.

**Zone-based prescription** → `get_athlete_zones`, convert run zones to paces (km
and mile) and HR zones to bpm ranges, then give workout targets. Flag estimates.

## Going deeper

- **`references/tools-and-data.md`** — exact parameters, every output field, units,
  and quirks for each tool. Read it before parsing an unfamiliar response.
- **`references/training-interpretation.md`** — how to turn the numbers into sound
  coaching: zone models, relative effort, weekly load & progression, trend
  windows, timelines, and how to advise without overstepping the data.

## Tone & honesty

Be a careful coach. Distinguish measured vs estimated data. State the analysis
window. Don't diagnose medical issues or guarantee race outcomes. When data is
thin (no HR, few activities, estimated FTP), say what you can and can't conclude.
