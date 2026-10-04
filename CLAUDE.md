# BRXProd base project

Reusable base for building on a Bricks site running Bricks Productivity
(BRXProd). Each project made from it connects to exactly **one** site.

- **New project:** create from this template, then run `/init-brxprod <site-url>`.
  Re-run it any time to re-check the site is ready.
- **This site's facts and tokens:** [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md), generated
  by `/design-system`. **Read it before writing any CSS or naming any token** —
  resolve every concept ("spacing M", "section padding", "brand colour") through
  its *Concept map*. If it is missing or stale, run `/design-system`.
- **What to write:** [PROJECT_BRIEF.md](PROJECT_BRIEF.md) — business, audience,
  voice, pages, content sources. Anything still `_TODO_` is unknown: ask, never
  invent content, contact details or claims.

## Order of authority

1. **Bricks' own skills and abilities** (`bricks:*` skills, `bricks/*`
   abilities) — the highest priority, always. They own *how* anything is
   built: pages, posts, templates, elements, components, global classes,
   variables, theme styles, the save pipeline and render verification. Load
   `bricks:bricks-start-here` and the task's Bricks skill before any write, and
   use a `bricks/*` ability whenever one exists — never execute-php, a
   `novamira/bricks-*` ability or a BRXProd ability in its place.
2. `brxprod/get-design-instructions` — the site owner's live house rules for
   *what* to write (CSS, naming, labels, semantics, code location), plus the
   `rails` / `corners` / `grids` sections when those systems are installed.
3. This file and `standards/` — how we work in every project. Where they
   explicitly say they override the site's instructions (label case; no
   HTML/CSS import), they win.
4. Other skills (`brxprod`, `brxprod-notes`, `brxprod-feedback`, `novamira`).

Where they disagree, the higher one wins. If a needed `bricks/*` ability is
unavailable, stop and tell the user which switch to turn on (Bricks → AI) —
do not fall back to another write path.

## Building content — element trees, never copy/paste or HTML import

**Never create content with Bricks' copy/paste or HTML/CSS conversion.** The
converter turns CSS into values in the element **Settings model** (Bricks'
style controls) instead of CSS — the opposite of our CSS standard. This
covers:

- the builder's paste (pasting HTML/CSS or copied elements into the canvas);
- `bricks/convert-html-css-to-bricks-data`,
  `bricks/preview-html-css-page-import`, `bricks/apply-html-css-page-import`,
  `bricks/commit-html-css-page-import`, and the `bricks:bricks-html-css-to-bricks`
  workflow.

This overrides the site's default instruction to build through the HTML/CSS
import, and the `brxprod` skill's pointer to it.

**Build element structures directly with Bricks' abilities:**

- write the tree with `bricks/add-element` (nested children), or
  `bricks/set-page-elements` / `bricks/create-template` with `elements` for an
  empty page or template; edit with `bricks/update-element`,
  `bricks/batch-update-elements` or the page-workspace abilities
  (`checkout` → `preview` → `apply`);
- check element settings against `bricks/get-element-schema` (load
  `bricks:bricks-element-schemas`);
- element settings carry **structure and content only** — `_cssGlobalClasses`,
  label, `tag`, text, links, media, attributes, and simple UI settings such as a
  button's `style`; never style-control values (spacing, colour, typography,
  layout);
- all styling goes in the **block's global class CSS** (`_cssCustom`) per
  [standards/css.md](standards/css.md), created/edited with Bricks'
  global-class abilities;
- verify with `bricks/render-elements` (and `brxprod/render-frontend-html` for
  content inside nestable elements).

The reference shape is [standards/examples/test-card.bricks.json](standards/examples/test-card.bricks.json)
— that is the structure to produce, written through abilities, never pasted.

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
- execute-php is for **read-only inspection** when no ability covers it. Never
  use it to write Bricks data.

## Frameworks

A BRXProd site runs one of two token frameworks, and the same concept has a
different name in each:

| Framework | Variables | Brand colours |
|---|---|---|
| **Bricks Wireframes** | `brxw-*` (e.g. `--brxw-space-m`) | BRXProd palette: `--brxp-primary`, shades `-{l,d,t}-N` |
| **Core Framework** | unprefixed (`--space-m`), or a user-chosen prefix | its own: `--primary`, transparency `-{5…90}`, shades `-{l,d}-N`; plus semantic `--text-body`, `--bg-surface`, `--border-primary` |

`brxprod/get-context` reports which one and the prefix in force;
`DESIGN_SYSTEM.md` records it. **The `brxp-*` CSS, classes and variables are
common to both.** Never hard-code a framework's token name in a rule meant for
either — and never invent a name the site doesn't have. Each framework lacks
some concepts the other has (Core Framework: no width, measure, line-height,
transition or ratio tokens); the concept map shows these as *not found*.

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

**Read [standards/css.md](standards/css.md) before writing any class, label or
CSS.** Reference build: [standards/examples/test-card.bricks.json](standards/examples/test-card.bricks.json).
In short:

- BEM classes; nested blocks are new blocks marked `_abpBemMeta.bemAction: "skip"`.
- Labels = the BEM segment in **Title Case** ("Test Card", "Content"); bracket
  comments `()` `[]` `{}` ignored. Overrides the site default's sentence case.
- All component CSS in the **block's** global class (literal `.block` selector);
  element classes stay empty.
- One `/* Settings */` block: `--_block__element-prop: var(--block__element-prop, token)`;
  rules use only `--_` vars. **Modifiers only set the public vars** — structural
  variants become variables too.
- Element rules flat; nest only states, pseudo-elements and `@container`.
- **Never `@media`**: `:has(> .block){container-type:inline-size}` + nested
  `@container (inline-size <= Npx)`, literal px, widest first.
- Use **BRXProd CSS Patterns** verbatim when one fits — e.g. a sticky header
  template gets the `sticky-header` pattern in its top element's CSS (needs the
  `header-height` snippet active).

## JavaScript & PHP standards

**Read [standards/js.md](standards/js.md) before writing any JavaScript.** In short:

- Every script in an **IIFE**; ES6+ (`const`/`let`, arrows); no jQuery, no globals.
- **Browser APIs first** (IntersectionObserver, ResizeObserver, delegation,
  AbortController…), and **events instead of timers** — including Bricks'
  frontend events (`bricks/ajax/query_result/displayed`, `bricks/popup/open`…).
- AJAX-loaded content: delegate, or idempotent init re-run on the Bricks event.
- JS sets state (attributes, custom properties); CSS decides looks.

Where code goes (follows the site's `code` section): a code manager via
`brxprod/create-snippet` — a **draft**; never activate it or claim to have —
never a Bricks Code element. Read `brxprod/get-site-js` first.

**PHP: [standards/php.md](standards/php.md)** — WordPress PHP Coding Standards;
prefixed global names; escape, sanitise, capability/nonce checks; no `eval`;
enqueue assets. Stored as a draft snippet — never activated by the agent.

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

- `/init-brxprod [url]` — connect, install skills, check site readiness,
  generate the design system, create the brief, offer Wireframes templates.
- `/setup-site <url>` — connection step on its own (also run by init).
- `/design-system` — (re)generate `DESIGN_SYSTEM.md`.
- **Bricks skills first** (`bricks:*`, from the `bricks@bricks-skills` plugin;
  start with `bricks:bricks-start-here`) for all Bricks work. Then the
  project's `brxprod`, `brxprod-notes`, `brxprod-feedback` (installed by init
  from `wpeasy/bricks-productivity-skills`, version in
  `.claude/skills/.brxprod-skills-version`) for plugin features, and
  `novamira` for general CLI use.
