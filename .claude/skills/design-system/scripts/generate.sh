#!/bin/sh
# Regenerate DESIGN_SYSTEM.md from the connected site.
# Run from the project root: sh .claude/skills/design-system/scripts/generate.sh
set -eu

DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$DIR/../../../.." && pwd)

: "${NOVAMIRA_SITE:?NOVAMIRA_SITE is not set - run /setup-site first}"
: "${NOVAMIRA_HOME:?NOVAMIRA_HOME is not set - run /setup-site first}"
command -v python3 >/dev/null 2>&1 || { echo "python3 is required" >&2; exit 1; }

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# Framework detection is BRXProd's job; an error here is tolerated and
# render.py falls back to inferring from variable prefixes.
novamira run brxprod/get-context --json > "$TMP/context.json" 2>/dev/null || true

python3 -c 'import json,sys; print(json.dumps({"code": open(sys.argv[1]).read()}))' \
  "$DIR/extract.php" > "$TMP/input.json"

# extract.php is read-only; --yes only satisfies the CLI's blanket
# "execute-php is destructive" confirmation.
novamira --yes run novamira/execute-php --input "@$TMP/input.json" --json > "$TMP/data.json"

python3 "$DIR/render.py" "$TMP/context.json" "$TMP/data.json" "$ROOT/DESIGN_SYSTEM.md"
