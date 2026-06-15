# Interpreting Strava data like a coach

How to turn the raw numbers into sound, honest training insight. Pair this with
`tools-and-data.md` (what the fields mean) and SKILL.md (which tool, what units).

Guiding principle: **be useful but calibrated.** Always state your analysis
window, separate measured from estimated data, and avoid medical claims or race
guarantees. Endurance training has large individual variation -- frame advice as
general principles, not prescriptions for this specific person's physiology.

---

## 1. Intensity zones

The MCP returns three zone systems from `get_athlete_zones`. Convert them, then
use them to *label* every workout's intensity.

### Heart-rate zones (5-zone)

Boundaries in bpm; the top zone is open-ended (`min` only). A common reading:

| Zone | Common name | Feel | Typical use |
|------|-------------|------|-------------|
| Z1 | Recovery | very easy, conversational | warm-up, recovery |
| Z2 | Endurance / aerobic | easy, can talk in sentences | the bulk of base training |
| Z3 | Tempo | comfortably hard | "grey zone" -- use sparingly |
| Z4 | Threshold | hard, short phrases only | lactate threshold work |
| Z5 | VO2max / anaerobic | maximal | short intervals |

`heart_rate_zone_source` tells you how they were derived (`MaxHeartRate`,
`Threshold`, etc.). If derived from an estimated max HR, treat boundaries as
approximate. **HR lags effort** (~30-60 s) and drifts up with heat, fatigue,
caffeine, and dehydration -- don't over-interpret single-point HR.

### Power zones (cycling, 7-zone)

Watt boundaries derived from FTP. If `ftp_is_estimated` is true, the zones are
rough -- say so and avoid precise watt prescriptions. The classic 7-zone model:
Active Recovery, Endurance, Tempo, Threshold, VO2max, Anaerobic, Neuromuscular.
Power is the most objective intensity metric when a meter is present
(`has_device_watts` = true).

### Run-pace zones (5-zone)

**Boundaries are speeds, not paces** (m/s on metric accounts -- verify the unit
system) -- convert each to pace per km and per mile. A higher speed bound is a
*faster* (lower) pace. `run_zone_source` such as
`PerformancePredictions` or `RacePace` indicates how they were modeled; if a
`sample_race_pace` is flagged `is_estimated`, the zones inherit that uncertainty.

When analyzing a workout, compare each lap/segment `avg_hr` (and pace) to these
zones to classify it as easy / endurance / tempo / threshold / VO2.

## 2. Relative Effort (load proxy)

`relative_effort` (the metric that replaced the old "Suffer Score") is Strava's
HR-based session-load number. It's built on **Bannister's TRIMP model**
(co-developed with Marco Altini): time-in-HR-zone weighted by progressively
larger coefficients per zone, so it **weights intensity over duration** -- a
20-minute interval session can score like a multi-hour easy ride. Strava then
**normalizes it against a global dataset**, so it's intentionally designed to be
comparable across sports (run/ride/swim/row) and even between athletes.

How to use it:

- It's the best single **load** proxy the MCP exposes. Sum it for **weekly load**
  and track the trend; also fine for cross-sport session comparison.
- **It's only as accurate as the athlete's max HR.** A wrong/estimated max HR
  skews RE (and the zones derived from it). If `heart_rate_zone_source` implies an
  estimate, caveat accordingly. Optical-wrist HR is noisier than a chest strap.
- It's absent/zero without HR -- for non-HR or strength sessions, fall back to
  duration and `total_calories` as a crude load stand-in.
- Avoid quoting fixed "easy vs hard" point thresholds as universal -- RE scales
  with the individual and the session. Strava itself judges *weekly* RE against a
  ~3-week rolling average (in-range = sustainable; well above = needs recovery;
  below = taper/recovery). Mirror that relative framing.

If power is present you can mention TSS-style concepts, but the MCP doesn't return
TSS or Fitness/Freshness values -- don't fabricate them.

## 3. Weekly load & progression

From `list_activities` over a date range (`range_start`/`range_end`):

- **Volume:** sum `distance` (-> km/mi) and `moving_time` (-> h) per week, per sport.
- **Load:** sum `relative_effort` per week; track the week-over-week trend.
- **Distribution:** classify sessions by zone. A widely used target is
  **polarized / 80-20**: ~80% of *time* easy (Z1-Z2), ~20% hard (Z4-Z5), with
  little time stuck in Z3. Flag if the athlete lives in the "grey zone". Practical
  metric choice: judge **easy** days by **HR** (e.g. keep below ~77% of max HR /
  upper Z2) since that's where people accidentally drift too hard; judge **hard
  intervals** by **pace/power**, because HR lags 30-60 s and under-reads short
  reps. The most common error is easy days run too hard -- call it out.
