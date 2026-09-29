import os

FILE = r"src\dashboard\static\js\tabs\advisory.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Replace dash-layout and its left/right wrappers
start_marker = '<div class="dash-layout">'
end_marker = '<!-- /dash-right -->'

# We need to restructure the HTML. It's safer to just provide the new HTML string.
# Let's extract the top part of render up to `<div class="dash-layout">`
parts = code.split('<div class="dash-layout">')
if len(parts) > 1:
    before_layout = parts[0]
    rest = parts[1]
    
    # We will replace the entire inner HTML of the container up to ``;
    
    # Actually, it's easier to just find the exact strings and replace them.
    # Turn dash-left into a full width container
    code = code.replace('<div class="dash-layout">', '<div class="dash-layout-vertical" style="display:flex; flex-direction:column; gap:24px;">')
    code = code.replace('<div class="dash-left" style="flex:0 0 40%;">', '<!-- Top Params Block --><div>')
    code = code.replace('<div class="dash-right" style="flex:0 0 60%;">', '<!-- Result Block --><div>')
    
    # Now we need to make the Advisory Parameters a horizontal grid.
    # It is currently `<div style="display:flex;flex-direction:column;gap:16px;">`
    # Let's change it to a grid.
    code = code.replace('<div style="display:flex;flex-direction:column;gap:16px;">', '<div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:16px; align-items:end;">')
    
    # The Chat Section ("Ask About Your Crop") needs to move below the Advisory Result.
    # Let's extract it.
    chat_start = code.find('<!-- Voice Input -->')
    chat_end = code.find('</div>\n\n      <!-- RIGHT: Result -->')
    
    if chat_start != -1 and chat_end != -1:
        chat_section = code[chat_start:chat_end + 6]
        code = code[:chat_start] + code[chat_end + 6:]
        
        # Now insert chat_section AFTER the Advisory Result block
        # Find end of Advisory Result
        result_end = code.find('</div>\n          </div>\n        </div>\n      </div>')
        if result_end != -1:
            code = code[:result_end + 25] + '\n\n' + chat_section + code[result_end + 25:]

    # Ensure buttons have equal height with inputs
    code = code.replace('height:46px;', 'height:40px;')
    code = code.replace('height:42px;', 'height:40px;')
    
    with open(FILE, "w", encoding="utf-8") as f:
        f.write(code)
    
    print("Rewritten advisory.js HTML layout")
else:
    print("dash-layout not found in advisory.js")
