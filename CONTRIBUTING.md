# Contributing

Thanks for helping improve the Strava skill for Claude. This guide explains how
the repo is organized, how to validate and test changes, and what we look for in
a pull request.

## What this project is

A single [Claude skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
(`strava-coach`) that helps Claude fetch and interpret Strava MCP data, packaged as a
Claude Code plugin marketplace. Contributions usually fall into one of:

- **Accuracy fixes** — your Strava MCP build returns a field, unit, or quirk that
  the docs get wrong or don't cover.
- **Interpretation improvements** — better, well-sourced coaching guidance.
- **Skill-quality fixes** — clearer instructions, tighter structure, broken links.

## Project layout

```
.claude-plugin/   marketplace.json + plugin.json (distribution manifests)
skills/strava-coach/  SKILL.md (entry point) + references/ (loaded on demand)
scripts/          validate.py (structure/link/manifest checks)
evaluations.md    behavior test scenarios (run by hand against a live MCP)
```

`SKILL.md` is the always-loaded entry point; everything in `references/` is pulled
in only when a task needs it. Keep that split intact.

## Authoring guidelines

These follow Anthropic's
[skill-authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices):

- **Keep `SKILL.md` concise** (well under 500 lines). Push depth into `references/`.
- **References one level deep** — link reference files directly from `SKILL.md`,
  not from each other.
- **Description in third person**, stating both *what* the skill does and *when*
  to use it. Max 1024 chars.
- **Consistent terminology** and concrete examples over abstract prose.
- **Both units** — always support km **and** miles, and show running speed as pace.
- **No personal data.** This is a public, generic skill. Don't commit anyone's
  athlete data, tokens, or activity IDs; use illustrative example values.
- **No time-sensitive claims** that will silently rot.
- **Cite sources** for training-science guidance in the PR description.

## Validate your change

Structural checks are stdlib-only and run in CI on every push/PR. Run them
locally first:

```bash
python scripts/validate.py
```

This checks frontmatter (name/description rules), that reference links resolve,
and that `plugin.json` / `marketplace.json` are valid. It must pass (exit 0).

## Test behavior with evaluations

`scripts/validate.py` only checks structure — it does **not** test whether the
skill actually behaves correctly. For that, use [`evaluations.md`](evaluations.md):
a set of representative queries plus the behavior a correct run must show.

There's no automated runner (the scenarios need a live Strava account), so test
by hand:

1. Load the skill and connect a Strava MCP in a Claude session.
2. Run each query from `evaluations.md`.
3. Check the output against that scenario's expected-behavior checklist.

If your change affects behavior, add or update a scenario so the new behavior is
covered.

## Pull request checklist

- [ ] `python scripts/validate.py` passes.
- [ ] Relevant `evaluations.md` scenarios still hold (and new ones added if needed).
- [ ] `SKILL.md` stays concise; new depth lives in `references/`.
- [ ] No personal data, secrets, or time-sensitive claims.
- [ ] Training-science changes cite a source in the PR description.
- [ ] If you changed what the plugin ships, bump `version` in **both**
      `.claude-plugin/plugin.json` and the matching `marketplace.json` entry.

## Releasing (maintainers)

Bump `version` in `.claude-plugin/plugin.json` **and** the `marketplace.json`
plugin entry so installed users receive the update, then tag a GitHub Release with
a short changelog. (Omitting both `version` fields instead makes every commit a
new version automatically.)

## Reporting issues

Open a GitHub issue with: what you asked Claude, what it did, what you expected,
and — if it's a data/units discrepancy — the relevant tool name and a redacted
sample of the response (strip personal data and IDs).

## License

By contributing, you agree your contributions are licensed under the repository's
[MIT License](LICENSE).
