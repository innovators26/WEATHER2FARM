import os
import re

FILE = r"src\dashboard\app.py"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("}rt load_dotenv\nload_dotenv()", "}\n\nfrom dotenv import load_dotenv\nload_dotenv()")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Fixed syntax error.")
