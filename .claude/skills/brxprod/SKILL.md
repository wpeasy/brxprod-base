---
name: brxprod
description: House standards for building and styling on a Bricks site running the Bricks Productivity plugin (BRXProd). Use when writing CSS or applying classes on such a site, identifying which token framework it uses, applying BRXProd rails/corner/utility classes, regenerating the a11y text colours after a palette change, working with the Style Guide page, deciding where JavaScript or PHP should live, or installing snippets. Says what to delegate to Bricks' own abilities and what is genuinely this plugin's. For builder notes, use the brxprod-notes skill.
---

# Working on a BRXProd site

This covers **how we work**, not how Bricks works. Bricks ships its own agent
layer and that layer is the authority on Bricks itself.

## Rule 0: read the site's own instructions first

**Call `brxprod/get-design-instructions` before anything else.** It returns the
house rules the site owner has written: which tokens to use, how classes and
element labels are formed, which CSS practices are required, and where code is
allowed to live. It comes back as Markdown, both joined (`instructions`) and
split (`sections.general`, `.css`, `.code`).

**The response may carry additional sections the owner did not write** —
`sections.rails`, `.corners`, `.grids` — describing this plugin's own layout
systems. They are switched on per site and are **omitted entirely when the
system they describe is not installed**, so their presence is itself the signal
that the system is available here. Where one appears it is the authoritative
account of that system; prefer it over anything below.

**Those rules outrank this file.** This skill describes how BRXProd sites work
in general; that ability describes how *this* site works, and the owner can
change it without anyone republishing a skill. Where the two disagree, the site
wins.

**Two starting sets ship, and they are opposites**, so read rather than assume:

- **Code** — styling stays in CSS and never in Bricks' style controls; BEM
  names; container queries rather than `@media`.
- **Visual** — everything must land in Bricks' own controls; short `ai-`
  prefixed class names; Bricks' breakpoints, never container queries.

On a visual site the HTML/CSS import is expected to run with
`options.custom_css_policy: "forbid"`, which makes Bricks reject any candidate
needing a Code element or custom CSS. A `custom_css_forbidden` error there is
that policy working as intended: revise the source, and do not switch the
policy to `allow` without asking the owner first.

## Rule 1: use Bricks' own abilities and skills first

Bricks 2.4+ ships ~176 `bricks/…` abilities and its own skills. **Read
`bricks/…`'s own start-here guidance and load the relevant Bricks skill before
you write anything.** Its ability names use slashes (`bricks/get-design-context`);
the MCP tools use hyphens (`bricks-get-design-context`).

Bricks owns all of this — do not look for a BRXProd equivalent, and do not accept
a second-hand account of it from anywhere, including this file:

| task | Bricks owns it |
|---|---|
| element structure, ids, validation, normalisation | `bricks/get-page-elements`, `bricks/get-page-structure`, element validator/normaliser |
| creating or editing page content | `bricks/checkout-page-workspace`, `bricks/commit-site-edit-plan`, changesets |
| HTML/CSS → Bricks conversion | `bricks/commit-html-css-page-import` + the `bricks-html-css-to-bricks` skill |
| global classes, variables, categories, colours | `bricks/list-global-classes`, `bricks/list-global-variables`, `bricks/batch-create-global-classes`, `bricks/list-color-palettes` |
| theme styles, typography, breakpoints, pseudo-classes | `bricks/…` design + style-manager abilities |
| design system overview | `bricks/get-design-context` |
| render verification | `bricks/render-elements` |

Its save pipeline is journaled, idempotent and resumable, and it validates what
you send. Hand-building content and pushing it some other way loses all of that.

**BRXProd used to expose `get-design-tokens`, `get-typography`, `create-page` and
`update-page`. They have been removed** — each duplicated the Bricks ability less
capably, and two tools that disagree about the same site is worse than one
because you cannot tell which is authoritative. If you find them on an older
install, do not use them.

