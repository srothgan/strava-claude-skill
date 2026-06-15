# Evaluations

Per [Anthropic's skill-authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices),
a skill should ship with evaluations: representative tasks plus the behavior a
correct run must exhibit. These are for maintainers/contributors to verify the
skill against a live Strava MCP — they are **not** loaded by the skill at runtime
(kept out of `strava/` so they cost no context).

There's no built-in runner; execute each query in a session with the skill and
the Strava MCP loaded, then check the expected behaviors by hand.

---

## Eval 1 — Single-run analysis with correct units

**Query:** "Analyze my most recent run."

**Expected behavior:**
- Reads `get_athlete_profile` (units) and uses `get_activity_performance` (and
  optionally `get_activity_streams`) for the latest run from `list_activities`.
- Reports **pace** (min/km or min/mile per preference), never raw m/s.
- Cross-references HR against `get_athlete_zones` to label intensity.
- If intervals, summarizes per-rep from `laps`; flags missing HR if absent.
- Does not invent fields that weren't returned.

## Eval 2 — Weekly load review with explicit unit request

**Query:** "How did my training load trend over the last 4 weeks? Use miles."

**Expected behavior:**
- Uses `list_activities` with a `range_start`/`range_end` covering ~4 weeks
  (paginates via `end_cursor` if needed).
- Converts distances to **miles** as requested (overriding stored preference).
- Aggregates weekly volume + `relative_effort` (load) and names the window.
- Comments on easy/hard distribution and progression (~10%/deload) with caveats.
- Treats non-distance sports (distance 0) correctly — no bogus pace.

## Eval 3 — Zones translated to usable targets, estimates flagged

**Query:** "What are my heart-rate and pace zones? Give paces in min/km."

**Expected behavior:**
- Calls `get_athlete_zones`.
- Presents 5 HR zones as bpm ranges.
- Converts run-zone **m/s** boundaries into **pace** ranges (min/km), correctly
  noting faster zones = lower pace.
- If `ftp_is_estimated` / `is_estimated` / estimated max HR, says the values are
  approximate rather than presenting them as precise.

## Eval 4 — Graceful handling of thin/absent data

**Query:** "Compare my power zones and FTP progression." (athlete may have no power meter)

**Expected behavior:**
- If no power data / FTP is estimated, says so plainly and explains what can't be
  concluded, rather than fabricating watts or a progression.
- Suggests the HR/pace-based alternatives the data does support.
