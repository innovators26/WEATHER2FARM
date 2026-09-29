import re

FILE = r"src\dashboard\static\js\app.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Make sendMessage globally exposed
send_logic = """
window.sendGlobalChatMessage = async function() {
    const input = document.getElementById('global-chatbot-input');
    const messages = document.getElementById('global-chatbot-messages');
    if (!input || !messages) return;
    
    const q = input.value.trim();
    if (!q) return;

    input.value = '';
    
    const userMsg = `<div style="background:#E2E8F0; padding:12px; border-radius:8px; font-size:13px; color:var(--text-main); border-bottom-right-radius:0; max-width:85%; align-self:flex-end; line-height:1.4;">${q}</div>`;
    messages.innerHTML += userMsg;
    messages.scrollTop = messages.scrollHeight;

    const aiContainerId = 'chat-ai-' + Date.now();
    const aiMsgTpl = `<div id="${aiContainerId}" style="background:var(--primary-bg); padding:12px; border-radius:8px; font-size:13px; color:var(--text-main); border-bottom-left-radius:0; max-width:85%; line-height:1.4;"><em>Thinking...</em></div>`;
    messages.innerHTML += aiMsgTpl;
    messages.scrollTop = messages.scrollHeight;

    try {
        const st = window.__state_cache || {};
        const payload = {
            message: q,
            panchayat_id: (st.panchayat && st.panchayat.gp_code) ? st.panchayat.gp_code : "2731002008",
            crop: st.crop || "Onion",
            sowing_date: st.sowingDate || new Date().toISOString().split('T')[0],
            language: localStorage.getItem('lang') || "en"
        };

        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        const aiSpan = document.getElementById(aiContainerId);
        if (data.success) {
            aiSpan.innerHTML = data.answer.replace(/\\n/g, '<br>');
        } else {
            aiSpan.innerHTML = `<span style="color:var(--danger)">${data.error || 'AI assistant is temporarily unavailable.'}</span>`;
        }
    } catch (e) {
        document.getElementById(aiContainerId).innerHTML = `<span style="color:var(--danger)">Unable to connect to AI right now.</span>`;
        console.error("Chat Error:", e);
    } finally {
        messages.scrollTop = messages.scrollHeight;
    }
};

window.handleGlobalChatKey = function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        window.sendGlobalChatMessage();
    }
};
"""

code += send_logic

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

FILE_HTML = r"src\dashboard\templates\index.html"
with open(FILE_HTML, "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace('id="global-chatbot-send"', 'id="global-chatbot-send" onclick="window.sendGlobalChatMessage()"')
html = html.replace('id="global-chatbot-input"', 'id="global-chatbot-input" onkeypress="window.handleGlobalChatKey(event)"')

with open(FILE_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("Applied foolproof send handlers for global chatbot")
