#!/usr/bin/env python3
"""Read-only readiness check for a BRXProd project and its site.

Usage (from the project root):
    python3 .claude/skills/init-brxprod/scripts/status.py [--json]

Prints a checklist. Each line is PASS / WARN / FAIL with the fix the user (not
the agent) should make. Nothing here writes to the site or the project.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "design-system", "scripts"))
from render import house_rule_set  # noqa: E402  (shared with DESIGN_SYSTEM.md)

# Bundled BRXProd snippets the standards rely on: id -> Fluent Snippets file stem.
SNIPPETS = {
    "header-height": "header-footer-heights",  # --brxp-header-height (sticky-header pattern)
    "fadein-fix": "fix-fadein-compound",
    "register-compound-animation": "register-compound-animation",
}

# Read-only probe; executed with --yes only because the CLI treats every
# execute-php call as destructive.
PROBE_PHP = r"""
$ts = (array) get_option('bricks_theme_styles', []);
$styles = [];
$css = '';
foreach ($ts as $id => $s) {
    $styles[] = ['label' => $s['label'] ?? $id, 'conditions' => count((array) ($s['settings']['conditions']['conditions'] ?? []))];
    $css .= (string) ($s['settings']['css']['stylesheet'] ?? '');
}
$markers = [];
foreach (['BRXP_LAYOUT_RAILS', 'BRXP_INVERTED_RADIUS', 'BRXP_OUTSET_RADIUS'] as $m) $markers[$m] = strpos($css, $m . '_START') !== false;
$markers['ANIMATION_OVERRIDES'] = strpos($css, 'Bricks Animation Overrides') !== false;
$snips = [];
$dir = WP_CONTENT_DIR . '/fluent-snippet-storage';
foreach ((array) glob($dir . '/*.php') as $f) {
    if (basename($f) === 'index.php') continue;
    $head = (string) file_get_contents($f, false, null, 0, 2000);
    preg_match('/@status:\s*(\S+)/', $head, $st);
    $snips[basename($f)] = $st[1] ?? '?';
}
$gs = (array) get_option('bricks_global_settings', []);
return [
    'themeStyles' => $styles,
    'markers' => $markers,
    'snippets' => $snips,
    'bricksPostTypes' => array_values((array) ($gs['postTypes'] ?? [])),
    'bricksTemplates' => (int) wp_count_posts('bricks_template')->publish,
];
"""


def novamira(*args, payload=None):
    cmd = ["novamira"] + list(args) + ["--json"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=120).stdout
        doc = json.loads(out)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)
    if not doc.get("ok", False):
        return None, (doc.get("error") or {}).get("code", "error")
    return doc.get("data"), None


def run_php(code):
    path = os.path.join(os.environ.get("TMPDIR", "/tmp"), "brxprod-status-%d.json" % os.getpid())
    with open(path, "w") as fh:
        json.dump({"code": code}, fh)
    try:
        data, err = novamira("--yes", "run", "novamira/execute-php", "--input", "@" + path)
    finally:
        os.remove(path)
    if data and data.get("success") is False:
        return None, data.get("error_message")
    return (data or {}).get("return_value"), err


def main():
    rows = []
    facts = {}

    def add(status, area, message, fix=""):
        rows.append({"status": status, "area": area, "message": message, "fix": fix})

    # --- Project -----------------------------------------------------------
    if not (os.environ.get("NOVAMIRA_HOME") and os.environ.get("NOVAMIRA_SITE")):
        add("FAIL", "Connection", "NOVAMIRA_HOME / NOVAMIRA_SITE not set", "run /setup-site <url>")
        return finish(rows, facts)

    stamp = os.path.join(ROOT, ".claude", "skills", ".brxprod-skills-version")
    if os.path.exists(stamp):
        add("PASS", "Skills", "BRXProd skills installed (%s)" % open(stamp).read().strip())
    else:
        add("FAIL", "Skills", "BRXProd skills not installed in this project", "run install-skills.sh")
    try:
        plugins = subprocess.run(["claude", "plugin", "list"], capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.TimeoutExpired):
        plugins = ""
    if "bricks@bricks-skills" in plugins:
        add("PASS", "Skills", "Bricks agent skills plugin (bricks@bricks-skills) installed")
    else:
        add("FAIL", "Skills", "Bricks agent skills plugin not found",
            "/plugin marketplace add codeerhq/bricks-skills, then /plugin install bricks@bricks-skills")

    # --- Site --------------------------------------------------------------
    doctor, err = novamira("doctor")
    if not doctor or doctor.get("status") != "pass":
        failing = [c["id"] for c in (doctor or {}).get("checks", []) if c.get("status") != "pass"]
        add("FAIL", "Connection", "novamira doctor failed: %s" % (", ".join(failing) or err),
            "fix the failing check; re-run /setup-site if the token is invalid")
        return finish(rows, facts)
    add("PASS", "Connection", "novamira doctor passes")

    listing, _ = novamira("discover")
    items = listing if isinstance(listing, list) else (listing or {}).get("abilities", [])
    names = [i["name"] if isinstance(i, dict) else i for i in items]
    counts = {ns: sum(n.startswith(ns + "/") for n in names) for ns in ("bricks", "brxprod", "novamira")}
    facts["abilities"] = counts
    if counts["bricks"]:
        add("PASS", "Bricks", "%d bricks/* abilities available" % counts["bricks"])
    else:
        add("FAIL", "Bricks", "no bricks/* abilities — Bricks' agent layer is off",
            "WordPress admin → Bricks → AI: enable the Bricks Abilities API")
    for needed in ("bricks/list-remote-templates", "bricks/insert-remote-template"):
        facts[needed] = needed in names

    ctx, err = novamira("run", "brxprod/get-context")
    if not ctx:
        add("FAIL", "BRXProd", "brxprod/get-context unavailable (%s)" % err,
            "BRXProd → Settings → AI Tools → WordPress Abilities: enable Read-only tools")
        return finish(rows, facts)
    fw = ctx.get("framework") or {}
    facts["framework"] = fw.get("detected")
    facts["prefix"] = fw.get("variablePrefix")
    status = "PASS" if fw.get("detected") in ("bricks-wireframes", "core-framework") else "WARN"
    add(status, "Framework", "%s (prefix `%s`)" % (fw.get("detected"), fw.get("variablePrefix") or ""),
        "" if status == "PASS" else "install Bricks Wireframes (insert a Wireframes template) or Core Framework")

    groups = ((ctx.get("abilityGroups") or {}).get("groups")) or {}
    for key, why in (("reads", "required"), ("createCode", "needed to store JS/PHP"), ("snippets", "needed to install bundled snippets")):
        g = groups.get(key) or {}
        if g.get("enabled"):
            add("PASS", "BRXProd", "ability group '%s' on" % g.get("label", key))
        else:
            add("FAIL" if key == "reads" else "WARN", "BRXProd", "ability group '%s' off (%s)" % (g.get("label", key), why),
                "BRXProd → Settings → AI Tools → WordPress Abilities")

    sets = ((ctx.get("brxprod") or {}).get("classCategories")) or {}
    missing = [v.get("label", k) for k, v in sets.items() if not v.get("installed")]
    add("WARN" if missing else "PASS", "BRXProd",
        "class sets missing: " + ", ".join(missing) if missing else "rails, corner and utility class sets installed",
        "BRXProd: Add BRXProd features" if missing else "")
    code = ctx.get("codeManager") or {}
    if code.get("canCreateSnippet"):
        add("PASS", "Code", "code manager: %s (agent can write drafts)" % ", ".join(code.get("detected") or []))
    elif code.get("detected"):
        add("WARN", "Code", "code manager %s — agent hands code over to paste" % ", ".join(code["detected"]))
    else:
        add("WARN", "Code", "no code manager — JS/PHP has nowhere to go", "install Fluent Snippets")
    sg = ctx.get("styleGuide") or {}
    add("PASS" if sg.get("exists") else "WARN", "BRXProd",
        "Style Guide page ID %s" % sg.get("pageId") if sg.get("exists") else "no Style Guide page",
        "" if sg.get("exists") else "BRXProd: Update Style Guide Page")

    instr, err = novamira("run", "brxprod/get-design-instructions")
    if instr:
        rule_set = house_rule_set(instr.get("instructions", ""))
        facts["houseRules"] = rule_set
        add("PASS", "House rules", "%s set%s; sections: %s" % (
            rule_set, " (default)" if instr.get("isDefault") else " (customised)",
            ", ".join(sorted((instr.get("sections") or {}).keys()))))
    else:
        add("FAIL", "House rules", "brxprod/get-design-instructions unavailable (%s)" % err)

    probe, err = run_php(PROBE_PHP)
    if probe:
        active = [s["label"] for s in probe["themeStyles"] if s["conditions"]]
        add("PASS" if active else "WARN", "Theme style",
            "active: " + ", ".join(active) if active else "no theme style has conditions — none applies",
            "" if active else "give the framework's theme style a site-wide condition")
        m = probe["markers"]
        missing = [k for k, v in m.items() if not v]
        add("WARN" if missing else "PASS", "BRXProd",
            "theme stylesheet missing: " + ", ".join(missing) if missing else "rails, corners and animation overrides in theme stylesheet",
            "BRXProd → Features: re-run Process / Animation Overrides" if missing else "")
        snips = probe["snippets"]
        for sid, fname in SNIPPETS.items():
            hit = [(f, st) for f, st in snips.items() if fname in f]
            if not hit:
                add("WARN", "Snippets", "%s not installed" % sid, "init offers: brxprod/install-snippet {\"id\":\"%s\"} (draft)" % sid)
            else:
                add("PASS" if hit[0][1] == "published" else "WARN", "Snippets", "%s: %s" % (sid, hit[0][1]),
                    "" if hit[0][1] == "published" else "review and activate in Fluent Snippets")
        facts["bricksTemplates"] = probe["bricksTemplates"]
        facts["bricksPostTypes"] = probe["bricksPostTypes"]
        add("PASS" if probe["bricksPostTypes"] else "WARN", "Bricks",
            "Bricks enabled for: " + (", ".join(probe["bricksPostTypes"]) or "no post types"),
            "" if probe["bricksPostTypes"] else "Bricks → Settings → Post types")
    else:
        add("WARN", "Site", "read-only probe failed (%s)" % err)

    # --- Project docs ------------------------------------------------------
    ds = os.path.join(ROOT, "DESIGN_SYSTEM.md")
    add("PASS" if os.path.exists(ds) else "FAIL", "Docs",
        "DESIGN_SYSTEM.md present" if os.path.exists(ds) else "DESIGN_SYSTEM.md missing", "" if os.path.exists(ds) else "run /design-system")
    brief = os.path.join(ROOT, "PROJECT_BRIEF.md")
    if not os.path.exists(brief):
        add("WARN", "Docs", "PROJECT_BRIEF.md missing", "init creates the template")
    elif "_TODO_" in open(brief).read():
        add("WARN", "Docs", "PROJECT_BRIEF.md still has _TODO_ fields", "fill it in so the agent can write content")
    else:
        add("PASS", "Docs", "PROJECT_BRIEF.md filled in")
    return finish(rows, facts)


def finish(rows, facts):
    if "--json" in sys.argv:
        print(json.dumps({"checks": rows, "facts": facts}, indent=1))
    else:
        for r in rows:
            print("%-4s  %-12s %s%s" % (r["status"], r["area"], r["message"], ("  →  " + r["fix"]) if r["fix"] else ""))
        print("\nfacts: " + json.dumps(facts))
    return 1 if any(r["status"] == "FAIL" for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
