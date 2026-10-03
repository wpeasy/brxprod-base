# BRXProd base project

Reusable base for building on a Bricks site running Bricks Productivity
(BRXProd). Each project made from it connects to exactly **one** site.

- **New project:** create from this template, then run `/setup-site <site-url>`.
- **This site's facts and tokens:** [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md), generated
  by `/design-system`. **Read it before writing any CSS or naming any token** —
  resolve every concept ("spacing M", "section padding", "brand colour") through
  its *Concept map*. If it is missing or stale, run `/design-system`.

## Order of authority

1. `brxprod/get-design-instructions` — the site owner's live house rules, plus
   the `rails` / `corners` / `grids` sections when those systems are installed.
2. This file — how we work in every project.
3. Skills (`bricks:*`, `brxprod`, `novamira`) — general reference.

Where they disagree, the higher one wins.

## Connection — Novamira CLI (not MCP)

- The site is reached **only** through the `novamira` CLI. `.claude/settings.local.json`
  (created by `/setup-site`, never committed) sets `NOVAMIRA_HOME` to this
  project's own profile store `.claude/novamira/` — containing only this site —
  and `NOVAMIRA_SITE` to its profile. The global Novamira store stays empty.
- **Never** override `NOVAMIRA_HOME` / `NOVAMIRA_SITE`, pass `--site`, or run
  `novamira auth login` for a different site from here. The `ask` rules in
  `.claude/settings.json` make each of those prompt.
- Health check: `novamira doctor --json`.
- `novamira/execute-php` always needs `--yes` (the CLI treats it as destructive).
  Only add it after confirming what the code does. Pass code through a JSON file:
  `novamira --yes run novamira/execute-php --input @input.json` with
  `{"code": "..."}` — no `<?php`, `return` a value.
- Prefer real abilities (`bricks/*`, `brxprod/*`) over execute-php; use PHP for
  read-only inspection when no ability covers it.

## Frameworks

A BRXProd site runs one of two token frameworks, and the same concept has a
different name in each:

| Framework | Variables |
|---|---|
| **Bricks Wireframes** | `brxw-*` (e.g. `--brxw-space-m`) |
| **Core Framework** | unprefixed (`--space-m`), or under a user-chosen prefix |

`brxprod/get-context` reports which one and the prefix in force;
`DESIGN_SYSTEM.md` records it. **The `brxp-*` CSS, classes and variables are
common to both.** Never hard-code a framework's token name in a rule meant for
either — and never invent a name the site doesn't have.

## BRXProd systems (summary — the site's design instructions are authoritative)

All plugin classes are **locked, empty shells**. Their CSS lives in the active
theme style's stylesheet inside `BRXP_*_START/END` fences (rails, corners) or,
for animation/utility classes, in the class's own custom CSS. Never hand-edit
either — fixes belong in the BRXProd plugin.

- **Rails** — `brxp-rails` on the Section/Container makes a grid with named lines
  `full / layout / breakout / wide / content` (each `-start` / `-end`). Children
  default to `content`.
  - **Symmetric span** → the utility class only:
    `brxp-rail-{content|wide|breakout|layout|full}`. No width, max-width or
    negative margin. `brxp-rail-full` strips inline padding; compose
    `brxp-gutter-{x|left|right}` back on for edge protection.
  - **Asymmetric span** → ID-level CSS on the element, never a new class:
    `%root%{ grid-column-start: content-start; grid-column-end: full-end; }`.
  - Widths: `--brxp-{content,wide,breakout,layout}-width`, `--brxp-page-gutter`;
    the rails converge fluidly as the viewport narrows.
  - Background media: `brxp-has-bg-media` + child `brxp-has-bg-media__media`
    (child hidden from assistive tech).
- **Corners** — `brxp-inverted-radius-{corner}-*`: a mask scoop into the element;
  all four at once is fine; `-horizontal`/`-vertical` are aliases (use one); tune
  `--inverted-radius`; no colour variable. `brxp-outset-radius-{corner}-{horizontal|vertical}`:
  a pseudo-element flare into the parent (`-horizontal` = `::before`,
  `-vertical` = `::after`), so **max two per element**, one of each; tune
  `--outset-radius` and `--outset-color` (match the element's background) in the
  element's own `%root%`.
- **Tamed animations** — the theme stylesheet rewrites Bricks' animation
  keyframes to read `--brxp-distance` / `--brxp-rotate`, forces
  `.brx-animated { animation-duration: var(--brxp-duration) }`, adds
  `@keyframes brxpCompound` (driven by `--brxp-compound-{x,y,scale,rotate}`) and
  reduced-motion handling. Size tiers are global vars
  `--brxp-{distance,rotate,duration}--{s,m,l,xl}`, chosen per element with
  `brxp-animation-{distance|rotate|duration}--*` and
  `brxp-animation-compound-*` classes. `brxp-animation-stagger-{duration|delay}`
  on a parent staggers its children (step via `brxp-animation-stagger-step--*ms`),
  indexed by `--brx-entry-index` else `sibling-index() - 1`.
- **Animation snippets** (bundled; install with `brxprod/install-snippet`, they
  land as Fluent Snippets **drafts** the user activates):
  `fadein-fix` (JS — hides fadeIn*/Compound enter-view elements until Bricks'
  trigger point, fades them out on exit, sets `--brx-entry-index` per entering
  batch) and `register-compound-animation` (PHP — adds "Compound" to the
  builder's Animation Type list). Without them Compound can't be picked and
  fade-ins can flash.
- **Grids** — hand-written layout grids match the Grid Builder format (see the
  site's `grids` instructions): `/* abp-grid:start */` fence on the grid's ID
  CSS, placement by `> :nth-child(N)`, containment via `:has(> #id)`.

## CSS standards

_To be specified._ Until then follow the site's `get-design-instructions` `css`
section (CSS not Bricks controls, `@container` not `@media`, one `/* Settings */`
`%root%` block with `--_x: var(--x, token)`, nested rules, BEM).

## JavaScript & PHP standards

_To be specified._ Until then follow the site's `code` section: code goes in a
code manager via `brxprod/create-snippet` (draft — never activate it or claim to
have), never a Bricks Code element; read `brxprod/get-site-js` first.

## Known issues (BRXProd plugin, not site faults)

- `bricks/audit-design-system` reports locally-scoped custom properties (e.g.
  `--_layout`, `--_m-tl`, `--brxp-distance`, `--brxp-duration`) as orphans. They
  are set inside the theme style / class CSS — ignore.
- The generated Style Guide references `--brxp-{info,success,warning,danger}-d-2`,
  which don't exist (contextual colours shouldn't use d-shades). Being fixed in
  BRXProd — don't create the variables or edit the page.
- The theme stylesheet carries the reduced-motion block twice (one copy outside
  any fence). Harmless.

## Skills

- `/setup-site <url>` — connect this project to its site (isolated profile).
- `/design-system` — (re)generate `DESIGN_SYSTEM.md`.
- Official Bricks skills (`bricks:*`, start with `bricks:bricks-start-here`) for
  all Bricks work; `brxprod`, `brxprod-notes`, `brxprod-feedback` for plugin
  features; `novamira` for general CLI use.
