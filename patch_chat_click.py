import re

FILE = r"src\dashboard\static\js\app.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Make the toggle completely foolproof by exposing it to window
# or just querying the popup element directly on click
toggle_code = """
window.toggleGlobalChatbot = function() {
    const popup = document.getElementById('global-chatbot-popup');
    if (!popup) return;
    const isHidden = popup.style.display === 'none' || popup.style.display === '';
    popup.style.display = isHidden ? 'flex' : 'none';
    
    if (isHidden) {
        const input = document.getElementById('global-chatbot-input');
        const locSpan = document.getElementById('chat-context-loc');
        if (locSpan && window.__state_cache) {
            locSpan.innerText = (window.__state_cache.panchayat && window.__state_cache.panchayat.gp_name) ? window.__state_cache.panchayat.gp_name : 'None Selected';
        }
        if (input) input.focus();
    }
};

window.closeGlobalChatbot = function() {
    const popup = document.getElementById('global-chatbot-popup');
    if (popup) popup.style.display = 'none';
};
"""

code += toggle_code

# We need to save state for the global toggle
code = code.replace("subscribe((s) => {", "subscribe((s) => { window.__state_cache = s;")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

FILE_HTML = r"src\dashboard\templates\index.html"
with open(FILE_HTML, "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace('id="global-chatbot-btn"', 'id="global-chatbot-btn" onclick="window.toggleGlobalChatbot()"')
html = html.replace('id="global-chatbot-close"', 'id="global-chatbot-close" onclick="window.closeGlobalChatbot()"')

with open(FILE_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("Applied foolproof onclick handlers for global chatbot")
