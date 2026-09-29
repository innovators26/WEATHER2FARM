import re

FILE = r"src\dashboard\static\js\tabs\risk.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Fix syntax error in grid-template-columns logic
bad_str = r"grid-template-columns: ${risks.length === 1 ? \'1fr\' : \'repeat(auto-fit, minmax(450px, 1fr))\'};"
good_str = r"grid-template-columns: ${risks.length === 1 ? '1fr' : 'repeat(auto-fit, minmax(450px, 1fr))'};"
code = code.replace(bad_str, good_str)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Fixed syntax error")
