import os

FILE = r"src\dashboard\static\js\tabs\downscaling.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Remove inline styles that break flex flow
code = code.replace('class="dash-layout" style="display:flex; gap:24px;"', 'class="dash-layout"')
code = code.replace('class="dash-left" style="flex:0 0 60%; display:flex; flex-direction:column; gap:24px;"', 'class="dash-left" style="flex:1;"')
code = code.replace('class="dash-right" style="flex:1; display:flex; flex-direction:column; gap:24px;"', 'class="dash-right" style="flex:1;"')

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Patched downscaling.js alignment")
