#!/bin/sh
# Install / update Bricks' agent skills (codeerhq/bricks-skills), following its
# README's release-managed install. Checks each part first; only what is
# missing or out of date is changed. Machine-wide (shared by every project):
#   - checkout:    ~/.bricks/skills/bricks-skills, pinned to the latest release
#   - Claude Code: marketplace `bricks-skills` (that checkout) + plugin bricks@bricks-skills
#   - Codex:       symlinks in ~/.agents/skills
# Run from the project root: sh .claude/skills/init-brxprod/scripts/install-bricks-skills.sh
set -u

REPO="https://github.com/codeerhq/bricks-skills.git"
CHECKOUT="$HOME/.bricks/skills/bricks-skills"
AGENTS_DIR="$HOME/.agents/skills"
FAILED=0

# 1. Release checkout — clone if missing, then let Bricks' own upgrade script
#    compare the local VERSION with the latest release (it exits early when current).
if git -C "$CHECKOUT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "BRICKS_CHECKOUT_PRESENT $CHECKOUT ($(cat "$CHECKOUT/VERSION" 2>/dev/null || echo unknown))"
else
  if [ -e "$CHECKOUT" ]; then
    echo "BRICKS_CHECKOUT_NOT_GIT $CHECKOUT — move it aside, then re-run"
    exit 2
  fi
  mkdir -p "$(dirname "$CHECKOUT")"
  if git clone --quiet "$REPO" "$CHECKOUT"; then
    echo "BRICKS_CHECKOUT_CLONED $CHECKOUT"
  else
    echo "BRICKS_CHECKOUT_CLONE_FAILED $REPO"
    exit 3
  fi
fi

if command -v node >/dev/null 2>&1; then
  # Prints BRICKS_SKILLS_ALREADY_CURRENT … or the upgrade it made.
  sh "$CHECKOUT/scripts/bricks-skills-upgrade" || FAILED=1
else
  echo "BRICKS_UPGRADE_SKIPPED node not found — the upgrade script needs Node.js"
  FAILED=1
fi

# 2. Claude Code — marketplace from the checkout, then the plugin.
if command -v claude >/dev/null 2>&1; then
  MARKETS=$(claude plugin marketplace list 2>/dev/null || true)
  if printf '%s\n' "$MARKETS" | grep -q "bricks-skills"; then
    echo "BRICKS_MARKETPLACE_PRESENT bricks-skills"
  elif claude plugin marketplace add "$CHECKOUT" >/dev/null 2>&1; then
    echo "BRICKS_MARKETPLACE_ADDED $CHECKOUT"
  else
    echo "BRICKS_MARKETPLACE_ADD_FAILED — run: /plugin marketplace add $CHECKOUT"
    FAILED=1
  fi

  PLUGINS=$(claude plugin list 2>/dev/null || true)
  if printf '%s\n' "$PLUGINS" | grep -q "bricks@bricks-skills"; then
    echo "BRICKS_PLUGIN_PRESENT bricks@bricks-skills"
  elif claude plugin install bricks@bricks-skills >/dev/null 2>&1; then
    echo "BRICKS_PLUGIN_INSTALLED bricks@bricks-skills"
  else
    echo "BRICKS_PLUGIN_INSTALL_FAILED — run: /plugin install bricks@bricks-skills"
    FAILED=1
  fi
else
  echo "BRICKS_CLAUDE_SKIPPED claude CLI not found"
fi

# 3. Codex (and other agents) — symlink each skill folder; existing links are left.
mkdir -p "$AGENTS_DIR"
ADDED=0
PRESENT=0
for skill in "$CHECKOUT"/skills/bricks-*; do
  [ -d "$skill" ] || continue
  link="$AGENTS_DIR/$(basename "$skill")"
  if [ -L "$link" ] && [ "$(readlink "$link")" = "$skill" ]; then
    PRESENT=$((PRESENT + 1))
  else
    ln -sfn "$skill" "$link" && ADDED=$((ADDED + 1))
  fi
done
echo "BRICKS_CODEX_LINKS present=$PRESENT added=$ADDED ($AGENTS_DIR)"

exit $FAILED