## Rule 2: what this plugin actually adds

Reach for BRXProd abilities only for these:

| ability | for |
|---|---|
| `brxprod/get-design-instructions` | the site's own house rules — **call this first**, they outrank this file |
| `brxprod/get-context` | which token framework this site runs, what BRXProd has installed, which code managers are present |
| `brxprod/find-style-guide` | locate the plugin-managed Style Guide page |
| `brxprod/render-frontend-html` | render an element as the FRONT END outputs it — Bricks' own render runs in builder mode |
| `brxprod/get-site-js` | read the site-wide custom scripts before proposing more |
| `brxprod/create-snippet` | store JavaScript or PHP you wrote, as a draft snippet |
| `brxprod/list-snippets`, `install-snippet` | install one of the plugin's own bundled snippets |
| `brxprod/get-diagnostics` | server / WP / plugin diagnostics for support |
| `brxprod/regenerate-a11y-colors` | recompute the `--brxp-a11y-*-text` variables after the site's colours change — see Rule 4 |

Each group is behind its own switch in **Settings → AI Tools → WordPress
Abilities**, all off by default except reads. `regenerate-a11y-colors` is in no
group: it is there whenever the Abilities master switch is on (`get-context`
lists it under `abilityGroups.ungrouped`), and it needs `manage_options`.

**If an ability you expect is missing, it is almost certainly switched off
rather than broken** — an unregistered ability and a nonexistent one look
identical from outside. `get-context` reports the group state: anything
it lists under `abilityGroups.unavailable` is off, and it names the switch. Tell
the user which one to turn on; do not work around it, and do not report a fault.

The common cases are `install-snippet` and `create-snippet`, both off by
default because they put runnable code on the site — and they are **separate
switches**, because installing something the plugin vetted and storing
something you just wrote are not the same risk. Notes is additionally Pro, so
on a free licence its switch cannot help.

There is no BRXProd ability that writes page content. That is not an oversight;
use Bricks'.

**Builder notes are a separate skill** — `brxprod-notes`. Six more abilities sit
behind it (`list-notes`, `create-note`, `update-note`, `delete-note`,
`list-note-groups`, `save-note-groups`). Nothing in this file is needed to use
them: Bricks has no notes feature, so none of the delegation rules apply there.

## Rule 3: establish which framework is in play before naming a token

A BRXProd site runs on one of three token systems, and **the same concept has a
different variable name in each**. Guessing produces CSS that references a
variable that does not exist, which resolves to nothing: the declaration is
dropped, no error is raised, and the spacing or colour is simply absent.

**`brxprod/get-context` answers this in one call** — it
reports the detected framework, the variable prefix actually in force, and what
BRXProd has installed. Prefer it over inferring the answer yourself.

If you are inferring it, read the variable list (`bricks/list-global-variables`
or `bricks/get-design-context`) and identify the system by prefix:

| you see | system |
|---|---|
| `brxw-*` (e.g. `brxw-space-l`, `brxw-grid-12`, `brxw-content-gap`) | **Bricks Wireframes** |
| unprefixed structural names (`--primary`, `--space-m`, `--gutter`, `--container`) | **Core Framework** |
| the same names under a user prefix (`--cf-space-m`) | Core Framework **with a prefix set** — follow whatever prefix is actually there |
| neither | the site's own framework, or none |

`brxp-*` is orthogonal — see Rule 4. Its presence tells you BRXProd features are
installed, not which framework the site uses. A site can have `brxw-*` and
`brxp-*` together, which is the common case.

**Never hardcode a framework's variable name into generated CSS.** Resolve the
concept against the list you just read. If the site has no variable for what you
need, say so and use a literal value — do not invent a plausible name.

**Core Framework's prefix is the user's to set.** Do not impose one, and do not
assume it is empty: third-party template libraries built for Core Framework
reference the bare names, so a prefixed install and an unprefixed one are both
normal. Read the actual names.

