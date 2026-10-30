# BRXProd base project

Reusable base for building on a Bricks site running Bricks Productivity
(BRXProd). Each project made from it connects to exactly **one** site.

Shared by **Claude Code** (reads `CLAUDE.md`, which imports this file) and
**Codex** (reads this file). Skills live in `.claude/skills/`; `.agents/skills`
is a symlink to it, so both agents load the same ones. Invoke a skill as
`/name` in Claude Code or `$name` in Codex.

**Read this file (and `CLAUDE.md` in Claude Code) in full before doing any
work** — including straight after copying the base into a new folder. The
session must run *in* the project folder; one started elsewhere hasn't loaded
these rules, the skills or the site connection — stop and start a new session
there.

- **New project:** copy this base's files into a new folder, then run the `init-brxprod`
  skill with the site URL. Re-run it any time to re-check the site is ready.
- **This site's facts and tokens:** [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md), generated
  by the `design-system` skill. **Read it before writing any CSS or naming any token** —
  resolve every concept ("spacing M", "section padding", "brand colour") through
  its *Concept map*. If it is missing or stale, run the `design-system` skill.
- **What to write:** [PROJECT_BRIEF.md](PROJECT_BRIEF.md) — business, audience,
  voice, pages, content sources. Anything still `_TODO_` is unknown: ask, never
  invent content, contact details or claims.

## Order of authority

1. **Bricks' own skills and abilities** (`bricks:*` skills, `bricks/*`
   abilities) — the highest priority, always. They own *how* anything is
   built: pages, posts, templates, elements, components, global classes,
   variables, theme styles, the save pipeline and render verification. Load
   `bricks:bricks-start-here` and the task's Bricks skill before any write, and
   use a `bricks/*` ability whenever one exists — not a `novamira/bricks-*`
   ability or a BRXProd ability in its place, and not execute-php except where
   *Abilities or execute-php* below says PHP makes more sense.
2. `brxprod/get-design-instructions` — the site owner's live house rules for
   *what* to write (CSS, naming, labels, semantics, code location), plus the
   `rails` / `corners` / `grids` sections when those systems are installed.
3. This file (`AGENTS.md`) and `standards/` — how we work in every project. Where they
   explicitly say they override the site's instructions (label case; no
   HTML/CSS import; rails start at `layout`), they win.
4. Other skills (`brxprod`, `brxprod-notes`, `brxprod-feedback`, `novamira`).

Where they disagree, the higher one wins.

**Abilities or execute-php — use whichever makes more sense.** Abilities are
the default; `novamira/execute-php` is a first-class tool, not only a last
resort. For every task:

1. **An ability does it in a few calls** → use it (`bricks/*` first, then
   `brxprod/*`, then other `novamira` abilities).
2. **An ability exists but would take many round trips** — bulk or repetitive
   work such as deleting, renaming or re-categorising many classes, creating
   many pages or menu items, or any loop where each call needs a fresh
   ownership read (roughly more than ~10 calls, or minutes of waiting) → do it
   in **one execute-php call** with the same WordPress / Bricks PHP APIs the
   ability uses. Say up front that you are doing so and why.
3. **It exists but is switched off** (`get-context` / the status check lists
   it as unavailable) → tell the user which switch turns it on (Bricks → AI,
   BRXProd → Settings → AI Tools) and ask whether to wait for that or go ahead
   with execute-php.
4. **No ability covers it** → use execute-php, for reads *and* writes.

Reads are always fair game for execute-php when one PHP call answers what
would take several ability calls (usage counts, scans, bulk lookups).

**Keep on the abilities** whatever the call count: writing page / template
element trees (`bricks/set-page-elements`, `create-template`…) and creating
global classes — they run Bricks' save pipeline, revisions and validation.
**The exception is `_cssCustom` itself:** until Bricks fixes its CSS
normaliser, class and element CSS is written through execute-php (*Writing
CSS* below). See *Connection* for how to run execute-php safely.

### Writing CSS — through execute-php (temporary)

Bricks' abilities rewrite any `_cssCustom` they save (*Known issues*), so
**all class and element CSS is written with `novamira/execute-php`**, unwrapped
— no `@supports` wrapper. The rewrite lives only in the abilities
(`Bricks\Abilities\Element_Style_Normalizer`); CSS stored directly is kept and
rendered byte-for-byte (tested on Bricks 2.4.3, 2026-10-18).

