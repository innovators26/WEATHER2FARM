import os

APP_FILE = r"src\dashboard\app.py"
with open(APP_FILE, "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    'print(f"[CHAT] Groq response received: {answer[:50]}...")',
    'print(f"[CHAT] Groq response received: {answer[:50].encode(\'ascii\', \'ignore\').decode(\'ascii\')}...")'
)

with open(APP_FILE, "w", encoding="utf-8") as f:
    f.write(code)
print("Patched logging unicode.")
