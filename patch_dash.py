import os

FILE = r"src\dashboard\static\js\tabs\dashboard.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Farm Advisory chunk:
advisory_start = code.find("<!-- Farm Advisory -->")
advisory_end = code.find("<!-- Model Status -->")

if advisory_start != -1 and advisory_end != -1:
    code = code[:advisory_start] + code[advisory_end:]

# 2. Model Status chunk:
model_start = code.find("<!-- Model Status -->")
model_end = code.find("<!-- Feedback -->")

if model_start != -1 and model_end != -1:
    code = code[:model_start] + code[model_end:]

# 3. Feedback chunk:
fb_start = code.find("<!-- Feedback -->")
fb_end = code.find("<!-- System Status -->")

if fb_start != -1 and fb_end != -1:
    code = code[:fb_start] + code[fb_end:]

# Now we need to remove the Javascript code that attaches listeners to these removed elements.
# The user said: "Remove unnecessary Dashboard-only code that exists solely to render: today's advisory preview, model status preview, rainfall feedback preview"

js_fb_start = code.find("const btnYes = document.getElementById('dashRainYes');")
js_fb_end = code.find("});\n\n  // Render mini map", js_fb_start)
if js_fb_start != -1 and js_fb_end != -1:
    code = code[:js_fb_start] + code[js_fb_end:]

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Removed HTML and JS chunks.")
