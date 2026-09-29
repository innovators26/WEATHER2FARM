import os

FILE = r"src\dashboard\static\css\style.css"
with open(FILE, "r", encoding="utf-8") as f:
    css = f.read()

css = css.replace('#risk-tab > div > div[style*="display:grid"] {\n    grid-template-columns: repeat(3, 1fr) !important;\n    gap: 20px !important;\n}', '')
css = css.replace('#risk-tab > div > div[style*="display:grid"] {\n        grid-template-columns: 1fr !important;\n    }', '')

with open(FILE, "w", encoding="utf-8") as f:
    f.write(css)

print("Removed bad risk-tab grid override")
