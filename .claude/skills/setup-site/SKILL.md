---
name: setup-site
description: Connect this project (a copy of the BRXProd base project) to its one WordPress site through the Novamira CLI, isolated so it can never reach another site — project-local NOVAMIRA_HOME profile store, pinned NOVAMIRA_SITE, OAuth login, doctor check, then DESIGN_SYSTEM.md. Use when the user runs `/setup-site <site-url>`, starts a new project from the base, or asks to connect/reconnect this project to a site.
---

# /setup-site <site-url>

Gives this project its own Novamira profile store containing exactly one site,
and pins it. Every `novamira` command run from this project then reaches only
that site; another site's login cannot be seen from here, and this site cannot be
seen from other projects.

Several commands below set `NOVAMIRA_*` inline or call `novamira auth`, so the
project's `ask` rules will prompt the user for each — that is intended.

## 1. Preconditions

- **URL** — the argument. If missing, ask for it. Normalise to the site's home
  URL (e.g. `https://example.com/` or a subdirectory install `https://host/site/`).
- **CLI** — `command -v novamira`. If missing, tell the user and offer the
  official installer (`curl -fsSL https://raw.githubusercontent.com/use-novamira/novamira-cli/main/install.sh | env NOVAMIRA_AGENT='claude-code' sh`);
  run it only with their go-ahead.
- **Existing connection** — read `.claude/settings.local.json` and list
  `.claude/novamira/`. If a profile already exists:
  - same site → this is a reconnect; skip to step 2 (re-login) only if
    `novamira doctor --json` fails on the token.
  - **different site** → STOP. The folder was copied from another project.
    Ask before deleting `.claude/novamira/` and replacing the settings.

## 2. Log in into the project-local store

`H` is the absolute path of `<project root>/.claude/novamira` — compute it with
`pwd`; never hard-code another project's path.

```bash
mkdir -p .claude/novamira && chmod 700 .claude/novamira
NOVAMIRA_HOME="$H" novamira auth login '<site-url>'
```

Run it in the foreground with a long timeout (it waits up to 5 minutes for the
user to approve in the browser). If the browser flow fails, times out, cannot
open a browser, or the session is headless, retry with `--device`, show the user
the verification URL and code, and keep it running until approved.

The token goes to the macOS Keychain (or the OS credential store), keyed by
origin + profile name — not into the project folder.

## 3. Pin the profile

```bash
NOVAMIRA_HOME="$H" novamira sites list --json
```

Exactly one profile must be listed; take its `name`. Then merge into
`.claude/settings.local.json`, preserving any other keys:

```json
{ "env": { "NOVAMIRA_HOME": "<H>", "NOVAMIRA_SITE": "<profile name>" } }
```

Do not touch `.claude/settings.json` — the permission rules there are shared by
every project made from the base.

## 4. Verify

```bash
NOVAMIRA_HOME="$H" NOVAMIRA_SITE='<profile>' novamira doctor --json
```

Require `"status":"pass"`. Report WordPress / plugin versions and the ability
count. If `site.permission` or `oauth.token` fails, the account that approved
access lacks Novamira management permission — say so.

Then check BRXProd's abilities: `novamira run brxprod/get-context --json`. If
it is `ability_not_found`, the owner must enable them under **Settings → AI
Tools → WordPress Abilities** in BRXProd — tell them, don't work around it.

## 5. Generate the design system

Skip this when `/init-brxprod` called you — it runs the design system itself.
Otherwise run the `/design-system` skill. Its script reads the env vars, so if this
session does not yet see the new values, prefix the command with the same
`NOVAMIRA_HOME=… NOVAMIRA_SITE=…`.

## 6. Report

Site URL, profile, framework detected, design-system counts, and that a new
chat may be needed for the env vars to apply everywhere. Remind the user, if
this is a site project rather than the base, to delete the per-site lines
(`DESIGN_SYSTEM.md`, `PROJECT_BRIEF.md`) from `.gitignore` so they are committed.
