import { t } from '../i18n.js';
import { updateState } from '../state.js';
/**
 * Crop Advisory Tab
 * Uses existing Python rule_engine.py via POST /api/advisory
 */

export async function render(state) {
  const container = document.getElementById('advisory-tab');
  const gp_code  = state.panchayat ? state.panchayat.gp_code : '2731002008';
  const gp_name  = state.panchayat ? state.panchayat.gp_name : 'Tamhini';

  const today = new Date();
  const defaultSow = new Date(today);
  defaultSow.setDate(today.getDate() - 30);
  const defaultSowStr = state.sowingDate || defaultSow.toISOString().split('T')[0];
  const initialCrop = state.crop || 'Onion';

  container.innerHTML = `
    
    <div style="display:flex;align-items:baseline;gap:16px;margin-bottom:24px;">
      <h1 style="font-size:32px;font-weight:700;color:var(--primary);" data-i18n="adv.title">Crop Advisory</h1>
      <span style="color:var(--text-muted);font-size:16px;" data-i18n="adv.subtitle">Powered by the existing rule-based advisory engine</span>
    </div>

    <div class="dash-layout-vertical" style="display:flex; flex-direction:column; gap:24px;">
      <!-- LEFT: Inputs -->
      <!-- Top Params Block --><div>
        <div class="card">
          <div class="card-title" style="margin-bottom:20px;">
            <i class="ph-fill ph-sliders"></i> <span data-i18n="adv.params">Advisory Parameters</span>
          </div>
          <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:16px; align-items:end;">

            <div>
              <label style="font-size:13px;font-weight:600;display:block;margin-bottom:6px;" data-i18n="loc.panchayat">Panchayat</label>
              <input type="text" value="${gp_name}" readonly
                style="width:100%;height:40px;border-radius:6px;border:1px solid var(--border);
                       padding:0 12px;background:var(--bg-main);color:var(--text-muted);font-size:14px;">
            </div>

            <div>
              <label style="font-size:13px;font-weight:600;display:block;margin-bottom:6px;" data-i18n="adv.crop">Crop</label>
              <select id="advCrop" data-value="${initialCrop}" style="width:100%;height:40px;border-radius:6px;border:1px solid #CBD5E1;padding:0 12px;font-size:14px;box-sizing:border-box;">
                <option value="Onion" data-i18n="crop_onion">Onion</option>
                <option value="Rice" data-i18n="crop_rice">Rice</option>
                <option value="Wheat" data-i18n="crop_wheat">Wheat</option>
                <option value="Maize" data-i18n="crop_maize">Maize</option>
                <option value="Cotton" data-i18n="crop_cotton">Cotton</option>
                <option value="Sugarcane" data-i18n="crop_sugarcane">Sugarcane</option>
                <option value="Tomato" data-i18n="crop_tomato">Tomato</option>
              </select>
            </div>

            <div>
              <label style="font-size:13px;font-weight:600;display:block;margin-bottom:6px;" data-i18n="adv.sowing">Sowing Date</label>
              <input type="date" id="advDate" value="${defaultSowStr}"
                style="width:100%;height:40px;border-radius:6px;border:1px solid #CBD5E1;padding:0 12px;font-size:14px;box-sizing:border-box;">
            </div>

            <div style="background:var(--bg-main);padding:14px;border-radius:6px;border:1px solid var(--border);">
              <div style="display:flex;justify-content:space-between;">
                <div>
                  <div style="font-size:12px;color:var(--text-muted);" data-i18n="adv.das">Days After Sowing</div>
                  <div id="advDas" style="font-size:18px;font-weight:700;">30</div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:12px;color:var(--text-muted);" data-i18n="adv.calc_stage">Calculated Stage</div>
                  <div id="advStage" style="font-size:14px;font-weight:700;color:var(--primary);" data-i18n="stage_vegetative">Vegetative Growth</div>
                </div>
              </div>
            </div>

            <button id="genAdvBtn" class="btn-primary" style="width:100%;justify-content:center;height:40px;font-size:15px;">
              <i class="ph-fill ph-lightning"></i> <span data-i18n="adv.gen">Generate Advisory</span>
            </button>
            <div id="advErrorMsg" style="display:none; color:var(--danger); font-size:13px; margin-top:8px; text-align:center;"></div>
          </div>
        </div>

        

      <!-- RIGHT: Result -->
      <!-- Result Block --><div>
        <div class="card" id="advResultCard" style="display:none;height:100%;min-height:400px;flex-direction:column;">
          <div class="card-title" style="margin-bottom:20px;">
            <i class="ph-fill ph-file-text"></i> Advisory Result
          </div>

          

          <div id="advResult" style="display:flex;flex-direction:column;gap:24px;">

            <div style="display:flex;flex-direction:column;gap:8px;background:var(--bg-main);border:1px solid var(--border);padding:16px;border-radius:6px;">
              <div style="display:flex;align-items:center;gap:12px;">
                <i id="advStatusIcon" class="ph-fill ph-warning" style="font-size:36px;color:var(--warning);"></i>
                <div>
                  <div style="font-size:12px;color:var(--text-muted);">Alert Level</div>
                  <div id="advStatusText" style="font-size:22px;font-weight:700;">Normal</div>
                </div>
              </div>
              <div id="advStatusReason" style="font-size:14px;color:var(--text-main);margin-top:4px;"></div>
            </div>

            <div style="background:var(--primary-bg); border-left:4px solid var(--primary); padding:16px; border-radius:6px;">
              <h3 style="font-size:16px;font-weight:700;margin-bottom:8px;color:var(--text-main);" data-i18n="adv.res_condition">Current Crop Condition</h3>
              <div id="advResCropCondition" style="font-size:14px;color:var(--text-main);line-height:1.5;">--</div>
            </div>

            <div style="background:var(--bg-main); border:1px solid var(--border); padding:16px; border-radius:6px;">
              <h3 style="font-size:16px;font-weight:700;margin-bottom:12px;color:var(--text-main);" data-i18n="adv.res_impact">Weather Condition & Impact</h3>
              <div style="display:flex;gap:12px;margin-bottom:12px;">
                <div style="flex:1;background:var(--primary-bg);padding:10px;border-radius:6px;text-align:center;">
                  <div style="color:var(--text-muted);font-size:12px;" data-i18n="dash.rain">Rainfall</div>
                  <div id="advResRain" style="font-size:16px;font-weight:700;color:var(--text-main);">--</div>
                </div>
                <div style="flex:1;background:#FEF3E7;padding:10px;border-radius:6px;text-align:center;">
                  <div style="color:var(--text-muted);font-size:12px;" data-i18n="dash.temp">Temp</div>
                  <div id="advResTemp" style="font-size:16px;font-weight:700;color:#D64545;">--</div>
                </div>
                <div style="flex:1;background:var(--primary-bg);padding:10px;border-radius:6px;text-align:center;">
                  <div style="color:var(--text-muted);font-size:12px;" data-i18n="dash.hum">Humidity</div>
                  <div id="advResHum" style="font-size:16px;font-weight:700;color:var(--text-main);">--</div>
                </div>
                <div style="flex:1;background:var(--bg-main);border:1px solid var(--border);padding:10px;border-radius:6px;text-align:center;">
                  <div style="color:var(--text-muted);font-size:12px;" data-i18n="dash.wind">Wind</div>
                  <div id="advResWind" style="font-size:16px;font-weight:700;color:var(--text-main);">--</div>
                </div>
              </div>
              <div id="advResWeatherImpact" style="font-size:14px;color:var(--text-main);line-height:1.5;">--</div>
            </div>

            <div>
              <h3 style="font-size:16px;font-weight:700;margin-bottom:8px;color:var(--text-main);" data-i18n="adv.res_trend">Weather Trend (7-Day Forecast)</h3>
              <div id="advResTrend" style="font-size:14px;color:var(--text-muted);line-height:1.5;background:var(--bg-main);padding:12px;border-radius:6px;">--</div>
            </div>

            <div id="advResRisksContainer">
              <h3 style="font-size:16px;font-weight:700;margin-bottom:8px;color:var(--text-main);" data-i18n="adv.res_risk">Crop Risk</h3>
              <div id="advResRisks" style="display:flex;flex-direction:column;gap:12px;"></div>
            </div>

            <div>
              <h3 style="font-size:16px;font-weight:700;margin-bottom:12px;color:var(--text-main);" data-i18n="adv.res_actions">Recommended Actions</h3>
              <div id="advResActions" style="display:flex;flex-direction:column;gap:12px;"></div>
            </div>

            <div id="advResAvoidContainer" style="background:#FFF3F3; border-left:4px solid var(--danger); padding:16px; border-radius:6px;">
              <h3 style="font-size:16px;font-weight:700;margin-bottom:8px;color:var(--danger);" data-i18n="adv.res_avoid">Avoid</h3>
              <ul id="advResAvoid" style="margin:0;padding-left:20px;font-size:14px;color:var(--danger);line-height:1.5;"></ul>
            </div>

            <div style="background:var(--primary-bg); padding:16px; border-radius:6px;">
              <h3 style="font-size:16px;font-weight:700;margin-bottom:8px;color:var(--primary);" data-i18n="adv.res_next7">Next 3–7 Days</h3>
              <div id="advResNext7" style="font-size:14px;color:var(--text-main);line-height:1.5;">--</div>
            </div>
          </div>
 


      </div>       </div>
      </div>
    </div>

  `;




  let latestAdvisory = null;
  // Compute DAS and Stage on date change

  const renderResult = () => {
      if (!latestAdvisory) return;
      const d = latestAdvisory;
      const p = d.advanced ? (d.advanced.params || {}) : {};

      const sev = (d.severity || 'NORMAL').toUpperCase();
      const sevMap = { "NORMAL": "NORMAL", "WATCH": "WATCH", "WARNING": "WARNING", "SEVERE": "SEVERE", "CRITICAL": "CRITICAL", "HIGH": "HIGH", "MODERATE": "MODERATE", "LOW": "LOW" };
      
      document.getElementById('advStatusText').innerText = t(sevMap[sev] || sev);
      
      const icon = document.getElementById('advStatusIcon');
      if (sev === 'SEVERE') {
        icon.className = 'ph-fill ph-warning-circle';
        icon.style.color = 'var(--danger)';
      } else if (sev === 'WARNING') {
        icon.className = 'ph-fill ph-warning';
        icon.style.color = '#E57373';
      } else if (sev === 'WATCH') {
        icon.className = 'ph-fill ph-info';
        icon.style.color = 'var(--warning)';
      } else {
        icon.className = 'ph-fill ph-check-circle';
        icon.style.color = 'var(--success)';
      }

      if (d.advanced && d.advanced.alert_reason) {
         document.getElementById('advStatusReason').innerHTML = `<strong>${t('adv.res_why')}:</strong> ${t(d.advanced.alert_reason, p)}`;
      } else {
         document.getElementById('advStatusReason').innerHTML = '';
      }

      const w = d.weather || {};
      document.getElementById('advResRain').innerText  = (w.rain  ?? '--');
      document.getElementById('advResTemp').innerText  = (w.temp  ?? '--');
      document.getElementById('advResHum').innerText   = (w.humidity ?? '--');
      document.getElementById('advResWind').innerText  = (w.wind  ?? '--');

      if (d.advanced) {
        document.getElementById('advResCropCondition').innerText = t(d.advanced.crop_condition, p);
        document.getElementById('advResWeatherImpact').innerText = t(d.advanced.weather_impact, p);
        document.getElementById('advResTrend').innerText = t(d.advanced.trend_summary, p);
        
        const riskBox = document.getElementById('advResRisks');
        riskBox.innerHTML = '';
        if (d.advanced.risks && d.advanced.risks.length > 0) {
           d.advanced.risks.forEach(r => {
             const col = r.level === 'HIGH' || r.level === 'CRITICAL' || r.level === 'SEVERE' ? 'var(--danger)' : 'var(--warning)';
             riskBox.innerHTML += `
               <div style="background:var(--bg-main);border:1px solid var(--border);padding:12px;border-radius:6px;">
                 <div style="font-size:14px;font-weight:700;color:${col};margin-bottom:4px;">${t(r.risk_name, p)} — ${t(r.level)}</div>
                 <div style="font-size:13px;color:var(--text-muted);line-height:1.4;"><strong>${t('adv.res_why')}:</strong> ${t(r.reason, p)}</div>
               </div>
             `;
           });
           document.getElementById('advResRisksContainer').style.display = 'block';
        } else {
           riskBox.innerHTML = `<div style="font-size:14px;color:var(--text-muted);">${t('common.nodata')}</div>`;
        }

        const actBox = document.getElementById('advResActions');
        actBox.innerHTML = '';
        if (d.advanced.actions && d.advanced.actions.length > 0) {
           d.advanced.actions.forEach((a, idx) => {
             actBox.innerHTML += `
               <div style="background:var(--bg-main);border:1px solid var(--border);padding:14px;border-radius:6px;">
                 <div style="font-size:14px;font-weight:700;margin-bottom:6px;color:var(--text-main);">${idx + 1}. ${t(a.action, p)}</div>
                 <div style="font-size:13px;color:var(--text-muted);margin-bottom:4px;line-height:1.4;"><strong>${t('adv.res_why')}:</strong> ${t(a.why, p)}</div>
                 <div style="font-size:13px;color:var(--text-muted);line-height:1.4;"><strong>${t('adv.res_when')}:</strong> <span style="font-weight:600;color:var(--primary);">${t(a.when, p)}</span></div>
               </div>
             `;
           });
        } else {
           actBox.innerHTML = `<div style="font-size:14px;color:var(--text-muted);">${t('common.nodata')}</div>`;
        }

        const avoidList = document.getElementById('advResAvoid');
        avoidList.innerHTML = '';
        if (d.advanced.avoid && d.advanced.avoid.length > 0) {
           d.advanced.avoid.forEach(av => {
             avoidList.innerHTML += `<li>${t(av, p)}</li>`;
           });
           document.getElementById('advResAvoidContainer').style.display = 'block';
        } else {
           document.getElementById('advResAvoidContainer').style.display = 'none';
        }

        document.getElementById('advResNext7').innerText = t(d.advanced.next_7_days, p);
      }
  };

  if (window._advLangHandler) window.removeEventListener('languageChanged', window._advLangHandler);
  window._advLangHandler = renderResult;
  window.addEventListener('languageChanged', window._advLangHandler);


  function computeDAS() {
    const dateVal = document.getElementById('advDate').value;
    if (!dateVal) return;
    const sow = new Date(dateVal);
    const das = Math.max(0, Math.floor((Date.now() - sow.getTime()) / 86400000));
    document.getElementById('advDas').innerText = das;
    let stage = 'Sowing';
    if (das > 14) stage = 'Vegetative';
    if (das > 45) stage = 'Flowering';
    if (das > 75) stage = 'Grain Filling';
    if (das > 100) stage = 'Maturity';
    if (das > 120) stage = 'Harvesting';
    document.getElementById('advStage').innerText = stage;
  }
    document.getElementById('advCrop').value = initialCrop;

  document.getElementById('advCrop').addEventListener('change', e => {
      updateState({ crop: e.target.value });
    const resCard = document.getElementById('advResultCard');
    
    if (resCard) resCard.style.display = 'none';
    

  });

  document.getElementById('advDate').addEventListener('change', e => {
      updateState({ sowingDate: e.target.value });
    const resCard = document.getElementById('advResultCard');
    
    if (resCard) resCard.style.display = 'none';
    

      computeDAS();
  });

  computeDAS();

  // Generate advisory
  document.getElementById('genAdvBtn').addEventListener('click', async () => {
    const btn = document.getElementById('genAdvBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> Generating...';
    
    // Hide previous result
    document.getElementById('advResultCard').style.display = 'none';
    
    const errMsg = document.getElementById('advErrorMsg');
    if (errMsg) errMsg.style.display = 'none';


    try {
      const res = await fetch('/api/advisory', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          gp_code,
          gp_name,
          crop: document.getElementById('advCrop').value,
          sowing_date: document.getElementById('advDate').value
        })
      });
      
      const d = await res.json();
      latestAdvisory = d;





      
      document.getElementById('advResultCard').style.display = 'flex';
      
      renderResult();

      if (d.rules_applied && d.rules_applied.length) {
        document.getElementById('advRulesArea').style.display = 'block';
        document.getElementById('advRulesList').innerText = d.rules_applied.join(', ');
      }
    } catch (e) {
      const errMsg = document.getElementById('advErrorMsg');
      if (errMsg) {
        errMsg.innerText = 'Generation failed: ' + e.message;
        errMsg.style.display = 'block';
      }
    }

    btn.disabled = false;
    btn.innerHTML = '<i class="ph-fill ph-lightning"></i> Generate Advisory';
  });

  }
