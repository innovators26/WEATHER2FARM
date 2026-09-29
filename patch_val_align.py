import os

FILE = r"src\dashboard\static\js\tabs\validation.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace('font-size:22px;', 'font-size:26px; line-height:1.2;')
code = code.replace('class="dash-bottom" style="margin-bottom:24px;"', 'class="weather-metrics-grid" style="margin-bottom:24px;"')

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Patched validation.js metrics alignment")
