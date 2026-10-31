---
name: init-brxprod
description: One-command setup (and re-check) of a BRXProd project — connects the site if needed, installs the BRXProd agent skills, checks the site is ready for agent work (Bricks abilities, BRXProd ability groups, framework, class sets, theme style, code manager, snippets), creates PROJECT_BRIEF.md, asks whether to define the theme and colours now or later in the brief — if now, asks light or dark and the primary/secondary colours then sets the palette, Surfaces and page colours — generates DESIGN_SYSTEM.md, asks GSAP or Bricks Interactions for motion. Never offers or inserts Bricks Wireframes templates. Use when the user runs `/init-brxprod`, starts a new project from the base, or asks whether the project/site is ready to build on. Safe to re-run; done steps are skipped.
---

# /init-brxprod [site-url]

Gets a project to the point where the agent can build pages, posts, templates
and content with **Bricks' own skills and abilities first**, BRXProd's rules on
top, and the installed framework's tokens. Every step is idempotent: re-running
refreshes and re-checks rather than redoing.

Run the steps in order. Report progress in one line per step.

## 0. Read the project instructions — before anything else

- **Check the working directory is the project root** (`AGENTS.md` and
  `CLAUDE.md` are in it). If the project is a subfolder — e.g. this session
  copied the base into `my-site/` — **stop**: tell the user to start a new
  session in that folder. Its skills, permissions and site connection
  (`.claude/settings*.json`, `.codex/config.toml`) only apply there.
- **Read `CLAUDE.md` and `AGENTS.md` in full** if they are not already in your
  context, and follow them for everything after. Do no other work first.

## 1. Connect

If `NOVAMIRA_HOME` / `NOVAMIRA_SITE` are not set, or `novamira doctor --json`
fails on the profile, run the **setup-site** skill (with the URL argument if
given; otherwise ask for it). Otherwise skip.

## 2. Skills

Install both skill sets automatically. Each script **checks first** and only
downloads or changes what is missing or out of date — run both every time.

**BRXProd skills** (`wpeasy/bricks-productivity-skills`, into this project):

```bash
sh .claude/skills/init-brxprod/scripts/install-skills.sh
```

Compares the repo's latest commit with `.claude/skills/.brxprod-skills-version`
and the installed `brxprod`, `brxprod-notes`, `brxprod-feedback` folders.
Prints `BRXPROD_SKILLS_CURRENT <commit>` (nothing downloaded) or
`BRXPROD_SKILLS_INSTALLED old -> new`. The skills are committed with the project.

**Bricks skills** (`codeerhq/bricks-skills`, machine-wide, per its README's
release-managed install):

```bash
sh .claude/skills/init-brxprod/scripts/install-bricks-skills.sh
```

- Checkout `~/.bricks/skills/bricks-skills`: cloned if missing, then Bricks'
  own `bricks-skills-upgrade` compares `VERSION` with the latest GitHub release
  (`BRICKS_SKILLS_ALREADY_CURRENT …` when nothing to do). Needs Node.js.
- Claude Code: adds that checkout as the `bricks-skills` marketplace and
  installs `bricks@bricks-skills`, each only if not already there
  (`BRICKS_MARKETPLACE_PRESENT` / `BRICKS_PLUGIN_PRESENT`).
- Codex: symlinks each `bricks-*` skill into `~/.agents/skills`
  (`BRICKS_CODEX_LINKS present=N added=M`).

A `…_FAILED` line names the manual command to give the user (e.g.
`/plugin install bricks@bricks-skills`); continue with the other steps.

New or updated skills load in a **new chat**; say so if anything was installed
or updated.

## 3. Site status

```bash
python3 .claude/skills/init-brxprod/scripts/status.py
```

Read-only. Prints PASS / WARN / FAIL lines, each FAIL/WARN with the fix, and a
`facts` line (ability counts, framework, house-rule set, Bricks post types).

- **FAIL** lines block agent building. Relay each fix verbatim — they are
  switches only the site owner can turn on (Bricks → AI, BRXProd → Settings →
  AI Tools). Don't silently replace a disabled ability with execute-php — tell
  the user the switch and ask (AGENTS.md › Abilities or execute-php).
- **No `bricks/*` abilities** is the critical one: without Bricks' agent layer
  there is no supported way to create or edit pages, templates, classes or
  variables. Continue the remaining read-only steps, then report it as blocking.
- **WARN** lines are worth fixing but don't block. Offer what the agent can do:
  - missing bundled snippets (`header-height` — needed by the sticky-header
    CSS pattern; `fadein-fix`, `register-compound-animation` — animations) →
    `novamira run brxprod/install-snippet --input '{"id":"<id>"}'` (they land as
    Fluent Snippets drafts);
  - snippets in draft → activate the ones the build needs (AGENTS.md ›
    Activating snippets) and report which;
  - no Style Guide page → BRXProd's *Update Style Guide Page* (owner action).