## Rule 4: BRXProd's own classes and variables

Installed by the plugin, under fixed, readable category ids:

| class category | classes |
|---|---|
| `brxp-layout-rails` | `brxp-rails`, `brxp-rail-content`, `brxp-rail-wide`, `brxp-rail-breakout`, `brxp-rail-layout`, `brxp-rail-full`, `brxp-gutter-x`, `brxp-gutter-left`, `brxp-gutter-right`, `brxp-has-bg-media`, `brxp-has-bg-media__media` |
| `brxp-corners` | 16 classes — `brxp-outset-radius-{corner}-{horizontal\|vertical}` and `brxp-inverted-radius-{corner}-{horizontal\|vertical}` |
| `brxp-utilities` | `brxp-line-clamp`, `brxp-line-clamp--2…6`, `brxp-list-none`, the zero-margin family (`brxp-m--0`, `brxp-mi--0`, `brxp-mb--0`, `brxp-mbs--0`, `brxp-mbe--0`, `brxp-mis--0`, `brxp-mie--0`) and its padding twin (`brxp-p--0`, `brxp-pi--0`, …), and the form colour schemes `brxp-form--dark` / `brxp-form--light` |

Variables live under the `brxp-layout` category ("Design Vars"): the rails
(`--brxp-page-gutter`, `--brxp-layout-width`, `--brxp-content-width`,
`--brxp-wide-width`, `--brxp-breakout-width`), the corner pair
(`--brxp-outset-radius`, `--brxp-outset-color`, `--brxp-inverted-radius`), plus
generated accessibility text colours (`--brxp-a11y-*-text`) and animation
variables.

**If `get-design-instructions` returned a `rails` or `corners` section, read
that instead of this rule** — it is generated from the same source that installs
the classes, so it cannot drift from them, whereas this file is a second account
written by hand. What follows is the summary for when those blocks are switched
off.

Three things to know before using them:

- **Check they exist on this site.** All of it is opt-in — installed by Process
  or the "Add BRXProd features" button. `get-context` reports which of
  the three class categories are installed and lists their class names, so there
  is no need to assume.
- **The two corner families work differently.** Outset paints its fillet with a
  pseudo-element, so an element has exactly **two** slots (`-horizontal` →
  `::before`, `-vertical` → `::after`) and a third pick silently renders nothing.
  Inverted is a mask over the element itself with **no such ceiling** — all four
  corners can be on at once. For inverted, `-horizontal` and `-vertical` are
  back-compat aliases for the same corner.
- **There is no `--inverted-color`.** The inverted mask cuts a real hole showing
  the true parent, so there is nothing to fill. A value written there is read by
  nothing.

**Style a Bricks Form with `brxp-form--dark` or `brxp-form--light`** rather
than hand-writing field CSS. Put the class on the Form element (or a wrapper
around the fields); its inputs, selects, choices, error messages and date-picker
popup take that scheme. Pick the one that suits the section's background. To
adjust it, set its public variables on the form or a parent, e.g.
`--brxp-form--dark-field-background` or `--brxp-form--light-field-border-color`.
Do not edit the class's own CSS (see below). Plugin 1.3.2 and later.

These are locked, plugin-owned classes. Hand-edits to their CSS are replaced on
the next install or Process run — if a rule needs changing, that is a plugin
change, not a site change.

**The `--brxp-a11y-*-text` variables are generated, not authored.** Each one is
the light or dark text colour that reads best on one palette colour or shade
(`--brxp-a11y-primary-text`, `--brxp-a11y-primary-d-2-text`, …). Use them as the
text colour on that background rather than picking one yourself. Do not set
their values by hand: after the site's colours change — a palette edit through
Bricks' abilities, or a Core Framework save — call
`brxprod/regenerate-a11y-colors`. It creates any variable a new shade needs and
updates the ones whose pick changed.

- It reads the BRX Prod palette (Bricks Wireframes), or Core Framework's
  colours when there is no palette.
