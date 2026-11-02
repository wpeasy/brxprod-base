---
name: brxprod-gsap
description: Add, change, update, remove and uninstall GSAP animation effects on a Bricks site running the Bricks Productivity plugin (BRXProd) — hover/scroll effects for buttons, text, media, SVG and boxes from the gsap.brxprod.com library. Use when asked to animate an element, add a hover or scroll effect, make a button or heading do something, tune an effect's options, see where effects are used, update effects, or remove or uninstall one. Never write GSAP by hand on such a site. For general building and styling, use the brxprod skill.
---

# BRXProd GSAP effects

BRXProd bundles a library of verified GSAP effects. **Use it instead of writing GSAP,
pasting library code into a snippet, or fetching the website.** An effect is three things
that must stay together: a published Fluent snippet, a locked global class `brxp-fx-<id>`
that carries its CSS and is the JavaScript's selector, and (on the element) that class plus
its option attributes. The abilities below keep them together; a hand-built effect skips the
per-effect init marker and the shared GSAP Loader and behaves differently.

Bricks has no equivalent, so none of Bricks' own abilities replace these. Generic element
work (structure, text, other styling) is still Bricks'; see the `brxprod` skill.

## Before anything: `brxprod/get-gsap-status`

Call it first. It never fails because the feature is off; it says so, and says what to do:

- `featureOn: false` — the user has not switched on **Settings → Features → GSAP Effects**
  (experimental, off by default, per user). Ask them to. Do not work around it.
- `fluentSnippets: false` — Fluent Snippets must be installed and active. Ask.
- `outdated` — installed effects behind the bundled version: run `update-gsap-effects`.

If a `brxprod/…-gsap-…` ability is missing from your tool list, the **GSAP effects** group is
off (**Settings → AI Tools → WordPress Abilities**). `brxprod/get-context` names the switch
under `abilityGroups`. Tell the user; do not report a fault.

## The nine abilities

| ability | for |
|---|---|
| `get-gsap-status` | ready? switch, Fluent, loader, catalogue version, installed and outdated |
| `get-gsap-effects` | list (filter by `category`), or one effect in full with `id`: options, claims, target note, required inner classes, CSS |
| `get-gsap-effect-usage` | every element on every page, template, header and footer that carries an effect |
| `install-gsap-effect` | snippet + loader + plugin lines + global class, in one idempotent step |
| `update-gsap-effects` | refresh outdated effects (one `id`, or all outdated); elements keep their class and options |
| `uninstall-gsap-effect` | remove snippet and class; refuses while elements use it; `force` strips them first |
| `apply-gsap-effect` | put an effect on an element, with options; installs it first if needed |
| `set-gsap-effect-options` | change the options of an effect already on an element |
| `remove-gsap-effect` | take an effect off one element |

All of them need the same permissions as the builder's GSAP Effects window (`unfiltered_html`,
`install_plugins`, Bricks create-global-classes and code execution), and the element ones also
need to be allowed to edit that post with Bricks.

## Choosing an effect

1. `get-gsap-effects` with a `category` (`buttons`, `text`, `media`, `svg`, `boxes`). Read
   `whatItDoes`, `trigger` and `role`.
2. `get-gsap-effects` with the `id` for the full entry. **Read `target` and `markupNotes`
   before applying**: they say which element it goes on and what must be inside it.
3. The `role` decides where the class goes:
   - `self` — on the button, heading or text itself.
   - `container` — on the wrapper; the effect animates what is **inside** it. The children must be
     real elements (Blocks, cards, list items). **A container effect cannot work on bare Image
     elements** — an `<img>` cannot hold the layer the effect adds. Wrap each image in a Block with
     the class `gsap-box`. `apply-gsap-effect` warns about both an empty container and bare images.
   - an effect may also name `requiredClasses` — an inner element with that class (for example
     `card-caption`). The apply result warns when it is missing.

## Applying and options

```
apply-gsap-effect { postId, elementId, id: "BOX-16", options: { "data-box-16-trigger": "both" } }
```

- `area` is `content` (default), `header` or `footer`. Find `elementId` with Bricks' own page read.
- **Options are the effect's own `data-*` attributes**, and only the ones `get-gsap-effects`
  lists for that effect (not deprecated, not a child marker). Types and `choices` are enforced. An
  empty string or `null` removes the attribute so the effect default applies again. Write only
  what the user asked to change.
- **Styling is not an option.** Colours, sizes and radii are CSS variables (`--gsap-<id>-…`) on the
  effect's class `brxp-fx-<id>`, with site-wide `--gsap-*` theme tokens as the fallback. Edit the class's
  variables with Bricks' own abilities; never restyle by editing the snippet.
- **Clashes.** Effects declare what they take over (`claims`). If another effect on the element — or a
  page-wide claim elsewhere on the page — clashes, `apply-gsap-effect` answers `claim_clash` with the
  effects named. **Stop and tell the user.** Retry with `acknowledgeClashes: true` only when they agree.
- **Never edit text on an element that has an effect in the canvas.** The editor keeps effect elements
  non-editable on purpose (clicking in and typing saved the effect's own markup into the content). Text is
  changed in the element's settings, which is what a Bricks ability writes.

## Updating, removing, uninstalling

- `remove-gsap-effect` takes it off one element and clears its own option attributes (they are namespaced per
  effect, so other effects' and the user's attributes are untouched). The effect stays installed.
- `uninstall-gsap-effect` removes it from the site. If elements still use it you get `effect_in_use` with the
  places: **list them to the user and ask** before using `force: true`, which strips every one. It refuses even
  with `force` when a Bricks **component** uses the effect (these abilities do not edit components); the user
  removes it there in the builder. The shared GSAP Loader is never removed. Not reversible.
- Do not remove an effect to "reset" it: `update-gsap-effects` or `install-gsap-effect` refresh it in place.

## After you write

- **An editor tab that is already open on the same page or class list overwrites what you wrote on its next save**
  (Bricks saves the whole list). Tell the user to reload the editor.
- Class creation and the page write go through Bricks' own save, so Bricks' own change tracking is fine, but a
  write is not proof the effect runs. To confirm, render the front end (`brxprod/render-frontend-html`) and, for
  anything scroll- or hover-driven, say plainly that you did not watch it animate unless you did.
- Report what changed: effect id, class, element ids, options, any `warnings`.
