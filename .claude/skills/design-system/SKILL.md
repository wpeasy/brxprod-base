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

If the framework is `unknown`, say so prominently — the concept map will be
mostly empty and the rules in AGENTS.md can't be resolved against it.

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

## Frameworks

Both are verified against real sites (Bricks Wireframes; Core Framework 2.0.2):

- **Bricks Wireframes** — `brxw-` prefix. Brand and status colours come from
  BRXProd's palette (`--brxp-primary` …), which exists only as palette entries,
  not Bricks variables; the renderer includes palette names for that reason.
- **Core Framework** — unprefixed by default (a user prefix is honoured via
  `get-context`). It syncs all its tokens into Bricks' global variables, in one
  "Core Framework" category, and ships its own brand/status colours with
  transparency (`--primary-{5…90}`) and shade (`--primary-{d,l}-{1…4}`) series
  plus semantic colours (`--text-body`, `--bg-surface`, `--border-primary`…). It
  also adds ~900 utility classes, summarised by family.

A concept that is *not found* is a real gap in that framework's preset (e.g.
Core Framework has no width, measure, line-height, transition or ratio tokens).

## Changing colours

When creating or changing the site's colours (palette entries or colour
variables):

- **Only change each colour's root value** — the unsuffixed one (`primary`,
  `secondary`, `tertiary`, `base` / `surface`, status colours…). Every variant
  — shades `-{l,d}-N`, transparencies `-{5…90}`, tints — is auto-generated from
  it. Never edit a variant by hand.
- **50% lightness applies only to the neutral colours** — `base` / `surface`
  (whatever this site calls its neutral ramp; `DESIGN_SYSTEM.md` shows it).
  Keep their hue and saturation, set HSL lightness to exactly 50%, so the
  generated light and dark shades run evenly both ways. For a lighter or darker
  neutral, use a `-l-N` / `-d-N` variant instead of moving the root.
- **Brand and status colours are not 50%** — `primary`, `secondary`,
  `tertiary`, `success`, `danger`… take whatever lightness the design calls
  for. Never normalise them to 50%.
- **Always regenerate BRXProd's a11y colour variables afterwards** —
  `novamira run brxprod/regenerate-a11y-colors --json` (no input). It
  recalculates every `--brxp-a11y-*-text` for every colour and its shades, from
  the BRXProd palette (Wireframes) or Core Framework's colours. Omit `method` so
  it uses the contrast method the user last chose (`wcag2` / `apca`); pass one
  only if the user asks. Report its `created` / `updated` lists. If the ability
  isn't on the site (older BRXProd), stop and ask the user to update the plugin
  or run it in BRXProd.
- Don't touch the theme style for a palette change: its element defaults
  (buttons, links, site background, text colours) already read the colour
  variables and a11y tokens, so the change flows through. Remap one only when
  the design needs a different mapping, and report which keys changed and why.
- Then re-run this skill so `DESIGN_SYSTEM.md` shows the new values.

### Mapping a brief's colours to the roles

When the brief or a client spec gives more colours than our roles —
**Primary**, **Secondary** and **Surface** (the neutral `base` / `surface`;
each root generates 10 light and 10 dark shades):

1. **List every spec colour** — name, hex, and what the spec says it's for.
   If a hex value or a purpose is missing, ask before going on.
2. **Map by use, not by the spec's order.** Never rename a role after a spec
   colour — components, utilities and templates depend on the role names.

   | Role | The spec colour that is… | Root value |
   |---|---|---|
   | Primary | the action colour (CTAs, main buttons); else the main brand colour | the spec's exact hex |
   | Secondary | for navigation, links and headings | the spec's exact hex |
   | Surface | the page background and text colours | the hue and saturation that best fit the spec's neutrals, at **50% lightness** (the 50% rule above) |

   - Surface: the spec's background maps to the nearest `-l-N` shade and its
     text colour to the nearest `-d-N` shade — report which, and how close.
     Never move the root off 50% to hit them exactly.
   - A "primary brand colour" that can't work as a button (a pale yellow that
     won't take white text) is not Primary — make it an extra colour and say why.
   - Only one or two brand colours: derive the missing role (complementary,
     darker or lighter) and flag it for approval.
3. **Leftover colours become extra Bricks palette colours** — root only, no
   shades. **Every name starts with `brxp-`** (otherwise BRXProd's generation,
   including `regenerate-a11y-colors`, skips it), then the spec's name in
   kebab-case: "Sunshine Yellow" → `brxp-sunshine-yellow`. Unnamed: a short
   descriptive name (`brxp-bright-green`) — never a role-like name
   (`brxp-accent`, `brxp-tertiary`). Don't add colours a role already covers
   (Surface's background and text).
4. **Check contrast (WCAG 2.2 AA)** — each role root and each extra colour
   against white and against dark text; 4.5:1 normal text, 3:1 large text / UI.
   Where a root fails, name the shade to use for text or button backgrounds;
   for extras, the text colour they must pair with. Never change the client's
   hex values — only recommend shades and pairings.
5. **Confirm before writing anything:** show a mapping table (role or extra →
   spec name → hex → use), the contrast results and pairings, and anything
   guessed. After approval: set the role roots, add the extras (check every
   name starts with `brxp-`), run `brxprod/regenerate-a11y-colors`, record the
   mapping in `PROJECT_BRIEF.md` › Colour scheme and as your own content on the
   Style Guide page (`brxprod/find-style-guide`; never its generated `sg{n}-*`
   parts), then re-run this skill.

Example — a spec with six colours:

| Framework | Spec name | Hex | Why |
|---|---|---|---|
| Primary | Coral Reef | #FF6B6B | Calls to action |
| Secondary | Bay Blue | #1FA2D6 | Links, headings, navigation |
| Surface | Sandy Cream → Driftwood Ink | hue/sat of #FFF8E7 / #2B2D42 at 50% | Background (nearest `-l-N`) and text (nearest `-d-N`) |
| Extra `brxp-sunshine-yellow` | Sunshine Yellow | #FFC93C | Highlights — pair with dark text |
| Extra `brxp-gumleaf-green` | Gumleaf Green | #6BCB77 | Eco badges, success messages |
| Extra `brxp-jacaranda-purple` | Jacaranda Purple | #9B5DE5 | Workshop section accents |

The spec calls Sunshine Yellow its "primary brand colour", but it can't take
white text, so it's an extra colour rather than Primary.

## Changing the concept map

`ROLES` at the top of `scripts/render.py` maps each concept to candidate token
names, tried in order. Add a candidate when a framework (or a customised
preset) names a concept differently; add a role when house rules need a new
concept. Re-run and check both the new row and that existing rows didn't move.
