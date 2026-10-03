---
name: design-system
description: Generate or refresh DESIGN_SYSTEM.md from the connected BRXProd/Bricks site — detects the token framework (Bricks Wireframes `brxw-*` or Core Framework, unprefixed or user-prefixed), maps design concepts to this site's actual token names, and lists framework tokens, the shared BRXProd `brxp-*` layer, palettes, global classes and theme styles. Use when the user runs `/design-system`, after `/setup-site`, or whenever the site's variables, classes or palettes change. Read DESIGN_SYSTEM.md (do not regenerate) when you only need a token name.
---

# /design-system

Writes `DESIGN_SYSTEM.md` at the project root from live site data. Generation is
a fixed script, not hand-written per run, so two runs against the same site give
the same file.

## Run it

```bash
sh .claude/skills/design-system/scripts/generate.sh
```

That script:

1. Calls `brxprod/get-context` for the framework and variable prefix (the
   authoritative source; it falls back to inferring from variable names if the
   ability is unavailable).
2. Runs `scripts/extract.php` through `novamira/execute-php`. The PHP is
   **read-only**; `--yes` is passed only because the CLI treats every
   execute-php call as destructive. Never add writes to that file.
3. Runs `scripts/render.py`, which rewrites only the region between
   `<!-- design-system:start … -->` and `<!-- design-system:end -->`. Anything
   outside the fence (the *Project notes* section) survives.

Prerequisites: `NOVAMIRA_HOME` / `NOVAMIRA_SITE` set by `/setup-site`, and
`python3` locally.

## After running

Report the framework detected, the variable and class counts the script prints,
and any concept-map row that says **not found** — that means this site has no
token for the concept, which matters before anyone writes CSS against it.

If the framework is not `bricks-wireframes`, say so prominently: only the
Wireframes branch has been verified against a real site.

## What the file contains

- **Site** — URL, profile, versions, framework + prefix, code manager, Style Guide.
- **Concept map** — the table house rules should be resolved against: "spacing
  M", "section padding", "container width" → this site's token. Values are shown
  as `min → max (fluid)` for clamp-based scales.
- **Framework tokens** grouped by the site's own variable categories, scales in
  size order. `*-fluid-*` primitives are omitted (always use the non-fluid name).
- **BRXProd tokens** (`brxp-*`) — identical layer on every framework.
- **Palettes** (shade ramps collapsed to patterns), **global classes** by
  category (Style Guide `sg{n}-*` classes omitted), **theme styles**.

## Extending to Core Framework

The `ROLES` table at the top of `scripts/render.py` maps each concept to
candidate token stems. Wireframes stems are verified; Core Framework stems
(`space-m`, `text-m`, `gutter`, `section-padding-block`…) are guesses. When this
is first run on a Core Framework site:

1. Check whether its tokens are in Bricks' global variables at all — Core
   Framework may emit its own stylesheet and only optionally sync variables to
   Bricks. `extract.php` records any `core_framework*` options to help locate
   them.
2. Correct the `ROLES` candidates against the real names, and the
   `detect_framework` fallback if needed.
3. Remove the "provisional" note this skill tells you to give.
