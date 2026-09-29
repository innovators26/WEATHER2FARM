import os
import re

FILE = r"src\dashboard\static\css\style.css"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

code = re.sub(r"\.dash-bottom \{ display: grid; grid-template-columns: repeat\(4, 1fr\); gap: 20px; \}",
              r".dash-bottom { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }", code)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated dash-bottom grid.")
