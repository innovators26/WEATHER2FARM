import os
import re

FILE = r"src\dashboard\static\css\style.css"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

patterns_to_remove = [
    r"\.dash-bottom \{.*?\n",
    r"\.sys-list \{.*?\n",
    r"\.sys-item \{.*?\n",
    r"\.sys-status \{.*?\n",
    r"\.dash-bottom \{ grid-template-columns:.*?\n"
]

for p in patterns_to_remove:
    code = re.sub(p, "", code)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Cleaned CSS.")
