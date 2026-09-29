import os

FILE = r"src\dashboard\static\js\tabs\advisory.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

start_str = "document.getElementById('advAsk').addEventListener('click', async () => {"
start_idx = code.find(start_str)

end_str = "        answerEl.scrollTop = answerEl.scrollHeight;\n    }\n});"
end_idx = code.find(end_str, start_idx) + len(end_str)

new_listener = """document.getElementById('advAsk').addEventListener('click', async () => {
    const qInput = document.getElementById('advQuestion');
    const q = qInput.value.trim();
    if (!q) return;
    
    const askBtn = document.getElementById('advAsk');
    const answerEl = document.getElementById('advAnswer');
    
    askBtn.disabled = true;
    askBtn.innerHTML = '<i class="ph-fill ph-spinner ph-spin"></i>';
    answerEl.style.display = 'block';
    
    const userMsg = `<div style="margin-bottom:8px"><strong>USER</strong><br>${q}</div>`;
    const aiContainerId = 'ai-resp-' + Date.now();
    const aiMsgTpl = `<div style="margin-bottom:12px"><strong>WEATHER2FARM AI</strong><br><span id="${aiContainerId}"><em>Thinking...</em></span></div>`;
    
    if (!answerEl.innerHTML.includes('WEATHER2FARM AI')) {
        answerEl.innerHTML = '';
    }
    answerEl.innerHTML += userMsg + aiMsgTpl;
    answerEl.scrollTop = answerEl.scrollHeight;
    
    qInput.value = '';

    try {
        const cropEl = document.getElementById('advCrop');
        const dateEl = document.getElementById('advDate');
        const payload = {
            message: q,
            panchayat_id: (state.panchayat && state.panchayat.gp_code) ? state.panchayat.gp_code : "2731002008",
            crop: cropEl ? cropEl.value : "Onion",
            sowing_date: dateEl ? dateEl.value : new Date().toISOString().split('T')[0],
            language: state.lang || "en"
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
        document.getElementById(aiContainerId).innerHTML = `<span style="color:var(--danger)">Unable to get a response right now. Please try again.</span>`;
        console.error("Chat Error:", e);
    } finally {
        askBtn.disabled = false;
        const btnText = (typeof t === 'function' ? t('adv.ask_btn') : '') || 'Ask';
        askBtn.innerText = btnText;
        answerEl.scrollTop = answerEl.scrollHeight;
    }
});"""

code = code[:start_idx] + new_listener + code[end_idx:]

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Patched advisory.js")
