#!/bin/sh
# Install / update the BRXProd agent skills into this project's .claude/skills/.
# Run from the project root: sh .claude/skills/init-brxprod/scripts/install-skills.sh
set -eu

REPO="https://github.com/wpeasy/bricks-productivity-skills.git"
SKILLS="brxprod brxprod-notes brxprod-feedback"

DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$DIR/../../../.." && pwd)
DEST="$ROOT/.claude/skills"
STAMP="$DEST/.brxprod-skills-version"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

git clone --quiet --depth 1 "$REPO" "$TMP/repo"
COMMIT=$(git -C "$TMP/repo" rev-parse --short HEAD)
PREVIOUS=$(cat "$STAMP" 2>/dev/null || echo "none")

for skill in $SKILLS; do
  [ -f "$TMP/repo/skills/$skill/SKILL.md" ] || { echo "missing skills/$skill/SKILL.md in $REPO" >&2; exit 1; }
  rm -rf "$DEST/$skill"
  mkdir -p "$DEST/$skill"
  cp -R "$TMP/repo/skills/$skill/." "$DEST/$skill/"
done

echo "$COMMIT" > "$STAMP"
if [ "$PREVIOUS" = "$COMMIT" ]; then
  echo "BRXPROD_SKILLS_CURRENT $COMMIT"
else
  echo "BRXPROD_SKILLS_INSTALLED $PREVIOUS -> $COMMIT ($SKILLS)"
fi
