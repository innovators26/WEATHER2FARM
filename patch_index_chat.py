import re

FILE = r"src\dashboard\templates\index.html"
with open(FILE, "r", encoding="utf-8") as f:
    html = f.read()

chatbot_ui = """
    <!-- Global Chatbot -->
    <div id="global-chatbot-btn" style="position:fixed; right:24px; bottom:24px; width:56px; height:56px; border-radius:50%; background:var(--primary); color:#fff; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 12px rgba(0,0,0,0.15); cursor:pointer; z-index:9999; transition:0.2s;">
      <i class="ph-fill ph-chat-circle-dots" style="font-size:28px;"></i>
    </div>

    <div id="global-chatbot-popup" style="display:none; position:fixed; right:24px; bottom:90px; width:360px; max-height:520px; background:#fff; border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.15); z-index:9999; flex-direction:column; overflow:hidden; border:1px solid var(--border);">
      <div style="background:var(--primary-dark); color:#fff; padding:16px; display:flex; justify-content:space-between; align-items:center;">
        <div style="display:flex; align-items:center; gap:8px;">
          <i class="ph-fill ph-robot" style="font-size:20px;"></i>
          <span style="font-weight:600; font-size:15px;" data-i18n="chat.title">Weather2Farm AI</span>
        </div>
        <i class="ph ph-x" id="global-chatbot-close" style="cursor:pointer; font-size:20px;"></i>
      </div>
      <div style="background:#F8FAFC; padding:8px 16px; border-bottom:1px solid var(--border); font-size:12px; color:var(--text-muted); display:flex; gap:6px; align-items:center;">
        <i class="ph-fill ph-map-pin"></i> Context: <strong id="chat-context-loc">Loading...</strong>
      </div>
      <div id="global-chatbot-messages" style="flex:1; padding:16px; overflow-y:auto; display:flex; flex-direction:column; gap:12px; background:#fff; height:320px;">
        <div style="background:var(--primary-bg); padding:12px; border-radius:8px; font-size:13px; color:var(--text-main); border-bottom-left-radius:0; max-width:85%; line-height:1.4;">
          Hello! I am the Weather2Farm AI. How can I help you with your crop or weather decisions today?
        </div>
      </div>
      <div style="padding:12px; border-top:1px solid var(--border); display:flex; gap:8px; background:#fff;">
        <input type="text" id="global-chatbot-input" placeholder="Type your question..." style="flex:1; height:40px; border-radius:20px; border:1px solid #CBD5E1; padding:0 16px; font-size:13px; outline:none;">
        <button id="global-chatbot-send" style="height:40px; width:40px; border-radius:50%; background:var(--primary); color:#fff; border:none; cursor:pointer; display:flex; align-items:center; justify-content:center;">
          <i class="ph-fill ph-paper-plane-right"></i>
        </button>
      </div>
    </div>
"""

# Inject before </main>
if '<div id="global-chatbot-btn"' not in html:
    html = html.replace('</main>', chatbot_ui + '\n  </main>')

with open(FILE, "w", encoding="utf-8") as f:
    f.write(html)

print("Injected global chatbot into index.html")
