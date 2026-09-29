import re

FILE = r"src\dashboard\static\css\style.css"
with open(FILE, "r", encoding="utf-8") as f:
    css = f.read()

# I need to carefully remove #risk-tab from the common page headers rules in style.css

# 1. Remove #risk-tab from max-width wrapper
css = css.replace("#advisory-tab, #validation-tab, #risk-tab {", "#advisory-tab, #validation-tab {")

# 2. Remove from media queries
css = css.replace("#advisory-tab, #validation-tab, #risk-tab { width: calc(100% - 40px); }", "#advisory-tab, #validation-tab { width: calc(100% - 40px); }")
css = css.replace("#advisory-tab, #validation-tab, #risk-tab { width: calc(100% - 32px); }", "#advisory-tab, #validation-tab { width: calc(100% - 32px); }")

# 3. CRITICAL: Remove from the flex-row header!
bad_rule1 = """
#advisory-tab > div:first-child, 
#validation-tab > div:first-child, 
#risk-tab > div:first-child {
    display: flex;
    align-items: baseline;
    gap: 16px;
    margin-bottom: 24px;
}
"""
good_rule1 = """
#advisory-tab > div:first-child, 
#validation-tab > div:first-child {
    display: flex;
    align-items: baseline;
    gap: 16px;
    margin-bottom: 24px;
}
"""
css = css.replace(bad_rule1.strip(), good_rule1.strip())

bad_rule2 = """
#advisory-tab h1, #validation-tab h1, #risk-tab h1 {
    font-size: 26px !important;
    font-weight: 700;
    color: var(--primary);
    margin: 0;
}
"""
good_rule2 = """
#advisory-tab h1, #validation-tab h1 {
    font-size: 26px !important;
    font-weight: 700;
    color: var(--primary);
    margin: 0;
}
"""
css = css.replace(bad_rule2.strip(), good_rule2.strip())

bad_rule3 = """
#advisory-tab > div:first-child span, 
#validation-tab > div:first-child span, 
#risk-tab > div:first-child span {
    font-size: 15px;
    color: var(--text-muted);
}
"""
good_rule3 = """
#advisory-tab > div:first-child span, 
#validation-tab > div:first-child span {
    font-size: 15px;
    color: var(--text-muted);
}
"""
css = css.replace(bad_rule3.strip(), good_rule3.strip())

with open(FILE, "w", encoding="utf-8") as f:
    f.write(css)

print("Cleaned up style.css for risk-tab")
