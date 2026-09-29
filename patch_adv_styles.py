import os
import re

FILE = r"src\dashboard\static\js\tabs\advisory.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Replace height:42px with 40px and border-radius:8px with 6px for all form elements
code = code.replace("height:42px;", "height:40px;")
code = code.replace("height:46px;", "height:40px;")
code = code.replace("border-radius:8px;", "border-radius:6px;")

# But for advAnswer (chat bubbles) keep border-radius:8px, let's just do a specific replace for the inputs
code = code.replace('style="width:100%;height:40px;border-radius:6px;border:1px solid var(--border);padding:0 12px;font-size:14px;"',
                    'style="width:100%;height:40px;border-radius:6px;border:1px solid #CBD5E1;padding:0 12px;font-size:14px;box-sizing:border-box;"')

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Patched advisory.js forms")
