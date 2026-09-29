import { translateDOM, getLang, setLang, t } from './i18n.js';
/**
 * Weather2Farm - Main Application Entry Point
 * Manages routing, state, dropdowns, and tab rendering.
 */

import { state, updateState, loadState, subscribe } from './state.js';
window.__state_cache = state;
subscribe(s => window.__state_cache = s);
import { fetchHierarchy } from './api.js';

import { render as renderDashboard }   from './tabs/dashboard.js';
import { render as renderMap }         from './tabs/map.js';
import { render as renderDownscaling } from './tabs/downscaling.js';
import { render as renderAdvisory }    from './tabs/advisory.js';
import { render as renderValidation }  from './tabs/validation.js';
import { render as renderRisk }        from './tabs/risk.js';
import { render as renderFeedback }    from './tabs/feedback.js';

const RENDERERS = {
  'dashboard':   renderDashboard,
  'map':         renderMap,
  'downscaling': renderDownscaling,
  'advisory':    renderAdvisory,
  'validation':  renderValidation,
  'risk':        renderRisk,
  'feedback':    renderFeedback
};

let hierarchyData = {};

// ── Safe render wrapper ───────────────────────────────────────────────────────
async function safeRender(fn, s) {
  try {
    await fn(s);
  } catch (err) {
    console.error('[AgroScale] Render error:', err);
  }
}

// ── Routing ───────────────────────────────────────────────────────────────────
function getActiveTab() {
  const raw = window.location.hash.replace('#', '').trim();
  return RENDERERS[raw] ? raw : 'dashboard';
}

function showTab(tabName) {
  document.querySelectorAll('.tab-link').forEach(link => {
    link.classList.toggle('active', link.getAttribute('data-tab') === tabName);
  });
  document.querySelectorAll('.tab-section').forEach(sec => {
    sec.style.display = 'none';
  });
  const sec = document.getElementById(tabName + '-tab');
  if (sec) sec.style.display = 'block';
}

function handleRoute() {
  const tab = getActiveTab();
  showTab(tab);
  const renderer = RENDERERS[tab];
  if (renderer) safeRender(renderer, state);
}

// ── Dropdowns ─────────────────────────────────────────────────────────────────
function populateDropdowns() {
  const distSelect  = document.getElementById('districtSelect');
  const blockSelect = document.getElementById('blockSelect');
  const panSelect   = document.getElementById('panchayatSelect');

  // Populate District Select dynamically from hierarchyData
  const currentDist = state.district;
  distSelect.innerHTML = `<option value="">-- ${t('loc.select_district') || 'Select District'} --</option>`;
  Object.keys(hierarchyData).sort().forEach(d => {
    const opt = document.createElement('option');
    opt.value = d;
    opt.textContent = d;
    distSelect.appendChild(opt);
  });
  if (currentDist && hierarchyData[currentDist]) {
    distSelect.value = currentDist;
  } else {
    distSelect.value = "";
  }

  // Populate Block Select
  blockSelect.innerHTML = `<option value="">-- ${t('loc.select_block') || 'Select Block'} --</option>`;
  const district = distSelect.value;
  if (district && hierarchyData[district]) {
    blockSelect.disabled = false;
    Object.keys(hierarchyData[district]).sort().forEach(b => {
      const opt = document.createElement('option');
      opt.value = b;
      opt.textContent = b;
      blockSelect.appendChild(opt);
    });
    if (state.block && hierarchyData[district][state.block]) {
      blockSelect.value = state.block;
    }
  } else {
    blockSelect.disabled = true;
  }

  // Populate Panchayat Select
  panSelect.innerHTML = `<option value="">-- ${t('loc.select_panchayat') || 'Select Panchayat'} --</option>`;
  const block = blockSelect.value;
  if (district && block && hierarchyData[district] && hierarchyData[district][block]) {
    panSelect.disabled = false;
    hierarchyData[district][block].sort((a,b) => a.gp_name.localeCompare(b.gp_name)).forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.gp_code;
      opt.textContent = p.gp_name;
      panSelect.appendChild(opt);
    });
    if (state.panchayat && state.panchayat.gp_code) {
      panSelect.value = state.panchayat.gp_code;
    }
  } else {
    panSelect.disabled = true;
  }
}

function onMapSelectPanchayat(e) {
  const { gp_code, gp_name, block_name } = e.detail;
  updateState({ block: block_name, panchayat: { gp_code, gp_name } });
  populateDropdowns();
}

async function initApp() {
  loadState();

  if (!state.district) {
    updateState({ district: 'Pune' });
  }

  // 1. Render immediately — don't block on API
  handleRoute();

  // 2. Hash navigation
  window.addEventListener('hashchange', handleRoute);
  window.addEventListener('languageChanged', handleRoute);

  // 3. Listen for panchayat selection from the map (map click → global state)
  window.addEventListener('agroscale:select-panchayat', onMapSelectPanchayat);

  // 4. Tab nav clicks
  document.querySelectorAll('.tab-link').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const tab = e.currentTarget.getAttribute('data-tab');
      if (tab) window.location.hash = tab;
    });
  });

  // 5. Load hierarchy in background
  try {
    const { ok, data } = await fetchHierarchy();
    if (ok && data) hierarchyData = data;
  } catch (err) {
    console.warn('[AgroScale] Hierarchy fetch failed:', err);
  }
  populateDropdowns();

  // 6. Selector events
  document.getElementById('districtSelect').addEventListener('change', e => {
    updateState({ district: e.target.value, block: null, panchayat: null });
    populateDropdowns();
    handleRoute();
  });

  document.getElementById('blockSelect').addEventListener('change', e => {
    updateState({ block: e.target.value, panchayat: null });
    populateDropdowns();
    handleRoute();
  });

  document.getElementById('panchayatSelect').addEventListener('change', e => {
    const gp_code = e.target.value;
    if (!gp_code) {
      updateState({ panchayat: null });
      handleRoute();
      return;
    }
    const name = e.target.options[e.target.selectedIndex].text;
    updateState({ panchayat: { gp_code, gp_name: name } });
    handleRoute(); // re-renders active tab (including map)
  });

  // 7. Default hash
  if (!window.location.hash) window.location.hash = 'dashboard';
}


document.addEventListener('DOMContentLoaded', () => {
  const lang = getLang();
  const select = document.getElementById('langSelect');
  if (select) select.value = lang;
  translateDOM();
  updateTimestamp();
  initApp();
  initGlobalChatbot();
});



export function updateTimestamp() {
  const el = document.getElementById('lastUpdated');
  if (!el) return;
  const lang = getLang();
  const dtf = new Intl.DateTimeFormat(lang === 'hi' ? 'hi-IN' : lang === 'mr' ? 'mr-IN' : 'en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Kolkata'
  });
  el.innerText = `${t('status.last_updated')} ${dtf.format(new Date())}`;
}

window.addEventListener('languageChanged', () => {
    updateTimestamp();
});



/* GLOBAL CHATBOT STATE */
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
            aiSpan.innerHTML = data.answer.replace(/\n/g, '<br>');
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
