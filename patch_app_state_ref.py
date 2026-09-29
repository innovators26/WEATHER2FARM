import re

FILE = r"src\dashboard\static\js\app.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Replace window.__APP_STATE with state
code = code.replace('const st = window.__APP_STATE || {};', 'const st = state;')

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Fixed state reference in app.js")
