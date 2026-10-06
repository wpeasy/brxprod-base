---
name: init-brxprod
description: One-command setup (and re-check) of a BRXProd project — connects the site if needed, installs the BRXProd agent skills, checks the site is ready for agent work (Bricks abilities, BRXProd ability groups, framework, class sets, theme style, code manager, snippets), generates DESIGN_SYSTEM.md, creates PROJECT_BRIEF.md. Never offers or inserts Bricks Wireframes templates. Use when the user runs `/init-brxprod`, starts a new project from the base, or asks whether the project/site is ready to build on. Safe to re-run; done steps are skipped.
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
`facts` line (ability counts, framework, house-rule set, Bricks post types).

- **FAIL** lines block agent building. Relay each fix verbatim — they are
  switches only the site owner can turn on (Bricks → AI, BRXProd → Settings →
  AI Tools). Don't silently replace a disabled ability with execute-php — tell
  the user the switch and ask (AGENTS.md › Abilities first).
- **No `bricks/*` abilities** is the critical one: without Bricks' agent layer
  there is no supported way to create or edit pages, templates, classes or
  variables. Continue the remaining read-only steps, then report it as blocking.
- **WARN** lines are worth fixing but don't block. Offer what the agent can do:
  - missing bundled snippets (`header-height` — needed by the sticky-header
    CSS pattern; `fadein-fix`, `register-compound-animation` — animations) →
    `novamira run brxprod/install-snippet --input '{"id":"<id>"}'` (they land as
    Fluent Snippets **drafts**; never claim they are active);
  - snippets in draft → remind the user to review and activate them;
  - no Style Guide page → BRXProd's *Update Style Guide Page* (owner action).
- If `facts.bricksPostTypes` lacks a type the brief needs (e.g. `post`), say so:
  Bricks → Settings → Post types.

## 4. Design system

Run the **design-system** skill. Then confirm `DESIGN_SYSTEM.md` shows the
framework, the house-rule set (Code / Visual / Custom) and a concept map. Note
any *not found* concepts in the report.

## 5. Project brief

If `PROJECT_BRIEF.md` is missing, copy
`.claude/skills/init-brxprod/templates/PROJECT_BRIEF.md` to the project root.
Don't fill it in from guesses — ask the user to complete it (or to answer its
questions in chat, then write their answers in).

## 6. Report

A short checklist: connection, skills (versions, whether a new chat is
needed), status FAILs with their fixes, framework + house-rule set,
design-system counts, brief state, and a clear verdict:
**ready to build** or **blocked by …**.
