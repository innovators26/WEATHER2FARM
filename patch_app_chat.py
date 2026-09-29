import re

FILE = r"src\dashboard\static\js\app.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

chat_js = """

/* =====================================================================
   GLOBAL CHATBOT LOGIC
   ===================================================================== */
let chatbotOpen = false;

function initGlobalChatbot() {
    const btn = document.getElementById('global-chatbot-btn');
    const popup = document.getElementById('global-chatbot-popup');
    const closeBtn = document.getElementById('global-chatbot-close');
    const sendBtn = document.getElementById('global-chatbot-send');
    const input = document.getElementById('global-chatbot-input');
    const messages = document.getElementById('global-chatbot-messages');
    const locSpan = document.getElementById('chat-context-loc');

    if (!btn || !popup) return;

    // Toggle Chatbot
    btn.addEventListener('click', () => {
        chatbotOpen = !chatbotOpen;
        popup.style.display = chatbotOpen ? 'flex' : 'none';
        
        // Update context label whenever opened
        if (chatbotOpen) {
            const st = window.__APP_STATE || {};
            const panchayat = (st.panchayat && st.panchayat.gp_name) ? st.panchayat.gp_name : 'None Selected';
            locSpan.innerText = panchayat;
            input.focus();
        }
    });

    closeBtn.addEventListener('click', () => {
        chatbotOpen = false;
        popup.style.display = 'none';
    });

    // Send Message
    const sendMessage = async () => {
        const q = input.value.trim();
        if (!q) return;

        input.value = '';
        
        // Add User Message
        const userMsg = `<div style="background:#E2E8F0; padding:12px; border-radius:8px; font-size:13px; color:var(--text-main); border-bottom-right-radius:0; max-width:85%; align-self:flex-end; line-height:1.4;">${q}</div>`;
        messages.innerHTML += userMsg;
        messages.scrollTop = messages.scrollHeight;

        // Add Thinking...
        const aiContainerId = 'chat-ai-' + Date.now();
        const aiMsgTpl = `<div id="${aiContainerId}" style="background:var(--primary-bg); padding:12px; border-radius:8px; font-size:13px; color:var(--text-main); border-bottom-left-radius:0; max-width:85%; line-height:1.4;"><em>Thinking...</em></div>`;
        messages.innerHTML += aiMsgTpl;
        messages.scrollTop = messages.scrollHeight;

        try {
            const st = window.__APP_STATE || {};
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

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });
}
"""

if 'initGlobalChatbot' not in code:
    code += chat_js
    # We must also call initGlobalChatbot() on DOMContentLoaded
    init_call = "  initGlobalChatbot();\n});"
    code = code.replace("});\n\n\n\nexport function updateTimestamp()", init_call + "\n\n\n\nexport function updateTimestamp()")
    
with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Injected global chatbot logic into app.js")
