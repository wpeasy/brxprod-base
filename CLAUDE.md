@AGENTS.md

## Claude Code specifics

- Invoke skills as `/init-brxprod`, `/setup-site`, `/design-system`.
- Bricks' skills come from the `bricks@bricks-skills` plugin
  (`/plugin marketplace add codeerhq/bricks-skills`,
  `/plugin install bricks@bricks-skills`) and appear as `bricks:<skill>`.
- `.claude/settings.json` (shared) allows `novamira` and the project scripts,
  so they run without prompting. Nothing blocks login, site switching or
  `NOVAMIRA_*` overrides — the *Connection* rules in AGENTS.md are the guard.
  `.claude/settings.local.json` (per site, gitignored) holds `NOVAMIRA_HOME` /
  `NOVAMIRA_SITE`.