- **Progression:** the conventional guideline is to grow weekly volume by no more
  than ~10% and to insert a lighter (recovery/deload) week roughly every 3-4
  weeks. Big single-week jumps raise injury risk -- call them out.
- **Consistency** beats heroics: note frequency and gaps, not just peak sessions.

### Acute:Chronic Workload Ratio (ACWR) -- use with caution

You can compute ACWR = (last 7-day load) / (rolling 28-day average weekly load),
using `relative_effort` (or distance/time) as the load measure. A commonly cited
"sweet spot" is ~0.8-1.3, with very high ratios flagged as risk. **But be honest
about its limits:** the evidence is contested -- recent reviews and RCTs found
little to no predictive value for injury. Treat ACWR as one rough signal of
*ramp rate*, not a verdict. Never tell someone they "will" get injured from it.

Present load as a small table (week -> volume, time, load, %easy/hard) when you
have several weeks. Always name the window ("last 4 full weeks").

## 4. Trend windows

Pick the window to the question:

- **Acute:** last 7 days -- current fatigue/freshness.
- **Chronic:** last 28-42 days -- fitness base. A rising chronic load with
  controlled acute load is the healthy direction; acute spiking far above chronic
  is a warning sign (overreaching/injury risk).
- **Block:** 4-week blocks -- see periodization (build vs recovery).
- **Long arc:** season/year -- `best_efforts`, PRs, and pace at a given HR over
  time show fitness change. "Faster pace at the same HR" = improving aerobic
  fitness; "higher HR at the same pace" = fatigue or detraining (or heat).

## 5. Single-workout analysis patterns

- **Intervals:** `laps` alternate hard/easy with clear HR swings; report per-rep
  pace/power and HR, plus how repeatable they were (did pace fade or HR climb?).
- **HR drift / decoupling:** in a steady run/ride, compare HR (and pace) over the
  first vs second half from `get_activity_streams`. Rising HR at steady pace =
  aerobic decoupling (fatigue, heat, or fitness gap on long efforts).
- **Negative/positive split:** compare first vs second-half pace via streams.
- **Segments & PRs:** `segment_efforts` and `pr_achievements` highlight standout
  efforts; `best_efforts` (runs) give clean time trials over standard distances.
- Map laps onto streams using `start_index`/`end_index`.

## 6. Race readiness for a goal

When `current_focus` describes an event (and `expires_at_local` gives a date):

1. Identify target distance/time from the goal text.
2. Pull recent `best_efforts` and representative race-pace efforts.
3. Compare current fitness to the target; estimate the gap honestly.
4. Check the **timeline**: weeks remaining vs the volume/intensity needed, with a
   **taper** (reduce volume ~30-50% over the final 1-2 weeks while keeping some
   intensity) before race day.
5. Note limiters (load too low/high, no long runs, no goal-pace work, lots of
   grey-zone, recent gaps).

Frame readiness as a range and a plan, never a guarantee.

## 7. Sport-type handling

- Runs: report **pace** (per km and/or mile), HR, cadence; use run zones.
- Rides: report **speed** (km/h or mph) and **power** (if `has_device_watts`); use
  power/HR zones.
- Swims: distance/time/pace per 100 m.
- Strength/Elliptical/Yoga/etc.: distance & speed are 0 -- use duration, calories,
  and (if present) relative_effort. Don't compute pace.
- Mind `is_trainer` (treadmill/indoor; GPS-derived metrics may be unreliable) and
  `is_commute` (often not training stimulus) when summarizing.

## 8. Honesty checklist

Before giving advice, confirm you have:

- [ ] the athlete's units (`measurement_preference`) -- and converted accordingly
- [ ] enough data for the claim (state the window and # of activities)
- [ ] flagged estimated values (`ftp_is_estimated`, `is_estimated`, estimated max HR)
- [ ] separated measured fact from interpretation
- [ ] avoided medical diagnosis and race-result guarantees

When data is missing (no HR, no power, few sessions), say what you *can't*
conclude. A precise "I can't tell from this" beats a confident guess.
