# Strava MCP — tools, parameters & data reference

Field-by-field reference for every Strava MCP tool. **All numeric values are
metric** unless noted. Example values below are illustrative, not real data.
Convert to km/miles/pace for display (see SKILL.md "Conversions cheat sheet").

A general rule across the API: **optional fields are omitted when unavailable**
(no HR monitor, no power meter, no GPS, etc.). Never assume a key exists —
check before reading it.

---

## `health`
- **Params:** none.
- **Returns:** `{"ok": true}`. Liveness/connectivity check.

## `eligibility`
- **Params:** none.
- **Returns:** `{"eligible": bool, "message": str}`. If only this tool is visible,
  the full toolset hasn't loaded — advise the user to start a new chat.

## `get_athlete_profile`
- **Params:** none.
- **Returns:** identity and preferences:
  - `id` (int), `first_name`, `last_name`
  - `measurement_preference` — `"Metric"` or `"Imperial"`. Drives display units.
  - `gender`, `weight` (kg)
  - `location` — `{ city, state, country }` (any may be absent)
  - `current_focus` (when set) — `{ id, focus_type (e.g. "TrainForEvent"),
    open_text (free-text goal), expires_at_local (ISO local datetime) }`
- **Use:** call early in any analysis to fix units and understand the goal.

## `get_athlete_zones`
- **Params:** `as_of_date` (optional, `YYYY-MM-DD`) for historical zones; omit for current.
- **Returns:**
  - `heart_rate_zones` — array of **5** `{min, max}` bpm objects (top zone has
    `min` only, open-ended). `heart_rate_zone_source` (e.g. `"MaxHeartRate"`).
  - `power_zones` — array of **7** `{min, max}` watt objects (cycling only,
    requires FTP). `power_zone_source` (e.g. `"EstimatedFtpFromPower"`).
  - `ftp` (watts), `ftp_is_estimated` (bool) — if true, power data is approximate.
  - `run_zones` — array of **5** `{min, max}` boundaries **in m/s (speed)** →
    convert to pace ranges. `run_zone_source` (e.g. `"PerformancePredictions"`,
    `"RacePace"`).
  - `sample_race_pace` (when `run_zone_source` is RacePace) —
    `{ best_effort_type, time (formatted), is_estimated }`.
- **Gotcha:** run-zone bounds are speeds, not paces — faster zones have *higher*
  m/s but *lower* (faster) pace. Convert carefully and label "faster/slower".

## `list_activities`
- **Params:**
  - `first` (int, default 30, max 100)
  - `after` (cursor — pass `end_cursor` from a previous page)
  - `ordering` — `"StartDateLocalDesc"` (default, newest first) or `"StartDateLocalAsc"`
  - `range_start` / `range_end` — ISO LocalDateTime, e.g. `2025-01-01T00:00:00`,
    inclusive
  - `include_polyline` (bool) — adds a reduced encoded polyline per activity
    (off by default to cut size; only request if mapping/route is needed)
  - `include_tags` (bool) — adds `activity_tags`, `is_commute`, `is_trainer`
