import re

FILE = r"src\dashboard\static\js\tabs\advisory.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Remove the DOM for advChatCard
# The card starts with <div class="card" id="advChatCard" style="display:none;margin-top:20px;">
# and ends right before <!-- Result Block --> or at the end of the template string
chat_dom = re.search(r'<!-- Voice Input -->.*?</div>\s*</div>\s*</div>\s*<!-- RIGHT: Result -->', code, re.DOTALL)
if chat_dom:
    code = code.replace(chat_dom.group(0), '</div>\n\n      <!-- RIGHT: Result -->')
else:
    # It was moved after the Result block in my earlier patch!
    # "Now insert chat_section AFTER the Advisory Result block"
    # Let's just find `<!-- Voice Input -->` to the end of the card
    chat_dom2 = re.search(r'<!-- Voice Input -->.*?</div>\s*</div>\s*</div>', code, re.DOTALL)
    if chat_dom2:
        # Check if the matched string actually contains advChatCard
        if 'advChatCard' in chat_dom2.group(0):
            # We want to remove the card but not accidentally remove closing tags for other divs
            # The advChatCard has an outer <div class="card" id="advChatCard">, its card-title, flex inputs, advVoiceMsg, advAnswer, and closing div.
            pass
            
# Let's use a simpler regex for the chat DOM
code = re.sub(r'<!-- Voice Input -->.*?<div id="advAnswer".*?</div>\s*</div>', '', code, flags=re.DOTALL)

# Remove JS logic references to advChatCard
code = code.replace("document.getElementById('advChatCard').style.display = 'none';", "")
code = code.replace("const chatCard = document.getElementById('advChatCard');", "")
code = code.replace("if (chatCard) chatCard.style.display = 'none';", "")
code = code.replace("document.getElementById('advChatCard').style.display = 'block';", "")

# Remove Voice Input JS and Chatbot API logic
js_chat_logic = re.search(r'// Voice input.*}\n\n}\n', code, re.DOTALL)
if js_chat_logic:
    code = code.replace(js_chat_logic.group(0), '}\n')
else:
    # Try finding it till end of file
    js_chat_logic = re.search(r'// Voice input.*', code, re.DOTALL)
    if js_chat_logic:
        code = code.replace(js_chat_logic.group(0), '}\n')

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Removed chat from advisory.js")
