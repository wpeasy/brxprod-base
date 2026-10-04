---
name: init-brxprod
description: One-command setup (and re-check) of a BRXProd project — connects the site if needed, installs the BRXProd agent skills, checks the site is ready for agent work (Bricks abilities, BRXProd ability groups, framework, class sets, theme style, code manager, snippets), generates DESIGN_SYSTEM.md, creates PROJECT_BRIEF.md, and on Bricks Wireframes sites offers Wireframes templates. Use when the user runs `/init-brxprod`, starts a new project from the base, or asks whether the project/site is ready to build on. Safe to re-run; done steps are skipped.
---

# /init-brxprod [site-url]

Gets a project to the point where the agent can build pages, posts, templates
and content with **Bricks' own skills and abilities first**, BRXProd's rules on
top, and the installed framework's tokens. Every step is idempotent: re-running
refreshes and re-checks rather than redoing.

Run the steps in order. Report progress in one line per step.

## 1. Connect

If `NOVAMIRA_HOME` / `NOVAMIRA_SITE` are not set, or `novamira doctor --json`
fails on the profile, run the **setup-site** skill (with the URL argument if
given; otherwise ask for it). Otherwise skip.

## 2. Skills

```bash
sh .claude/skills/init-brxprod/scripts/install-skills.sh
```

Installs/updates `brxprod`, `brxprod-notes`, `brxprod-feedback` from
`wpeasy/bricks-productivity-skills` into `.claude/skills/` (committed with the
project; version in `.claude/skills/.brxprod-skills-version`). It prints
`BRXPROD_SKILLS_CURRENT` or `BRXPROD_SKILLS_INSTALLED old -> new`.

Bricks' own skills come from the `bricks@bricks-skills` Claude Code plugin. If
the status check (step 3) reports it missing, tell the user to run
`/plugin marketplace add codeerhq/bricks-skills` and
`/plugin install bricks@bricks-skills` — plugin installs need their approval.

New or updated skills load in a **new chat**; say so if anything changed.

## 3. Site status

```bash
python3 .claude/skills/init-brxprod/scripts/status.py
```

Read-only. Prints PASS / WARN / FAIL lines, each FAIL/WARN with the fix, and a
`facts` line (ability counts, framework, house-rule set, Bricks post types,
remote-template ability availability).

- **FAIL** lines block agent building. Relay each fix verbatim — they are
  switches only the site owner can turn on (Bricks → AI, BRXProd → Settings →
  AI Tools). **Never work around a disabled ability** (e.g. with execute-php
  writes).
- **No `bricks/*` abilities** is the critical one: without Bricks' agent layer
  there is no supported way to create or edit pages, templates, classes or
  variables. Continue the remaining read-only steps, then stop before step 5.
- **WARN** lines are worth fixing but don't block. Offer what the agent can do:
  - missing bundled snippets (`header-height` — needed by the sticky-header
    CSS pattern; `fadein-fix`, `register-compound-animation` — animations) →
    `novamira run brxprod/install-snippet --input '{"id":"<id>"}'` (they land as
    Fluent Snippets **drafts**; never claim they are active);
  - snippets in draft → remind the user to review and activate them;
  - no Style Guide page → BRXProd's *Update Style Guide Page* (owner action).
- If `facts.bricksPostTypes` lacks a type the brief needs (e.g. `post`), say so:
  Bricks → Settings → Post types.
- A *Bricks content ignored (Rendered with WordPress)* WARN lists posts whose
  Bricks data the front end skips. Relay the fix (admin bar → **Render with
  Bricks** on each one's WordPress edit screen). A builder Save does not fix
  it, and execute-php must not write the meta (AGENTS.md › Known issues).

## 4. Design system

Run the **design-system** skill. Then confirm `DESIGN_SYSTEM.md` shows the
framework, the house-rule set (Code / Visual / Custom) and a concept map. Note
any *not found* concepts in the report.

## 5. Wireframes templates (Bricks Wireframes sites only)

Skip unless `facts.framework` is `bricks-wireframes` and both remote-template
abilities are available. **Never on a Core Framework site** — inserting imports
the template's `brxw-*` design assets and would put a second framework on the
site. Load `bricks:bricks-templates-conditions` first; all writes here are
Bricks abilities.

1. `novamira describe` both `bricks/list-remote-templates` and
   `bricks/insert-remote-template` — the schemas are authoritative over this file.
2. List the library: `bricks/list-remote-templates` with
   `{"source":"wireframes","perPage":100}` (summary mode; page through all
   ~180). Each entry has `id`, `title`, `name`, `type` (section, header,
   footer…) and `bundles` (category: heroes, ctas, testimonials, slider…).
   Group by bundle.
3. **Propose** a set: from `PROJECT_BRIEF.md` when filled in (one or two options
   per section type its pages need), otherwise a starter set — one header, one
   footer, and a hero, features, testimonial and CTA section. Show title,
   bundle and thumbnail URL; wait for approval. Insert nothing unapproved.
4. For each approved template, make it a **saved Bricks template** — never
   insert into a page:
   1. `bricks/create-template` with `title` = the remote title, `type` = the
      remote `type`, `status: "publish"`, no elements, **no conditions**.
   2. `bricks/insert-remote-template` with `source: "wireframes"`,
      `remoteTemplateId`, `targetPostId` = the new template, `position:
      "replace"`, `importDesignAssets: "missing"` (keeps existing tokens),
      `importImages: false`. On the first insert into a site with no active
      theme style, also pass `applyThemeStyle: true`.
5. Verify with `bricks/list-templates`. A header/footer template must not have
   become site-wide: confirm it has no conditions.
6. Re-run step 4 (design system) — the inserts may have added `brxw-*`
   variables, classes or palettes. BRXProd's optional *Bricks Wireframe* tool
   (convert the variables to Bricks Scales and categories) is an owner action
   in BRXProd; mention it, don't attempt it.

The `design-sets` source also exists; its sets carry their own design assets,
so it is out of scope for init — use it only on an explicit request.

## 6. Project brief

If `PROJECT_BRIEF.md` is missing, copy
`.claude/skills/init-brxprod/templates/PROJECT_BRIEF.md` to the project root.
Don't fill it in from guesses — ask the user to complete it (or to answer its
questions in chat, then write their answers in). When the user gives only an
outline (business, place, audience), write their answers in and leave every
fact they didn't give — names, contact details, prices, statistics, team,
testimonials — as `_TODO_`; list those in section 9.

## 7. Report

A short checklist: connection, skills (versions, whether a new chat is
needed), status FAILs with their fixes, framework + house-rule set,
design-system counts, templates inserted, brief state, and a clear verdict:
**ready to build** or **blocked by …**.
