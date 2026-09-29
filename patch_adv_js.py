import os
import re

FILE = r"src\dashboard\static\js\tabs\advisory.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Replace the advAsk listener with the new one
start_str = "document.getElementById('advAsk').addEventListener('click', () => {"
start_idx = code.find(start_str)

if start_idx != -1:
    end_idx = code.find("  });\n\n  // Return public interface", start_idx)
    if end_idx == -1:
        end_idx = code.find("  });\n}", start_idx)

    if end_idx != -1:
        new_listener = """document.getElementById('advAsk').addEventListener('click', async () => {
    const qInput = document.getElementById('advQuestion');
    const q = qInput.value.trim();
    if (!q) return;
    
    const askBtn = document.getElementById('advAsk');
    const answerEl = document.getElementById('advAnswer');
    
    // UI update
    askBtn.disabled = true;
    askBtn.innerHTML = '<i class="ph-fill ph-spinner ph-spin"></i>';
    answerEl.style.display = 'block';
    
    // Add User message to chat history UI (append or replace? instructions: Display messages as USER message WEATHER2FARM AI response, Maintain readable spacing)
    // We'll just show the latest Q and A to avoid it being excessively large, or a short list.
    // Let's append to the innerHTML.
    const userMsg = `<div style="margin-bottom:8px"><strong>USER</strong><br>${q}</div>`;
    const aiContainerId = 'ai-resp-' + Date.now();
    const aiMsgTpl = `<div style="margin-bottom:12px"><strong>WEATHER2FARM AI</strong><br><span id="${aiContainerId}"><em>Thinking...</em></span></div>`;
    
    if (!answerEl.innerHTML.includes('WEATHER2FARM AI')) {
        answerEl.innerHTML = '';
    }
    answerEl.innerHTML += userMsg + aiMsgTpl;
    answerEl.scrollTop = answerEl.scrollHeight;
    
    qInput.value = '';

    const payload = {
        message: q,
        panchayat_id: state.panchayat || "unknown",
        crop: document.getElementById('advCropSelect').value || "Onion",
        sowing_date: document.getElementById('advSowingDate').value || new Date().toISOString().split('T')[0],
        language: state.lang || "en"
    };

    try {
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
        document.getElementById(aiContainerId).innerHTML = `<span style="color:var(--danger)">Network failure. Please try again.</span>`;
    } finally {
        askBtn.disabled = false;
        askBtn.innerText = t('adv.ask_btn') || 'Ask';
        answerEl.scrollTop = answerEl.scrollHeight;
    }
"""
        code = code[:start_idx] + new_listener + code[end_idx:]
        with open(FILE, "w", encoding="utf-8") as f:
            f.write(code)
        print("Replaced advAsk listener.")
    else:
        print("Could not find end of advAsk listener.")
else:
    print("Could not find advAsk listener start.")

# Add Enter key listener to advQuestion
enter_listener = """
  document.getElementById('advQuestion').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      document.getElementById('advAsk').click();
    }
  });
"""
if "e.key === 'Enter'" not in code:
    with open(FILE, "r", encoding="utf-8") as f:
        code = f.read()
    start_str = "document.getElementById('advAsk').addEventListener"
    start_idx = code.find(start_str)
    if start_idx != -1:
        code = code[:start_idx] + enter_listener + code[start_idx:]
        with open(FILE, "w", encoding="utf-8") as f:
            f.write(code)
        print("Added Enter key listener.")
