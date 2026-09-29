import os
import re

FILE = r"src\dashboard\static\js\tabs\dashboard.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Remove the dashRainYes / dashRainNo lines
code = re.sub(r"document\.getElementById\('dashRainYes'\)\.addEventListener.*\n", "", code)
code = re.sub(r"document\.getElementById\('dashRainNo'\)\.addEventListener.*\n", "", code)
code = re.sub(r"// Wire quick feedback buttons\n", "", code)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Removed remaining JS chunks.")
