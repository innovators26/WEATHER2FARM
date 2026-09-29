import re

FILE = r"src\dashboard\static\js\tabs\risk.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Fix actionStr inside buildRiskCard
buildRiskCard_fix = """
    let actionStr = "Monitor conditions.";
    if (adv.avoid && adv.avoid.length > 0 && (s === 'HIGH' || s === 'SEVERE')) {
        actionStr = "Avoid: " + adv.avoid.map(a => t(a)).join(', ');
    } else if (actions.length > 0) {
        actionStr = t(actions[0].action); // fallback
    } else {
        actionStr = t(actionStr);
    }
"""

old_buildRiskCard_logic = """
    let actionStr = "Monitor conditions.";
    if (adv.avoid && adv.avoid.length > 0 && (s === 'HIGH' || s === 'SEVERE')) {
        actionStr = "Avoid: " + adv.avoid.join(', ');
    } else if (actions.length > 0) {
        actionStr = actions[0].action; // fallback
    }
"""

if old_buildRiskCard_logic.strip() in code:
    code = code.replace(old_buildRiskCard_logic.strip(), buildRiskCard_fix.strip())
else:
    # try regex
    old_logic_re = re.search(r'let actionStr = "Monitor conditions\.";.*?actionStr = actions\[0\]\.action; // fallback\s*}', code, re.DOTALL)
    if old_logic_re:
        code = code.replace(old_logic_re.group(0), buildRiskCard_fix.strip())
    else:
        print("WARNING: Could not find actionStr logic in buildRiskCard")

# Also, the HTML inside buildRiskCard:
# Since actionStr is already translated in my fix, I should remove `t(actionStr)` from the HTML and just use `actionStr`.
code = code.replace('>${t(actionStr)}</div>', '>${actionStr}</div>')

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Patched buildRiskCard translations")
