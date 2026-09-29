import os
import re

FILES = [
    r"src\dashboard\static\js\tabs\dashboard.js",
    r"src\dashboard\static\js\tabs\map.js",
    r"src\dashboard\static\js\tabs\downscaling.js",
    r"src\dashboard\static\js\tabs\advisory.js",
    r"src\dashboard\static\js\tabs\validation.js",
    r"src\dashboard\static\js\tabs\risk.js",
    r"src\dashboard\static\js\tabs\feedback.js"
]

def patch_file(filepath):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath}")
        return
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Replace hardcoded dash-layout flex stuff
    content = content.replace('class="dash-layout" style="display:flex; gap:24px;"', 'class="dash-layout"')
    content = content.replace('class="dash-left" style="flex:0 0 60%; display:flex; flex-direction:column; gap:24px;"', 'class="dash-left dash-equal"')
    content = content.replace('class="dash-right" style="flex:1; display:flex; flex-direction:column; gap:24px;"', 'class="dash-right dash-equal"')
    
    content = content.replace('class="dash-left" style="flex:0 0 40%;"', 'class="dash-left dash-equal"')
    content = content.replace('class="dash-right" style="flex:0 0 60%;"', 'class="dash-right dash-equal"')

    # Remove arbitrary padding from containers
    content = re.sub(r'style="padding: \d+px;"', '', content)
    content = re.sub(r'style="padding:\d+px;"', '', content)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        
for f in FILES:
    patch_file(f)
    
print("Patched flex layouts")
