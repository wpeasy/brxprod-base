# BRXProd base project

A starting point for building WordPress sites with **Bricks Builder** and the
**Bricks Productivity** plugin (BRXProd) using [Claude Code](https://claude.com/claude-code).

Each project made from this template connects to **one** site and gives the
agent everything it needs to build pages, posts, templates and content the way
we do: Bricks' own skills and abilities first, BRXProd's rules on top, and the
site's own framework tokens — Bricks Wireframes or Core Framework.

## Requirements

**On the site**

- WordPress with **Bricks 2.4+**, and **Bricks → AI** (the Bricks Abilities API) enabled
- **Bricks Productivity** with its abilities on (Settings → AI Tools → WordPress Abilities)
- **Novamira** (provides the connection)
- A token framework: **Bricks Wireframes** or **Core Framework**
- A code manager — **Fluent Snippets** recommended (the agent can write drafts to it)

**On your machine**

- Claude Code
- Node.js 22.20+ (for the Novamira CLI), `python3`, `git`
- The Bricks agent skills plugin:

  ```
  /plugin marketplace add codeerhq/bricks-skills
  /plugin install bricks@bricks-skills
  ```

## Quick start

1. **Use this template** on GitHub to create a repository for the site, and
   clone it.
2. In the new repository, delete the per-site lines from `.gitignore`
   (`DESIGN_SYSTEM.md`, `PROJECT_BRIEF.md`) so the site's files get committed.
3. Open the folder in Claude Code and run:

   ```
   /init-brxprod https://example.com/
   ```

   Approve the login in your browser when asked.
4. Fill in `PROJECT_BRIEF.md`, then start a new chat and start building.

Re-run `/init-brxprod` any time to re-check that the site is ready; finished
steps are skipped.

## What `/init-brxprod` does

| Step | |
|---|---|
| **Connect** | Logs in to the site through the Novamira CLI and pins this project to it (see *Site isolation*). |
| **Skills** | Installs the BRXProd skills (`brxprod`, `brxprod-notes`, `brxprod-feedback`) and checks the Bricks skills plugin. |
| **Status** | Read-only readiness check — Bricks abilities, BRXProd ability groups, framework, class sets, theme style, code manager, snippets, Style Guide. Every problem comes with the switch to fix it. |
| **Design system** | Generates `DESIGN_SYSTEM.md` from the live site. |
| **Wireframes** | On Bricks Wireframes sites, proposes templates from the brief and saves the ones you approve as Bricks templates. |
| **Brief** | Creates `PROJECT_BRIEF.md` for you to fill in. |
| **Report** | Ends with *ready to build* or *blocked by …*. |

The agent never turns on a disabled ability or activates code itself — it tells
you which switch to use.

## Project layout

```
CLAUDE.md                 How the agent works in every project (loaded each session)
standards/
  css.md                  CSS, BEM and label standard
  js.md                   JavaScript standard
  examples/               Reference Bricks builds
.claude/
  settings.json           Shared permission rules
  skills/
    init-brxprod/         One-command setup and status check
    setup-site/           Connection step on its own
    design-system/        Generates DESIGN_SYSTEM.md
    brxprod*/             BRXProd skills (installed by init)

Per site — created by init, not in this template:
  DESIGN_SYSTEM.md        Framework, tokens, concept map, classes
  PROJECT_BRIEF.md        Business, audience, voice, pages, content
  .claude/settings.local.json, .claude/novamira/   Site connection (never committed)
```

## DESIGN_SYSTEM.md

Generated from the site by `/design-system` (run by init; re-run whenever the
site's variables, classes or palettes change). Its **concept map** turns
framework-neutral ideas — "spacing M", "section padding", "brand colour" — into
the site's real token names, so the standards work on both frameworks and the
agent never invents a variable.

Only the fenced region is regenerated. Notes you add under *Project notes*
survive.

## Standards

- **[CSS](standards/css.md)** — BEM classes; labels match the BEM name in
  Title Case; all component CSS in the block class; a `/* Settings */` block of
  `--_private: var(--public, token)` variables; Settings-only modifiers;
  container queries, never `@media`.
- **[JavaScript](standards/js.md)** — IIFE, ES6+, browser APIs first, events
  instead of timers (including Bricks' frontend events).
- **PHP** — to be specified.

Order of authority: **Bricks' skills and abilities** → the site's BRXProd
design instructions → `CLAUDE.md` and `standards/` → other skills.

## Site isolation

A project can only reach its own site:

- `/init-brxprod` gives the project a private Novamira profile store
  (`.claude/novamira/`) holding exactly one site, and pins it in
  `.claude/settings.local.json`. Both are gitignored.
- The access token is kept in the OS keychain, not in the repository.
- Shared rules in `.claude/settings.json` make the agent ask before logging in,
  switching sites or overriding the connection.

## Updating

- **BRXProd skills:** re-run `/init-brxprod` (or
  `sh .claude/skills/init-brxprod/scripts/install-skills.sh`). The installed
  version is in `.claude/skills/.brxprod-skills-version`.
- **Bricks skills:** `/plugin marketplace update bricks-skills`.
- **This template:** pull improvements from it into a site repository as you
  would any upstream.
