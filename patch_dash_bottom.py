import os
import re

FILE = r"src\dashboard\static\js\tabs\dashboard.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# I will find the bottom cards row and remove it.
start = code.find("    <!-- BOTTOM CARDS ROW -->")
end = code.find("    </div><!-- /dash-bottom -->")

if start != -1 and end != -1:
    code = code[:start] + code[end + len("    </div><!-- /dash-bottom -->\n"):]

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Removed bottom cards row.")
