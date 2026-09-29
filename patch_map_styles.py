import os

FILE = r"src\dashboard\static\js\tabs\map.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

original_select1 = """style="height:38px;border-radius:8px;border:1px solid #D1D5DB;padding:0 12px;
                       font-size:13px;background:#fff;color:#1F2937;cursor:pointer;outline:none;\""""
new_select = 'style="height:40px;border-radius:6px;border:1px solid #DDE6ED;padding:0 12px;font-size:14px;background:#fff;color:#17324D;cursor:pointer;outline:none;"'

code = code.replace(original_select1, new_select)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Patched map.js select styles")