1. **Structure through the abilities, CSS through PHP.** Create classes
   (`bricks/batch-create-global-classes`, no `_cssCustom`) and build element
   trees as usual, then set the CSS in a separate execute-php call.
2. **Global class CSS** lives in the `bricks_global_classes` option. Read it,
   change only the `_cssCustom` of the named classes, write it back in the
   same call, and bump `bricks_global_classes_timestamp`:

   ```php
   $css_by_name = array( 'site-footer' => "/* Settings */\n.site-footer{\n  …\n}" );
   $locked  = (array) get_option( 'bricks_global_classes_locked', array() );
   $classes = get_option( 'bricks_global_classes', array() );
   foreach ( $classes as &$class ) {
   	if ( isset( $css_by_name[ $class['name'] ] ) && ! in_array( $class['id'], $locked, true ) ) {
   		$class['settings'] = is_array( $class['settings'] ?? null ) ? $class['settings'] : array();
   		$class['settings']['_cssCustom'] = $css_by_name[ $class['name'] ];
   	}
   }
   unset( $class );
   update_option( 'bricks_global_classes', $classes );
   update_option( 'bricks_global_classes_timestamp', time() );
   ```

   Never write a locked class (BRXProd's `brxp-*` shells, framework classes).
   Don't do this while someone has the builder open on the site's classes — a
   builder save writes the whole list and would overwrite yours (ask first if
   unsure).
3. **Element CSS** lives in the element tree's post meta. Use the area's key
   (`\Bricks\Database::get_bricks_data_key( 'content' | 'header' | 'footer' )`),
   change only that element's `_cssCustom`, and save with `wp_slash()`.
   **Replace `%root%` with the real selector before saving** — `#brxe-{id}`,
   or `#{_cssId}` when the element has one. The builder and the abilities do
   that substitution on save; stored `%root%` is printed literally and ignored
   by the browser.
4. **Read it back** in the same call (the stored string must equal what you
   sent, with no new style-control keys), then check the front end renders it.
5. When Bricks ships a fixed normaliser, re-run the throwaway test in *Known
   issues* through the abilities; if it passes, go back to ability writes for
   CSS and delete this section.

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
- **never use the Block element — use Div.** Block ships default CSS (flex,
  width) and media queries that we'd then have to find and override; a Div
  starts clean and gets only the CSS we write. That includes the slides of a
  Slider (Nestable), which Bricks creates as Blocks;
- element settings carry **structure and content only** — `_cssGlobalClasses`,
  label, `tag`, text, links, media, attributes; never style-control values
  (spacing, colour, typography, layout);
- **buttons are the exception:** a Button element is styled only with its own
  controls — `size` (sm/md/lg/xl), `style` (primary/secondary/…), `circle`,
  `outline` — never CSS. Anything that looks like a button is a Button element,
  never a Text Link styled as one;
- all other styling goes in the **block's global class CSS** (`_cssCustom`) per
  [standards/css.md](standards/css.md) — the class created with Bricks'
  global-class abilities, its CSS written through execute-php (*Writing CSS*)
  — and **never targets a button or a link**; layout around a button
  (alignment, spacing) goes on its parent and siblings;
- **element defaults live in the active theme style**
  (`bricks/update-theme-style`): button colours in every state, sizes, borders
  and radius (`button.*`), links (`links.*`), site background and body/heading
  text colour (`general.siteBackground`, `typography.typographyBody.color`,
  `typography.typographyHeadings.color`). They are already mapped to the colour
  variables (e.g. `primaryBackground: var(--brxp-primary)`, hover
  `var(--brxp-primary-d-2)`), so a palette change flows through. Change a
  mapping only when the design needs it, and report exactly which keys changed
  and why. Shape shared by every button (radius, border width/style) goes on the
  default `button.border` and `button.border:hover`; the per-style keys
  (`primaryBorder`, `outlineBorder`…) stay colour-only;
- **read every CSS write back and compare** (*Writing CSS* › 4);
- verify with `bricks/render-elements` (and `brxprod/render-frontend-html` for
  content inside nestable elements).

**Never use or suggest Bricks Wireframes templates** — the remote template
library (`bricks/list-remote-templates` / `bricks/insert-remote-template`,
`source: "wireframes"` or `"design-sets"`), the builder's Templates panel, or
copying a Wireframes layout. This holds on a Bricks Wireframes site too: we use
the framework's *tokens*, never its templates. Build every section, header and
footer ourselves (or from the user's own design) as element trees, as above.

The reference shape is [standards/examples/test-card.bricks.json](standards/examples/test-card.bricks.json)
— that is the structure to produce, written through abilities, never pasted.

**After building a new page**, if BRXProd's Client Feedback is enabled and its
abilities are exposed (`brxprod/create-feedback` is listed; `get-context`
reports the group), log one internal review item on it with
`brxprod/create-feedback` — `scope: "page"`, `postId` the page,
`visibility: "internal"`, `label: "Review new page"`, `body: "AI Generated
page, please check and confirm the page quality and content"`.

- A **new page** is any page whose whole content the agent wrote: a page it
  created, **and** an existing page that was blank, empty or wiped (or that it
  cleared and rebuilt) before the agent filled it.
- Not for edits to a page that already had content — adding or changing
  sections there is an edit.
- Once per page build (the ability isn't idempotent): check `list-feedback`
  for that `postId` first and don't add a second open "Review new page" item.
- If the feedback abilities aren't available, skip it and say so.

### Example designs with a header or footer

When an example design (mockup, screenshot, Figma frame, HTML) includes a
header and/or footer, **build them as Bricks templates**, never as sections in
a page:

- load `bricks-headers-footers` (and `bricks-templates-conditions`) first;
- create each with `bricks/create-template` (`type: "header"` /
  `type: "footer"`), then build its element tree and classes exactly as for any
  other content (BEM, Title Case labels, class CSS, readback);
- the page itself gets only what sits between them;
- a sticky header gets BRXProd's `sticky-header` pattern in its top element's
  CSS ([standards/css.md](standards/css.md) › BRXProd CSS Patterns);
- display conditions decide where a template appears site-wide — **confirm
  with the user before setting them** (e.g. entire website), since that
  changes every page; until then leave them unset and say so.

### Navigation

**Read [standards/navigation.md](standards/navigation.md) before adding or
changing any navigation.** In short — this overrides `bricks:bricks-mega-menus`'
default of Nav (Nestable) for new headers:

- **Default: the Nav Menu element bound to a WordPress menu** (Appearance →
  Menus), so editors change links without Bricks. Link pages as page objects
  via `bricks/save-nav-menu`. Mega panels can stay on this path (a Bricks
  section template attached to the menu item).
- **Nav (Nestable) only when the nav is designed UI**: CTA/search/icons inside
  the bar, extra content in the mobile drawer, rich or data-driven dropdowns,
  bespoke dropdown behaviour, fixed structural links, or data-driven labels.
  Tell the user its links are edited in Bricks.
- **Always fix the mobile menu** (Bricks' defaults are bare): X close control
  top right, labelled toggles, edge padding, gap, size, brand background +
  a11y text — in the header block's class CSS on the open state — then verify
  at phone width.

### Motion — GSAP or Bricks Interactions

The project uses **one** motion system, recorded in `PROJECT_BRIEF.md` › Motion
(asked by `init-brxprod`). If it's not recorded, ask before adding any motion.
Never mix the two on the same element.

- **Bricks Interactions:** Bricks' interactions and entrance animations
  (`bricks:bricks-interactions`), tuned with BRXProd's tamed-animation classes
  (*BRXProd systems*). No GSAP.
- **GSAP:**
  - **Find the effect in the GSAP Prompt Library** — read
    https://gsap.brxprod.com/llms.txt, pick by description, fetch its
    `https://gsap.brxprod.com/effects/<id>.md` (prompt, sample code, demo
    HTML). Follow the prompt with `[SELECTOR]` = the element's BEM class;
    don't invent an effect the library already has.
  - **Editor or live site only** — `PROJECT_BRIEF.md` › Motion › *GSAP in
    the editor* (asked by `init-brxprod`; if missing, ask). **No** (the
    recommended default) → prefix **every** selector the effect code queries
    from the document with `body.bricks-is-frontend` — the class Bricks puts
    on `<body>` on the front end only, not in the editor canvas — e.g.
    `[SELECTOR]` `.card` → `body.bricks-is-frontend .card`, so the effect never
    runs in the editor. **Yes** → leave selectors unscoped. Selectors inside an
    already-matched element (`el.querySelector(...)`) need no prefix.
  - **GSAP and its plugins load only through BRXProd's `gsap-loader`
    snippet** (installed and active) — never the library's CDN `<script>`
    tags or `npm`, which it suggests. Load only the plugins the effect lists.
  - **One snippet per effect**, named after it (e.g. "GSAP T-01 Line
    Reveal"), so each can be found, activated or removed on its own. Only
    effects that form one compound or grouped effect — sharing a timeline or
    state, or meaningless apart — go in a single snippet, named for the group.
    Never pile unrelated effects into one "site animations" snippet.
  - The effect code is JavaScript under [standards/js.md](standards/js.md)
    (IIFE, no globals), stored with `brxprod/create-snippet` and activated
    (*Activating snippets*). Keep the library's `data-gsap-init` guard,
    `gsap.matchMedia()` reduced-motion handling, and its `data-gsap-cloak`
    rule scoped to `body.bricks-is-frontend` (CSS in a class, per css.md).
  - Verify on the front end that the effect runs and nothing flashes.
  - **ScrollTrigger auto-refresh** — whenever any ScrollTrigger effect is
    used. ScrollTrigger measures positions once at load and re-measures only
    on window resize; in the Bricks editor, late images/fonts, opening panels
    and element re-renders shift the layout without a resize, so effects fire
    in the wrong places (cards reveal late, then hide early). Unless the
    `gsap-loader` already includes an equivalent watcher (check its
    description in `brxprod/list-snippets`), create a JS snippet named
    **"GSAP ScrollTrigger auto-refresh"** from
    [standards/snippets/gsap-scrolltrigger-auto-refresh.js](standards/snippets/gsap-scrolltrigger-auto-refresh.js)
    with `brxprod/create-snippet` and activate it (*Activating snippets*).
    It must **run after the `gsap-loader`** (same location, later priority) —
    it exits silently if `gsap` / `ScrollTrigger` aren't defined yet; confirm
    `document.body` carries `data-st-refresh` on the front end. **Never fix
    misfiring effects by disabling them in the builder.** Verify: scroll the
    editor canvas after an edit — reveals still start at the effect's start
    line.
  - Never for carousels, sliders or marquees — see *Carousels* below.

### Carousels — Slider (Nestable) + Splide Extensions

**Any sliding content** — carousels, sliders, testimonial rotators, logo
tickers, marquees — is built with Bricks' **Slider (Nestable)**
(`slider-nested`; load `bricks:bricks-nestable-elements`), on every project
whatever its motion system. **Never GSAP** (not even the library's marquee
effects) and never hand-written carousel JS.

- **Install and activate BRXProd's "Splide Extensions for Slider (Nestable)"
  snippet** first: find its id with `brxprod/list-snippets` (read its
  description for the extensions and options it adds), `brxprod/install-snippet`
  if missing, then activate it (*Activating snippets*).
- **Configure through the slider's Splide custom options JSON** — the
  extension options go there, alongside Splide's own. Check the control's key
  and shape with `bricks/get-element-schema` for `slider-nested`; use only
  options the snippet's description lists.
- **Slides are Divs**, not the Block slides Bricks creates by default (the
  no-Block rule). Keep the slider's native child structure otherwise; a looped
  carousel puts the query on the one slide Div.
- Styling follows the CSS standard (BEM class on the slider and slides,
  container queries, a11y text tokens); the slider's own UI controls only for
  what Splide needs (per-page, gap, arrows, pagination).
- Verify on the front end: it initialises, autoplay/marquee motion respects
  reduced motion, and arrows/pagination are keyboard-operable and labelled.

## Connection — Novamira CLI (not MCP)

- The site is reached **only** through the `novamira` CLI. The `setup-site`
  skill sets `NOVAMIRA_HOME` and `NOVAMIRA_SITE` for each agent — Claude Code in
  `.claude/settings.local.json`, Codex in `.codex/config.toml` (Codex applies it
  only when the project is **trusted**). Neither file is committed. They point
  `NOVAMIRA_HOME` at this
  project's own profile store `.claude/novamira/` — containing only this site —
  and `NOVAMIRA_SITE` to its profile. The global Novamira store stays empty.
- **Never** override `NOVAMIRA_HOME` / `NOVAMIRA_SITE`, pass `--site`, or run
  `novamira auth login` for a different site from here. No permission rule
  stops these — this instruction is the only guard, so ask the user first.
- If `NOVAMIRA_HOME` / `NOVAMIRA_SITE` are not set, **stop** — do not run
  `novamira` against the global store. Run `setup-site` (or, in Codex, check the
  project is trusted so `.codex/config.toml` applies).
- Health check: `novamira doctor --json`.
- **Run every `novamira` command on its own** — one command per shell call,
  from the project root: no `cd … &&`, no pipes (`| python3`, `| jq`), no
  heredocs, `;` or `&&` chains. The `Bash(novamira:*)` allow rule only covers a
  command that is *only* `novamira`; anything chained to it makes Claude Code
  prompt for every call. Write input JSON with the file-writing tool (not the
  shell) to `.claude/tmp/` (gitignored), pass it as
  `--input @.claude/tmp/<name>.json`, and read the `--json` output directly
  instead of piping it into a parser.
- `novamira/execute-php` always needs `--yes` (the CLI treats it as destructive).
  Only add it after confirming what the code does. Pass code through a JSON file:
  `novamira --yes run novamira/execute-php --input @.claude/tmp/input.json` with
  `{"code": "..."}` — no `<?php`, `return` a value.
- Use execute-php when it makes more sense than the abilities (*Order of
  authority* › Abilities or execute-php) — bulk work, many-call loops, scans —
  or when no ability covers the task, for reads and writes alike. When writing
  with it: read the current state before changing it; use WordPress / Bricks PHP APIs, never raw
  SQL; change only what the task needs; read the result back; and tell the user
  you used execute-php and why. Everything else in this file — the CSS and HTML
  standards, readback, no HTML/CSS import — still applies to what it writes.

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

**Colours deferred to the brief:** if `PROJECT_BRIEF.md` › Colour scheme is
marked *Deferred* and still `_TODO_`, don't pick colours yourself — ask, or
build with the current palette. Once the user fills it in, apply it with
`init-brxprod` step 5 (5c–5e) before building more.

**Changing colours:** change only each colour's root (unsuffixed) value —
variants are auto-generated. **Only the neutral `base` / `surface` colour is
set to 50% HSL lightness** (use its `-l-N` / `-d-N` variants for lighter or
darker neutrals); brand colours (`primary`, `secondary`, and `tertiary` where a
site's palette has one) and status colours keep whatever lightness the design
needs. Then always run `brxprod/regenerate-a11y-colors`. Details: the `design-system` skill › *Changing colours*.

**A brief with more colours than our roles:** map Primary (action colour),
Secondary (nav, links, headings) and Surface (background + text, still at 50%)
by use; every leftover colour becomes an extra palette colour, root only, named
`brxp-<spec-name>` — never Tertiary, even where the site has one; check
contrast and get approval before writing. Steps: the `design-system` skill › *Mapping a brief's colours to the roles*.

## BRXProd systems (summary — the site's design instructions are authoritative)

All plugin classes are **locked, empty shells**. Their CSS lives in the active
theme style's stylesheet inside `BRXP_*_START/END` fences (rails, corners) or,
for animation/utility classes, in the class's own custom CSS. Never hand-edit
either — fixes belong in the BRXProd plugin.

- **Rails** — `brxp-rails` on the Section/Container makes a grid with named lines
  `full / layout / breakout / wide / content` (each `-start` / `-end`). Without
  a class, children land on `content` — the narrowest rail — so never rely on
  that default.
  - **Start wide, then step inwards.** `layout` is the site box width (the
    same as the Bricks container width) and is the **default for section
    content**: card grids, CTAs, feature rows, media, headers of a section —
    give them `brxp-rail-layout` explicitly. Step in to `breakout` / `wide` /
    `content` only for content that should be narrower than the site box
    (long-form text, a centred intro, a quote); `content` is for reading-width
    text. Never start narrow and widen. This overrides the site's `rails`
    instructions where they differ.
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
  land as Fluent Snippets drafts — activate them when the page needs them,
  per *JavaScript & PHP standards* › Activating snippets):
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

- BEM classes; nested blocks are new blocks marked `_abpBemMeta.bemAction: "skip"`
  (in the builder — abilities can't write it, see *Known issues*).
- Atomic components are **generic and structural**: one `card`, not
  `product-card` / `feature-card` / `person-card`. Visual variants are
  modifiers (`card--feature`); a different element tree is a version
  (`card-v2`). Purpose goes in the label comment (`Card (Product)`). Reuse an
  existing block before creating one.
- Labels = the BEM segment in **Title Case** ("Test Card", "Content"); bracket
  comments `()` `[]` `{}` ignored. Overrides the site default's sentence case.
- All component CSS in the **block's** global class (literal `.block` selector);
  element classes stay empty.
- **Write CSS through execute-php, unwrapped** — not through the abilities,
  which rewrite it (*Writing CSS*, *Known issues*). No `@supports` wrapper.
- One `/* Settings */` block: `--_block__element-prop: var(--block__element-prop, token)`;
  rules use only `--_` vars. **Modifiers only set the public vars** — structural
  variants become variables too.
- Element rules flat; nest only states, pseudo-elements and `@container`.
- **Text colour is always the a11y token for its background** —
  `--brxp-a11y-{colour}[-{l|d}-N]-text` (body, headings, muted text, labels,
  prices, button and link text). Brand colours are for backgrounds, borders and
  decoration only; hierarchy comes from size/weight, never a "muted" shade.
- **No CSS for buttons or links** — they take their look from the Button
  controls and the theme style's defaults (above).
- **Typography comes from the theme style's Typography settings** wherever
  possible; a needed variation (size, weight, style) is set in the block's
  class CSS. **Never `font-family` in CSS** — families come only from the theme
  style, so they stay consistent.
- **Google Fonts are installed as Bricks Custom Fonts** (files on the site, a
  face per weight/style used — never Google's CDN or Bricks' Google Fonts
  list); family and weights are then selected in Bricks' UI settings, which
  output the CSS.
- **Never `@media`**: `:has(> .block){container-type:inline-size}` + nested
  `@container (inline-size <= Npx)`, literal px, widest first.
- Use **BRXProd CSS Patterns** verbatim when one fits — e.g. a sticky header
  template gets the `sticky-header` pattern in its top element's CSS (needs the
  `header-height` snippet active).

## HTML semantics & accessibility

**Read [standards/html.md](standards/html.md) before building any element
tree.** Tags are chosen for what the content *is* (Bricks `tag`, or
`tag: "custom"` + `customTag` for `dl`/`dt`/`dd`/`time`/`blockquote`…;
attributes via `_attributes`). In short:

- collections → `ul`/`ol` > `li`; term/value pairs → `dl` > `dt`/`dd`;
  self-contained items → `article`; quotes → `figure` > `blockquote` +
  `figcaption`; dates → `time datetime`; contact → `address`; data → `table`.
- one `h1`, no skipped levels; Basic Text is a `div` by default — set `p`.
- Bricks provides `<main id="brx-content">` — never add another `main`, nor
  duplicate a landmark Bricks' header/footer wrappers output; every `nav` and
  `section` is named (`aria-label` / `aria-labelledby`).
- links navigate, buttons act; native elements before ARIA roles; decorative
  media `aria-hidden`; state via `aria-*`; WCAG 2.2 AA (contrast, keyboard,
  focus, reduced motion).

## JavaScript & PHP standards

**Read [standards/js.md](standards/js.md) before writing any JavaScript.** In short:

- Every script in an **IIFE**; ES6+ (`const`/`let`, arrows); no jQuery, no globals.
- **Browser APIs first** (IntersectionObserver, ResizeObserver, delegation,
  AbortController…), and **events instead of timers** — including Bricks'
  frontend events (`bricks/ajax/query_result/displayed`, `bricks/popup/open`…).
- AJAX-loaded content: delegate, or idempotent init re-run on the Bricks event.
- JS sets state (attributes, custom properties); CSS decides looks.

Where code goes (follows the site's `code` section): a code manager via
`brxprod/create-snippet` (it lands as a draft) — never a Bricks Code element.
Read `brxprod/get-site-js` first.

**Activating snippets — do it as needed.** When the work depends on a snippet
(one you wrote, or a bundled one from `brxprod/install-snippet`), activate it;
don't leave it as a draft for the user. This overrides the `brxprod` skill's
"never activate" rule. No ability activates a snippet, so use execute-php
against the code manager's own API (*Abilities or execute-php* › 4), then:

- **PHP:** lint it first (`php -l` locally, or `token_get_all` in execute-php);
  after activating, load the front end and `wp-admin` (`novamira doctor --json`
  and a page render). On any fatal or white screen, **deactivate it at once**
  and report.
- **JS / CSS:** check the page that uses it renders without console errors.
- Read the snippet's status back, and tell the user which snippets you
  activated and what each does.

**PHP: [standards/php.md](standards/php.md)** — WordPress PHP Coding Standards;
prefixed global names; escape, sanitise, capability/nonce checks; no `eval`;
enqueue assets. Stored as a snippet and activated per the rule above.

## Known issues

- **Bricks 2.4.2 / 2.4.3 rewrite CSS written through the abilities.** Every
  `_cssCustom` saved by an ability (element or global class) passes a
  normaliser that ignores the "sync Custom CSS ↔ style controls" setting —
  moving root declarations into style controls — and cannot parse CSS nesting,
  corrupting `&:hover`, nested `@container` and nested selectors (unbalanced
  braces, wrong values) while the save still reports `ok: true`.
  On 2026-10-16 Bricks 2.4.3 still rewrote unwrapped CSS (root
  `display`/`gap`/`padding`/`color` moved into style controls; `&:hover` →
  `&: hover`, `&::before` → `&: :before`; `@container` braces dropped).
  **Workaround: write `_cssCustom` through execute-php** (*Order of authority*
  › Writing CSS). The rewrite is only in the abilities' write path; CSS stored
  directly renders unchanged. (The previous workaround — wrapping all CSS in
  `@supports (display: grid) { … }` so the normaliser skipped it — is retired;
  unwrap any CSS still carrying it when you next touch that class.)
  **Re-test when Bricks updates:** through the abilities, save a throwaway
  class with unwrapped CSS containing root declarations, `&:hover`,
  `&::before` and a nested `@container`; read it back; delete it. If it comes
  back byte-identical with no style-control keys, go back to ability writes
  for CSS, delete *Writing CSS*, and remove this entry.
- **Bricks 2.4.2's element validator rejects `settings._abpBemMeta`**
  ("Expected a registered setting for the 'div' element") on ability writes
  (`create-post`, `set-page-elements`…), so the nested-block
  `bemAction: "skip"` marker can't be written that way. Leave it out, say so,
  and set it in the builder if BRXProd's BEM tool will be run on the page.

### BRXProd plugin (not site faults)

- **No ScrollTrigger auto-refresh in the `gsap-loader` yet** — hence the
  separate "GSAP ScrollTrigger auto-refresh" snippet (*Motion* › GSAP). Once
  the loader ships the same watcher, stop creating it, deactivate and remove
  it on existing sites, and delete that bullet and this entry.


- `bricks/audit-design-system` reports locally-scoped custom properties (e.g.
  `--_layout`, `--_m-tl`, `--brxp-distance`, `--brxp-duration`) as orphans. They
  are set inside the theme style / class CSS — ignore.
- The generated Style Guide references `--brxp-{info,success,warning,danger}-d-2`,
  which don't exist (contextual colours shouldn't use d-shades). Being fixed in
  BRXProd — don't create the variables or edit the page.
- The theme stylesheet carries the reduced-motion block twice (one copy outside
  any fence). Harmless.

## Skills

- `init-brxprod [url]` — connect, install skills, check site readiness,
  generate the design system, create the brief, choose the motion system.
- `setup-site <url>` — connection step on its own (also run by init).
- `design-system` — (re)generate `DESIGN_SYSTEM.md`.
- **Bricks skills first** (`bricks-start-here` and the task's Bricks skill) for
  all Bricks work — from the `~/.bricks/skills/bricks-skills` release checkout,
  as the `bricks@bricks-skills` plugin in Claude Code and symlinked into
  `~/.agents/skills` for Codex; `init-brxprod` installs and updates both. Then
  the project's `brxprod`,
  `brxprod-notes`, `brxprod-feedback` (installed by init from
  `wpeasy/bricks-productivity-skills`, version in
  `.claude/skills/.brxprod-skills-version`) for plugin features, and
  `novamira` for general CLI use.
