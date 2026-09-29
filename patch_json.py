import os

FILE = r"src\dashboard\app.py"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace('data = json.load(f)', 'import json\n            data = json.load(f)')

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Fixed json import.")
