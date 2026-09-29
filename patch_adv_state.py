import os
import re

FILE = r"src\dashboard\static\js\tabs\advisory.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Hide the Result card and Chat card initially, and give them IDs if they don't have one
# Result card: <div class="card" style="height:100%;min-height:400px;display:flex;flex-direction:column;">
code = code.replace(
    '<div class="card" style="height:100%;min-height:400px;display:flex;flex-direction:column;">',
    '<div class="card" id="advResultCard" style="display:none;height:100%;min-height:400px;flex-direction:column;">'
)

# Chat card: <div class="card" style="margin-top:20px;">
code = code.replace(
    '<div class="card" style="margin-top:20px;">',
    '<div class="card" id="advChatCard" style="display:none;margin-top:20px;">'
)

# 2. Remove advEmpty completely
adv_empty_start = code.find('<div id="advEmpty"')
if adv_empty_start != -1:
    adv_empty_end = code.find('</div>\n\n          <div id="advResult"', adv_empty_start)
    if adv_empty_end != -1:
        # We need to remove the whole block.
        # But wait, it's safer to just replace it with empty string
        # Let's use regex
        code = re.sub(r'<div id="advEmpty".*?</div>\s*</div>', '', code, flags=re.DOTALL)
        
# 3. Change advResult so it's not hidden (since its parent advResultCard is hidden)
code = code.replace('<div id="advResult" style="display:none;flex-direction:column;gap:24px;">', '<div id="advResult" style="display:flex;flex-direction:column;gap:24px;">')

# 4. In JS logic, remove references to advEmpty
code = code.replace("document.getElementById('advEmpty').style.display = 'none';", "")

# 5. In JS logic, when generate button is clicked, hide the cards until done
generate_start = code.find("document.getElementById('genAdvBtn').addEventListener('click', async () => {")
if generate_start != -1:
    # Insert hide logic at the beginning
    btn_logic = """const btn = document.getElementById('genAdvBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> Generating...';
    
    // Hide previous result
    document.getElementById('advResultCard').style.display = 'none';
    document.getElementById('advChatCard').style.display = 'none';"""
    
    # Replace the existing btn logic
    code = re.sub(r"const btn = document.getElementById\('genAdvBtn'\);\s*btn\.disabled = true;\s*btn\.innerHTML = '<i class=\"ph ph-spinner\"></i> Generating...';", btn_logic, code)

# 6. In JS logic, when generate is successful, show the cards
code = code.replace("document.getElementById('advResult').style.display = 'flex';", """document.getElementById('advResultCard').style.display = 'flex';
      document.getElementById('advChatCard').style.display = 'block';""")

# 7. In JS logic, when parameters change, hide the cards
hide_logic = """
    const resCard = document.getElementById('advResultCard');
    const chatCard = document.getElementById('advChatCard');
    if (resCard) resCard.style.display = 'none';
    if (chatCard) chatCard.style.display = 'none';
"""

# Crop change
crop_change = """document.getElementById('advCrop').addEventListener('change', e => {
      updateState({ crop: e.target.value });"""
code = code.replace(crop_change, crop_change + hide_logic)

# Date change
date_change = """document.getElementById('advDate').addEventListener('change', e => {
      updateState({ sowingDate: e.target.value });"""
code = code.replace(date_change, date_change + hide_logic)

# Also when Panchayat changes globally?
# The render function is called when global state changes, which re-renders the whole HTML!
# So since they are display:none by default in the HTML string, changing panchayat will re-render the tab and they will be hidden automatically!

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Patched advisory.js initial state logic")
