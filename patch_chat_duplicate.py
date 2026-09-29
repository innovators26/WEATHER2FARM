import re

FILE = r"src\dashboard\static\js\app.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# I will use regex to completely remove initGlobalChatbot and its setTimeout
# The function starts at: function initGlobalChatbot() {
# and the setTimeout block starts at: // Initialize chatbot directly

# Find the start of the old GLOBAL CHATBOT LOGIC
start_idx = code.find('/* =====================================================================\n   GLOBAL CHATBOT LOGIC\n   ===================================================================== */')

# Find the start of the new window.toggleGlobalChatbot
end_idx = code.find('window.toggleGlobalChatbot = function() {')

if start_idx != -1 and end_idx != -1:
    # Remove everything between them!
    code = code[:start_idx] + '\n/* GLOBAL CHATBOT STATE */\n' + code[end_idx:]

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Removed duplicate event listeners from app.js")