- **Returns:** `{ activities: [...], has_next_page, end_cursor }`. Each activity:
  - `id` (string), `name`, `description`, `sport_type`, `start_local` (naive local ISO)
  - `gear_id` (string; matches `gear_id.id` from `get_gear`)
  - `is_trainer` / `is_commute` / `activity_tags` (only with `include_tags`)
  - `summary`:
    - `distance` (m), `moving_time` / `elapsed_time` (s), `elevation_gain` (m)
    - `avg_speed` / `max_speed` (m/s) — convert to pace (run) or km/h·mph (ride)
    - `cadence`, `relative_effort` (Strava's HR-based effort score; absent without HR)
    - `total_calories`, `kudos_count`, `achievement_count`, `pr_count`
- **Gotcha:** non-distance sports return zeros for distance/speed/elevation.
- **Paging loop:** while `has_next_page`, call again with `after = end_cursor`.

## `get_activity_performance`
- **Params:** `activity_id` (string, required).
- **Returns:** rich per-activity stats:
  - `has_heartrate`, `has_device_watts` (booleans, inferred from stream presence)
  - `average_heartrate`, `max_heartrate` (bpm); `average_watts`, `average_cadence`
  - `calories`, `perceived_exertion` (when logged)
  - `pr_achievements` — `[{ achievement_type (e.g. SegmentPersonalRecordGold),
    entity_id, rank }]`
  - `segment_efforts` — `[{ id, segment_id, segment_name, distance (m),
    elev_gain (m), elapsed_time (s), moving_time (s), avg_hr }]`
  - `best_efforts` (runs) — `[{ id, name, type_value (e.g. Fastest5k),
    display_text (e.g. "5K"), value (SECONDS) }]` → format value as m:ss
  - `laps` — `[{ elapsed_time, moving_time (s), start_index, end_index,
    distance (m), elevation_gain (m), max_speed (m/s), avg_hr, max_hr,
    avg_grade (fraction; ×100 for %) }]`. `start_index`/`end_index` map laps onto
    the stream arrays from `get_activity_streams`.
- **Use:** the primary tool for analyzing a single workout's structure (intervals
  show up clearly as alternating hard/easy laps with HR swings).

## `get_activity_streams`
- **Params:**
  - `activity_id` (string, required)
  - `streams` (array, required) — any of: `time` (s from start), `location`
    (`[lat,lng]` pairs), `heart_rate` (bpm), `watts`, `cadence` (rpm/spm),
    `distance` (cumulative m), `altitude` (m), `velocity_smooth` (m/s),
    `grade_smooth` (% grade), `moving` (bool), `temp` (°C)
  - `resolution` (positive int) — granularity; omit for maximum
- **Returns:** an object of **index-aligned arrays**, one per requested stream that
  exists. Example: `{ time:[...], heart_rate:[...], distance:[...] }`.
- **Gotchas:**
  - Unknown stream names are silently ignored; missing streams are omitted —
    always check which keys came back.
  - Sample `i` across all returned arrays describes the same moment.
  - Use `time`/`distance` as the x-axis. Pair with `laps[].start_index/end_index`
    from `get_activity_performance` to compute per-interval splits.
  - Keep `resolution` modest unless you need full fidelity (responses get large).

## `get_gear`
- **Params:** `gear_types` (optional array: `"Bike"`, `"Shoe"`). Omit for all.
- **Returns:** `{ gear: [...] }`. Each item:
  - `gear_id` — `{ id (matches activity `gear_id`), gear_type }`
  - `name`, `description`, `retired` (bool), total `distance` (m)
  - Bikes also: `weight`, `frame_type`. Shoes also: `brand`, `model_name`.
- **Gotcha:** returns `{ "gear": [] }` if the athlete has registered none. Use
  cumulative `distance` for replacement guidance (e.g. shoes ~500–800 km).

## `get_club_info`
- **Params:** `clubs_first` (default 50), `clubs_after` (club cursor),
  `events_first` (events per club, default 10).
- **Returns:** `{ clubs: [...], has_next_page }`. Each club: name, `sport_type`,
  sports list, member count, and upcoming event occurrences (title, date/time,
  address, location, sport types, start/end, recurrence rule). Cursor pagination
  for both clubs and per-club events.
- **Gotcha:** `{ "clubs": [], "has_next_page": false }` if the athlete has none.

## `get_training_plan`
- **Params:** none.
- **Returns:** **may be a referral message/URL to a partner coaching product**
  rather than structured plan data. Do not present it as a generated plan. If the
  user wants an actual plan, build one from their data using
  `training-interpretation.md`, and optionally share the link.

## Auth tools (`authenticate` / `complete_authentication`)
- Used only to connect the MCP when it isn't yet authorized. If data tools fail
  with an auth error, run `authenticate` to get a URL, have the user approve, then
  `complete_authentication`. In a healthy session you won't need these.
