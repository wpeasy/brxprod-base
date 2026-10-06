#!/bin/sh
# Install / update the BRXProd agent skills into this project's .claude/skills/.
# Checks first: if the installed version matches the repo's latest commit and
# every skill is present, nothing is downloaded.
# Run from the project root: sh .claude/skills/init-brxprod/scripts/install-skills.sh
set -eu

REPO="https://github.com/wpeasy/bricks-productivity-skills.git"
SKILLS="brxprod brxprod-notes brxprod-feedback"

DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$DIR/../../../.." && pwd)
DEST="$ROOT/.claude/skills"
STAMP="$DEST/.brxprod-skills-version"
PREVIOUS=$(cat "$STAMP" 2>/dev/null || echo "none")

# 1. Check: latest commit on the repo vs the installed stamp.
LATEST=$(git ls-remote "$REPO" HEAD 2>/dev/null | cut -c1-7)
if [ -z "$LATEST" ]; then
  echo "BRXPROD_SKILLS_CHECK_FAILED could not reach $REPO (installed: $PREVIOUS)"
  exit 3
fi

MISSING=""
for skill in $SKILLS; do
  [ -f "$DEST/$skill/SKILL.md" ] || MISSING="$MISSING $skill"
done

if [ "$PREVIOUS" = "$LATEST" ] && [ -z "$MISSING" ]; then
  echo "BRXPROD_SKILLS_CURRENT $LATEST"
  exit 0
fi

# 2. Install / update.
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

git clone --quiet --depth 1 "$REPO" "$TMP/repo"
COMMIT=$(git -C "$TMP/repo" rev-parse --short=7 HEAD)

for skill in $SKILLS; do
  [ -f "$TMP/repo/skills/$skill/SKILL.md" ] || { echo "missing skills/$skill/SKILL.md in $REPO" >&2; exit 1; }
  rm -rf "$DEST/$skill"
  mkdir -p "$DEST/$skill"
  cp -R "$TMP/repo/skills/$skill/." "$DEST/$skill/"
done

echo "$COMMIT" > "$STAMP"
echo "BRXPROD_SKILLS_INSTALLED $PREVIOUS -> $COMMIT ($SKILLS)"
