import os
FILE = r"src\dashboard\static\js\tabs\validation.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace('class="dash-bottom" style="margin-bottom:24px;"', 'class="weather-metrics-grid" style="margin-bottom:24px;"')
code = code.replace('class="card" style="display:flex;align-items:center;gap:14px;"', 'class="card metric-card"')

# Fix inline styles for font size in metrics
code = code.replace('style="font-size:30px;', 'class="metric-icon" style="font-size:30px;')
code = code.replace('style="font-size:12px;color:var(--text-muted);"', 'class="metric-label"')
code = code.replace('style="font-size:22px;font-weight:700;"', 'class="metric-val"')
code = code.replace('style="font-size:22px;font-weight:700;color:var(--success);"', 'class="metric-val" style="color:var(--success) !important;"')

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Patched validation.js metrics")
