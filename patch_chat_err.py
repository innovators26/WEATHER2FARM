import os

APP_FILE = r"src\dashboard\app.py"
with open(APP_FILE, "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("if \"rate_limit\" in str(e).lower()", "print('GROQ ERROR:', e)\n        if \"rate_limit\" in str(e).lower()")

with open(APP_FILE, "w", encoding="utf-8") as f:
    f.write(code)
    print("Patched error logging.")