- If `facts.bricksPostTypes` lacks a type the brief needs (e.g. `post`), say so:
  Bricks → Settings → Post types.

## 4. Project brief

If `PROJECT_BRIEF.md` is missing, copy
`.claude/skills/init-brxprod/templates/PROJECT_BRIEF.md` to the project root.
Don't fill it in from guesses — ask the user to complete it (or to answer its
questions in chat, then write their answers in). It must exist before step 5,
which writes the theme and colours into it.

## 5. Theme and colours — light or dark, then Primary / Secondary, then Surfaces

Skip when `PROJECT_BRIEF.md` › Colour scheme already records the **Theme** and
the role colours **and** `brxprod/get-surfaces` shows nothing under `missing`
or `failing` and every `page` entry has `followsSurface1: true`.

### 5·0. Ask first: now, or in the brief?

If the brief's Colour scheme already has the Theme and role colours filled in
(but they aren't applied yet), skip this question and apply them (5c–5e).
Otherwise **ask the user one question** before any design question:

- **Define them now** — continue with 5a–5e.
- **Later, in the project brief** — ask nothing about theme or colours. Mark
  `PROJECT_BRIEF.md` › Colour scheme `Deferred — to be filled in the brief`,
  skip 5a–5e, and carry on with step 6. Tell the user that once they fill in
  the Theme and colours, re-running `/init-brxprod` (or asking the agent to
  apply the brief's colours) runs 5c–5e. Until then the site keeps its
  current palette and Surfaces.

When defining now, run the parts that aren't done, **in this order** — the
Surfaces and page colours are derived from the palette, so they come last.

### 5a. Ask: light or dark?

**Ask the user** (one question, two options) whether the site is
**light-themed** (light page, dark text) or **dark-themed** (dark page, light
text). Write it into `PROJECT_BRIEF.md` › Colour scheme › Theme.

### 5b. Ask for the Primary and Secondary colours

Ask for **Primary** (the action colour: buttons, CTAs) and **Secondary**
(navigation, links, headings) as hex values, plus the neutral hue for
**Surface** if they have one — or "agent to propose". More colours than roles,
or only one brand colour: follow the `design-system` skill › *Mapping a
brief's colours to the roles*. **Show the mapping and contrast check and get
approval before writing** (that section's step 5).

### 5c. Write the palette

Per the `design-system` skill › *Changing colours*:

1. Set each role's **root** palette colour (the BRX Prod palette entries whose
   `raw` is `var(--brxp-primary)`, `var(--brxp-secondary)`,
   `var(--brxp-surface)`) with `bricks/update-color`, using the colour's
   `itemOwnership` from a fresh `bricks/list-color-palettes` read. Surface
   keeps the chosen hue and saturation at **50% lightness**.
2. **Regenerate the shades** — `update-color` changes the root only; the
   `-l-N` / `-d-N` / `-t-N` children keep their old values until regenerated.
   For each root and each shade type it already has (`light`, `dark`,
   `transparent`, same step count): `bricks/generate-color-shades` with
   `paletteId`, `colorId`, `baseVariable` (the root's `raw`), `shadeType`,
   `steps` → take `saveOwnership` → call again with `save: true` and that
   ownership. Read back one shade per type to confirm it moved.
3. `brxprod/regenerate-a11y-colors` (no input) and report `created` / `updated`.
4. Record the final roles and values in `PROJECT_BRIEF.md` › Colour scheme.

### 5d. Set the Surfaces for the theme

Needs BRXProd 1.3.6+ and its **Edit Surfaces** ability group. If
`brxprod/set-surfaces` is unavailable (`get-context` lists it under
`abilityGroups.unavailable`), tell the user to switch on **Edit Surfaces**
(BRXProd → Settings → AI Tools → WordPress Abilities) and stop this part — do
not write the variables another way.

Read `brxprod/get-surfaces` first. There are **six** Surfaces; set 1–4 with
`set-surfaces` (5 and 6 — see below),
pointing at the palette's own tokens and giving every `-color` the a11y text
variable of its `-bg` (`var(--brxp-a11y-<token>-text)`):

| Surface | Role | Light theme `-bg` | Dark theme `-bg` |
|---|---|---|---|
| 1 | page / section | `--brxp-surface-l-9` | `--brxp-surface-d-9` |
| 2 | raised card / panel | `--brxp-surface-l-10` | `--brxp-surface-d-8` |
| 3 | inset well | `--brxp-surface-l-8` | `--brxp-surface-d-10` |
| 4 | accent block | `--brxp-primary` | `--brxp-primary` |

- **`-color`**: `var(--brxp-a11y-<that bg token>-text)`, e.g.
  `var(--brxp-a11y-surface-d-9-text)`.
- **`-link`**: light theme — a darker Primary/Secondary shade (start at
  `--brxp-primary-d-2`); dark theme — a lighter one (start at
  `--brxp-secondary-l-2`); Surface 4 — its own `-color`. Fix whatever the
  response lists under `failing` (move the link one shade further from the
  background) until `failing` is empty — never lower the 4.5:1 minimum.
- **Surfaces 5 and 6** (primary block, secondary block) follow the palette by
  default (`--brxp-primary` / `--brxp-secondary` with their a11y text), so init
  leaves them alone. Read them in `get-surfaces` and fix only a pair listed
  under `failing`; mention them in the report so the user knows all six exist.
- `classesInstalled: false` means the `brxp-surface{1-6}` classes aren't on
  the site yet: `set-surfaces` creates the variables, but the classes come from
  creating or updating the Style Guide page in the builder (owner action) —
  say so.

### 5e. Link the page body to Surface 1

The page is not a Surface: its background and text come from the active theme
style. For every style `get-surfaces` lists under `page` with
`followsSurface1: false`: `bricks/get-theme-styles` (`style` = its id) for the
ownership, then `bricks/update-theme-style` with

```json
{"general":{"siteBackground":{"color":{"raw":"var(--brxp-surface1-bg)"}}},
 "typography":{"typographyBody":{"color":{"raw":"var(--brxp-surface1-color)"}},
               "typographyHeadings":{"color":{"raw":"var(--brxp-surface1-color)"}}},
 "links":{"typography":{"color":{"raw":"var(--brxp-surface1-link)"}}}}
```

`siteBackground` takes the background-control shape (`{"color":{"raw":…}}`),
not a bare `{"raw":…}`. It deep-merges, so fonts and background images stay.
Report which keys changed. Then re-read `get-surfaces`: done only when
`failing` is empty and every `page` entry shows `followsSurface1: true` — from
then on, a re-theme of the Surfaces moves the page too.

## 6. Design system

Run the **design-system** skill — after step 5, so `DESIGN_SYSTEM.md` records
the new palette. Then confirm it shows the framework, the house-rule set
(Code / Visual / Custom) and a concept map. Note any *not found* concepts in
the report.

## 6b. Visual language — shapes, corners, backgrounds

Skip if `PROJECT_BRIEF.md` › Visual language is filled in **and** applied.

- If a brief, mood board or screenshots exist, **look at them** and fill the
  brief's *Visual language* section from what they show (AGENTS.md › Design
  fidelity). Otherwise ask the user one question: pill, rounded or square
  buttons, and large or small card corners.
- Apply the button shape now through the theme style: `bricks/get-theme-styles`
  (for the ownership), then `bricks/update-theme-style` with `radius` on
  `button.border` and `button.border:hover` (all four corners; a pill is the
  framework's `radius-full` token). Report the keys changed.
- Corners, backgrounds and signature details are applied later, while
  building, from the same checklist.

## 7. Motion — GSAP or Bricks Interactions

Skip if `PROJECT_BRIEF.md` › Motion already records a choice. Otherwise **ask
the user** which the site uses for animations and transitions:

- **GSAP** — effects adapted from the GSAP Prompt Library
  (https://gsap.brxprod.com/), loaded by BRXProd's `gsap-loader` snippet.
- **Bricks Interactions** — Bricks' own interactions and animations, tuned by
  BRXProd's tamed animations; no GSAP.

Write the answer into `PROJECT_BRIEF.md` › Motion. Then:

- **GSAP — ask a second question:** *"Should GSAP motion run in the Bricks
  editor?"* Recommend **No**: running effects in the editor makes it slower
  and harder to edit (elements hidden, moving or mid-animation while you
  work). Record the answer in `PROJECT_BRIEF.md` › Motion › *GSAP in the
  editor*. **No** → GSAP effect selectors you write are scoped to the live
  site with `body.bricks-is-frontend` (AGENTS.md › Motion › GSAP). **Yes** →
  selectors are left unscoped.
- **GSAP:** `novamira run brxprod/list-snippets --json` to confirm the
  `gsap-loader` id and whether its description includes the ScrollTrigger
  re-measure watcher (if not, tell the user to re-import the loader). Install
  it with `brxprod/install-snippet` if missing, and activate it (AGENTS.md ›
  Activating snippets). Effects are added later, per use, through
  `brxprod/get-gsap-effects` / `install-gsap-effect` (AGENTS.md › Motion ›
  GSAP); if those abilities aren't listed or the library is switched off
  (BRXProd → Settings → Features → GSAP Effects), say which switch. Don't
  install `fadein-fix` / `register-compound-animation` for this — they serve
  Bricks' animations.
- **Bricks Interactions:** offer `fadein-fix` and `register-compound-animation`
  (step 3's WARN lines) and no GSAP loader.

## 8. Report

A short checklist: connection, skills (versions, whether a new chat is
needed), status FAILs with their fixes, framework + house-rule set,
theme (light/dark) + role colours, or *colours deferred to the brief*, Surfaces state (`failing`, page follows Surface 1), design-system counts, brief state, motion choice, and a clear verdict:
**ready to build** or **blocked by …**.
