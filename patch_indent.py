import os
import re

FILE = r"src\dashboard\app.py"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Remove all local import json that precede data = json.load(f)
code = re.sub(r"^[ \t]*import json\n[ \t]*data = json\.load\(f\)", r"        data = json.load(f)", code, flags=re.MULTILINE)

# Some might be slightly different indent
code = re.sub(r"^[ \t]*import json\n[ \t]*with open", r"        with open", code, flags=re.MULTILINE)

# Then explicitly re-add import json at the top level just in case it got deleted
if "\nimport json\n" not in code and "\nimport json\r\n" not in code:
    code = "import json\n" + code

# Let's fix indentation for data = json.load(f) to always be 12 spaces if it's inside `with open`
code = re.sub(r"with open\((.*?)\) as f:\n[ \t]*data = json\.load\(f\)", r"with open(\1) as f:\n            data = json.load(f)", code)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Fixed indentation.")
