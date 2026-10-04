@AGENTS.md

## Claude Code specifics

- Invoke skills as `/init-brxprod`, `/setup-site`, `/design-system`.
- Bricks' skills come from the `bricks@bricks-skills` plugin
  (`/plugin marketplace add codeerhq/bricks-skills`,
  `/plugin install bricks@bricks-skills`) and appear as `bricks:<skill>`.
- `.claude/settings.json` (shared) allows `novamira` and the project scripts and
  makes login, site switching and `NOVAMIRA_*` overrides **ask** first.
  `.claude/settings.local.json` (per site, gitignored) holds `NOVAMIRA_HOME` /
  `NOVAMIRA_SITE`.