- **Omit `method`** unless the user asked for one. It then uses the contrast
  method they last chose in the plugin, which is what the builder's Recalculate
  button would do. `wcag2` lets WCAG 2 AA decide and APCA break ties; `apca`
  follows APCA always and can fail WCAG 2 AA. The light and dark text colours
  are always the user's saved ones.
- Report `created` and `updated` from the response. An `abp_cf_unresolved`
  error means Core Framework's colours have not synced to Bricks: ask the user
  to click Save changes in Core Framework, then run it again.

## Rule 5: the managed Style Guide page

`brxprod/find-style-guide` locates it — it is identified by a marker
in post meta, not by its title, so searching for a page called "Style Guide" is
not the same question.

**Edit it with Bricks' own page abilities**, like any other page. BRXProd no
longer exposes a writer for it.

One thing to tell the user before you touch it: **the generator is
authoritative.** The plugin regenerates the page's `sg{n}-*` classes, so
hand-edits to those are replaced on the next *Update Style Guide Page*. The
supported workflow is to tune in the builder, then fold the change back into the
plugin's variant template. Edits to your own content on that page are safe.

## Rule 6: where code goes

**Never put JavaScript or PHP in a Bricks Code element.** A Code element ties
the script to one element on one page, runs wherever that element happens to be
placed, and is invisible to anyone looking for the site's scripts.

Use a **code manager**, so generated code lives apart from code the site owner
wrote by hand and can be read, disabled or deleted as a unit.
`brxprod/get-context` reports `codeManager` — every manager it found in
`detected`, and whether you can write one yourself in `canCreateSnippet`.

Then:

1. **`canCreateSnippet` true** → `brxprod/create-snippet` with
   `language: php | js | css | html`. It lands as a **draft** in the BRXProd
   group.
2. **Another manager installed** (WPCode, Code Snippets, WPCodeBox, Advanced
   Scripts…) → that is a perfectly good home. Write the code and hand it over
   for the user to add. Do not offer to install a different one.
3. **None at all** → stop and ask: install Fluent Snippets, or, for JavaScript
   only, use Bricks' Site/Page settings via the plugin's JavaScript Panel. PHP
   has no fallback.

**Fluent Snippets is preferred for one concrete reason** — it is the manager
this plugin can write to directly, so code lands without a copy-paste step.
That is convenience, not a judgement about the others.

**Never activate a snippet, and never say you have.** `create-snippet` produces
a draft and there is no ability that activates one. PHP runs on every request
and a mistake takes the site down, so enabling it is the user's decision. Say
where it is and what it does.

`install-snippet` is the separate case: it installs one of the **plugin's own
bundled snippets** by id, also as a draft in the BRXProd group. It cannot
install arbitrary code — the source is read server-side.

Both need `unfiltered_html` **and** `install_plugins` — the same pair Fluent
Snippets demands of its own UI — and both groups are off by default. On
single-site WordPress an Editor holds `unfiltered_html` without
`install_plugins`, so an Editor cannot write snippets through these abilities
either.

**You cannot write the JavaScript Panel's own fields.** Its block sits inside a
marker fence in the user's field and splicing that fence is done in exactly one
place, so nothing else can drift from it and clobber somebody's script. Read
them with `brxprod/get-site-js`; to change them, hand the code over.

## Rule 7: say what you did not verify

**`brxprod/render-frontend-html` is the one thing that can show you real
output.** Every Bricks render path runs in builder mode, which replaces the
children of nestable elements (nav, dropdown, accordion, slider, tabs,
offcanvas, back-to-top) with a placeholder — so Bricks' own render cannot show
you what you just built inside one. Use ours to check.

Beyond that, a write response is not proof the result looks right — Bricks' own
guidance says the same, and it matters more here because BRXProd's rails and
corner classes are geometric.

When you finish, say plainly what you did not see, and point at what most needs a
human eye. Do not describe a page you have not viewed as looking good.
