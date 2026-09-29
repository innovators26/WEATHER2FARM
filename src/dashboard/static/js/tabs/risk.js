import { t } from '../i18n.js';

/**
 * Crop Risk Tab
 * Professional agricultural risk intelligence dashboard.
 */

export async function render(state) {

  const container = document.getElementById('risk-tab');
  
  if (!state.panchayat) {
    container.innerHTML = `
    <div style="max-width: 1450px; width: calc(100% - 48px); margin: 0 auto; display:flex; flex-direction:column; gap:20px;">
      
      <!-- HEADER -->
      <div style="display:flex; flex-direction:column; gap:4px; border-bottom:1px solid #DDE6ED; padding-bottom:16px;">
        <h1 style="font-size:32px; font-weight:700; color:#064B70; margin:0;">${t('risk.page_title').toUpperCase()}</h1>
        <div style="font-size:16px; color:#64748B;">${t('risk.subtitle')}</div>
        
        <div style="margin-top:12px; display:flex; justify-content:space-between; align-items:flex-end;">
          <div>
            <div style="font-size:24px; font-weight:700; color:#17324D;"></div>
            <div style="font-size:14px; color:#64748B;"></div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:12px; color:#64748B;">${t('risk.last_eval')}: </div>
          </div>
        </div>
      </div>

      <!-- TWO-COLUMN MAIN GRID -->
      <!-- Omitted for empty state since it's not fully rendered anyway, but let's keep it minimal -->
      <div style="padding: 40px; text-align: center; color: var(--text-muted);">
        <div>Please select a Panchayat</div>
      </div>
    </div>
  `;
    return;
  }

  const gp_code = state.panchayat.gp_code;
  const gp_name  = state.panchayat.gp_name;
  const block_name = state.block || "Selected Block";

  // Loading state
  container.innerHTML = `
    <div style="display:flex;align-items:baseline;gap:16px;margin-bottom:24px;">
      <h1 style="font-size:32px;font-weight:700;color:var(--primary);">${t('risk.page_title')}</h1>
      <span style="color:var(--text-muted);font-size:16px;">${t('risk.subtitle')}</span>
    </div>
    <div style="padding: 40px; text-align: center; color: var(--text-muted);">
      <i class="ph-fill ph-spinner ph-spin" style="font-size: 32px; margin-bottom: 12px;"></i>
      <div>${t('risk.loading_intel')} ${gp_name}...</div>
    </div>
  `;

  // Fetch real data from backend
  const payload = {
    gp_code: gp_code,
    gp_name: gp_name,
    crop: state.crop || "Onion",
    sowing_date: state.sowingDate || new Date().toISOString().split('T')[0]
  };

  let riskData = null;
  try {
    const res = await fetch('/api/advisory', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      riskData = await res.json();
    }
  } catch (err) {
    console.error("Failed to load risk data:", err);
  }

  if (!riskData || !riskData.advanced) {
    container.innerHTML = `
      <div style="display:flex;align-items:baseline;gap:16px;margin-bottom:24px;">
        <h1 style="font-size:32px;font-weight:700;color:var(--primary);">${t('risk.page_title')}</h1>
        <span style="color:var(--text-muted);font-size:16px;">${t('risk.subtitle')}</span>
      </div>
      <div style="padding:40px;text-align:center;color:var(--danger);background:#fff0f0;border-radius:8px;">
        <h3 style="margin-bottom:8px; text-transform: uppercase;">${t('risk.unavailable')}</h3>
        <p>${t('risk.unavailable_desc')}</p>
      </div>
    `;
    return;
  }

  const adv = riskData.advanced;
  const weather = riskData.weather || {};
  const risks = adv.risks || [];
  const actions = adv.actions || [];
  
  const p = adv.params || {};

  // Calculate summary counts
  let highCount = 0;
  let modCount = 0;
  let lowCount = 0;
  
  risks.forEach(r => {
    const s = (r.level || '').toUpperCase();
    if (s === 'HIGH' || s === 'SEVERE' || s === 'CRITICAL') highCount++;
    else if (s === 'MODERATE' || s === 'WARNING' || s === 'WATCH') modCount++;
    else lowCount++;
  });

  const overall = adv.overall_severity || 'NORMAL';
  let overallColor = '#4F8F3A'; // low/normal
  if (overall.toUpperCase() === 'HIGH' || overall.toUpperCase() === 'SEVERE') overallColor = '#D64545';
  else if (overall.toUpperCase() === 'MODERATE' || overall.toUpperCase() === 'WARNING') overallColor = '#E59A17';

  // Format Risk Cards
  function buildRiskCard(r) {
      const s = (r.level || '').toUpperCase();
      let bg = '#F4F7F9';
      let dot = '#4F8F3A';
      
      if (s === 'HIGH' || s === 'SEVERE' || s === 'CRITICAL') { bg = '#FFF5F5'; dot = '#D64545'; }
      else if (s === 'MODERATE' || s === 'WARNING' || s === 'WATCH') { bg = '#FFFDF5'; dot = '#E59A17'; }
      else { bg = '#F5FFF5'; dot = '#4F8F3A'; }
  
      let trigger = t('risk.rule_met');
      if (r.reason && (r.reason.includes("Exceeds") || r.reason.includes("exceeds"))) {
         trigger = t(r.reason, p);
      }
      
      let actionStr = t('risk.monitor');
      if (adv.avoid && adv.avoid.length > 0 && (s === 'HIGH' || s === 'SEVERE')) {
          actionStr = t('risk.avoid') + " " + adv.avoid.map(a => t(a, p)).join(', ');
      } else if (actions.length > 0) {
          actionStr = t(actions[0].action, p);
      }
  
      return `
        <div style="background:${bg}; border:1px solid #DDE6ED; border-radius:8px; display:flex; flex-direction:column; overflow:hidden; width:100%; box-sizing:border-box;">
          <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #DDE6ED; padding:16px 20px; background:${bg};">
            <h3 style="margin:0; font-size:16px; font-weight:700; color:#17324D; text-transform:uppercase;">${t(r.risk_name, p)}</h3>
            <div style="display:flex; align-items:center; gap:6px; background:#fff; padding:4px 10px; border-radius:12px; border:1px solid #DDE6ED;">
              <div style="width:10px; height:10px; border-radius:50%; background:${dot};"></div>
              <span style="font-size:12px; font-weight:700; color:#17324D; text-transform:uppercase;">${t(r.level, p)}</span>
            </div>
          </div>
          
          <div class="active-risk-card-inner" style="display:grid; grid-template-columns: 1.5fr 1.5fr 1fr; gap:24px; padding:20px; background:#fff;">
            <div>
              <div style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase; margin-bottom:6px;">${t('risk.assessment')}</div>
              <div style="font-size:14px; color:#17324D; line-height:1.5;">${t(r.reason, p)}</div>
            </div>
            
            <div>
              <div style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase; margin-bottom:6px;">${t('risk.rec_action')}</div>
              <div style="font-size:14px; color:#17324D; line-height:1.5;">${actionStr}</div>
            </div>
            
            <div>
              <div style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase; margin-bottom:6px;">${t('risk.trigger')}</div>
              <div style="font-size:13px; color:#64748B; line-height:1.5;">${trigger}</div>
            </div>
          </div>
        </div>
      `;
    }

  let risksHtml = '';
  if (risks.length === 0) {
    risksHtml = `
      <div style="grid-column: 1 / -1; padding:40px; text-align:center; background:#F5FFF5; border:1px solid #DDE6ED; border-radius:8px;">
        <h3 style="margin-bottom:8px; color:#17324D; text-transform: uppercase;">${t('risk.no_active')}</h3>
        <p style="color:#64748B;">${t('risk.no_active_desc')}</p>
      </div>
    `;
  } else {
    risksHtml = risks.map(buildRiskCard).join('');
  }
  
  let actionsHtml = '';
  if (actions.length > 0) {
      actionsHtml = actions.map((a, idx) => `
        <div style="display:flex; gap:16px; margin-bottom:${idx === actions.length-1 ? '0' : '16px'};">
            <div style="font-size:16px; font-weight:700; color:#064B70; min-width:24px;">0${idx+1}</div>
            <div>
                <div style="font-size:15px; font-weight:700; color:#17324D; margin-bottom:4px;">${t(a.action, p)}</div>
                <div style="font-size:13px; color:#64748B;">${t(a.why || '', p)} ${a.when ? '• ' + t(a.when, p) : ''}</div>
            </div>
        </div>
      `).join('');
  } else {
      actionsHtml = `<div style="color:#64748B;">${t('risk.no_actions')}</div>`;
  }

  const dateStr = new Date().toLocaleString();

  container.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:24px;">
      
      <!-- HEADER -->
      <div style="display:flex; flex-direction:column; gap:4px; border-bottom:1px solid #DDE6ED; padding-bottom:16px;">
        <h1 style="font-size:32px; font-weight:700; color:#064B70; margin:0; text-transform:uppercase;">${t('risk.page_title')}</h1>
        <div style="font-size:16px; color:#64748B;">${t('risk.subtitle')}</div>
        
        <div style="margin-top:12px; display:flex; justify-content:space-between; align-items:flex-end;">
          <div>
            <div style="font-size:24px; font-weight:700; color:#17324D; text-transform:uppercase;">${gp_name}</div>
            <div style="font-size:14px; color:#64748B;">${block_name} • Pune</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:12px; color:#64748B;">${t('risk.last_eval')}: ${dateStr}</div>
          </div>
        </div>
      </div>

      <div style="font-size:12px; color:#64748B; background:#F4F7F9; padding:8px 12px; border-radius:4px;">
        Risk assessment is generated from Weather2Farm's rule-based agricultural risk engine using current Panchayat weather, forecast conditions, terrain and crop context.
      </div>

      <!-- TODAY'S FARM RISK & OVERVIEW GRID -->
      <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap:24px;">
        
        <div style="background:#fff; border:1px solid #DDE6ED; border-radius:8px; padding:20px;">
          <h2 style="font-size:14px; font-weight:700; color:#64748B; margin-bottom:16px; text-transform:uppercase;">${t('risk.todays_farm_risk')}</h2>
          
          <div style="margin-bottom:16px;">
            <div style="font-size:12px; color:#64748B;">${t('risk.overall')}</div>
            <div style="font-size:24px; font-weight:700; color:${overallColor}; text-transform:uppercase;">${t(overall)}</div>
          </div>
          
          <div style="margin-bottom:16px;">
            <div style="font-size:12px; color:#64748B;">${t('risk.primary_concern')}</div>
            <div style="font-size:16px; font-weight:700; color:#17324D;">${adv.alert_reason ? t(adv.alert_reason, p) : t('risk.none')}</div>
          </div>
          
          <div>
            <div style="font-size:12px; color:#64748B;">${t('risk.priority_action')}</div>
            <div style="font-size:14px; color:#17324D; line-height:1.4;">${actions.length > 0 ? t(actions[0].action, p) : t('risk.continue_monitoring')}</div>
          </div>
        </div>

        <div style="background:#fff; border:1px solid #DDE6ED; border-radius:8px; padding:20px;">
          <h2 style="font-size:14px; font-weight:700; color:#64748B; margin-bottom:16px; text-transform:uppercase;">${t('risk.overview')}</h2>
          
          <div style="display:flex; justify-content:space-between; margin-bottom:16px;">
            <div style="text-align:center;">
              <div style="font-size:28px; font-weight:700; color:#D64545;">${highCount}</div>
              <div style="font-size:12px; font-weight:700; color:#64748B;">HIGH</div>
            </div>
            <div style="text-align:center;">
              <div style="font-size:28px; font-weight:700; color:#E59A17;">${modCount}</div>
              <div style="font-size:12px; font-weight:700; color:#64748B;">MODERATE</div>
            </div>
            <div style="text-align:center;">
              <div style="font-size:28px; font-weight:700; color:#4F8F3A;">${lowCount}</div>
              <div style="font-size:12px; font-weight:700; color:#64748B;">LOW</div>
            </div>
          </div>
          
          <div style="font-size:13px; color:#64748B; line-height:1.5;">
            <div style="margin-bottom:4px;"><strong>High:</strong> ${t('risk.high_desc')}</div>
            <div style="margin-bottom:4px;"><strong>Moderate:</strong> ${t('risk.mod_desc')}</div>
            <div><strong>Low:</strong> ${t('risk.low_desc')}</div>
          </div>
        </div>

      </div>

      <!-- ACTIVE RISK CONDITIONS -->
      <div>
        <h2 style="font-size:18px; font-weight:700; color:#064B70; margin-bottom:16px; border-bottom:2px solid #064B70; padding-bottom:8px; display:inline-block; text-transform:uppercase;">${t('risk.active')}</h2>
        <div style="display:grid; grid-template-columns: ${risks.length === 1 ? '1fr' : 'repeat(auto-fit, minmax(450px, 1fr))'}; gap:20px; width: 100%; box-sizing: border-box;">
          ${risksHtml}
        </div>
      </div>

      <!-- RISK EVIDENCE -->
      <div>
        <h2 style="font-size:18px; font-weight:700; color:#064B70; margin-bottom:16px; border-bottom:2px solid #064B70; padding-bottom:8px; display:inline-block; text-transform:uppercase;">${t('risk.evidence')}</h2>
        <div style="display:flex; flex-wrap:wrap; gap:16px;">
          <div style="background:#F4F7F9; border:1px solid #DDE6ED; padding:16px; border-radius:8px; min-width:140px;">
            <div style="font-size:12px; color:#64748B; margin-bottom:4px;">${t('map.rain')}</div>
            <div style="font-size:20px; font-weight:700; color:#17324D;">${weather.rain || 0} mm</div>
          </div>
          <div style="background:#F4F7F9; border:1px solid #DDE6ED; padding:16px; border-radius:8px; min-width:140px;">
            <div style="font-size:12px; color:#64748B; margin-bottom:4px;">${t('map.tmax')}</div>
            <div style="font-size:20px; font-weight:700; color:#17324D;">${weather.temp || 0} °C</div>
          </div>
          <div style="background:#F4F7F9; border:1px solid #DDE6ED; padding:16px; border-radius:8px; min-width:140px;">
            <div style="font-size:12px; color:#64748B; margin-bottom:4px;">${t('map.rh')}</div>
            <div style="font-size:20px; font-weight:700; color:#17324D;">${weather.humidity || 0} %</div>
          </div>
          <div style="background:#F4F7F9; border:1px solid #DDE6ED; padding:16px; border-radius:8px; min-width:140px;">
            <div style="font-size:12px; color:#64748B; margin-bottom:4px;">${t('map.wind')}</div>
            <div style="font-size:20px; font-weight:700; color:#17324D;">${weather.wind || 0} km/h</div>
          </div>
        </div>
      </div>

      <!-- RECOMMENDED FARM ACTIONS -->
      <div>
        <h2 style="font-size:18px; font-weight:700; color:#064B70; margin-bottom:16px; border-bottom:2px solid #064B70; padding-bottom:8px; display:inline-block; text-transform:uppercase;">${t('risk.farm_actions')}</h2>
        <div style="background:#fff; border:1px solid #DDE6ED; padding:24px; border-radius:8px;">
          ${actionsHtml}
        </div>
      </div>
      
      <!-- CROP CONTEXT -->
      <div>
        <h2 style="font-size:18px; font-weight:700; color:#064B70; margin-bottom:16px; border-bottom:2px solid #064B70; padding-bottom:8px; display:inline-block; text-transform:uppercase;">${t('risk.context')}</h2>
        <div style="display:flex; gap:32px; background:#fff; border:1px solid #DDE6ED; padding:20px; border-radius:8px;">
            <div>
                <div style="font-size:12px; color:#64748B; margin-bottom:4px;">${t('risk.crop')}</div>
                <div style="font-size:16px; font-weight:700; color:#17324D;">${riskData.crop ? t(riskData.crop, p) : t('risk.unknown')}</div>
            </div>
            <div>
                <div style="font-size:12px; color:#64748B; margin-bottom:4px;">${t('risk.growth_stage')}</div>
                <div style="font-size:16px; font-weight:700; color:#17324D;">${t(riskData.stage || 'Unknown', p)}</div>
            </div>
            <div>
                <div style="font-size:12px; color:#64748B; margin-bottom:4px;">${t('risk.das')}</div>
                <div style="font-size:16px; font-weight:700; color:#17324D;">${riskData.days_after_sowing || '0'}</div>
            </div>
        </div>
      </div>

    </div>
  `;
}

// Ensure responsive CSS is injected
if (!document.getElementById('risk-grid-style')) {
    const style = document.createElement('style');
    style.id = 'risk-grid-style';
    style.innerHTML = `
        @media (max-width: 900px) {
            #risk-tab .display\\:grid {
                grid-template-columns: 1fr !important;
            }
        }
    `;
    document.head.appendChild(style);
}

// Ensure responsive CSS is injected
if (!document.getElementById('active-risk-style')) {
    const style = document.createElement('style');
    style.id = 'active-risk-style';
    style.innerHTML = `
        @media (max-width: 900px) {
            #risk-tab .active-risk-card-inner {
                grid-template-columns: 1fr !important;
                gap: 16px !important;
            }
        }
    `;
    document.head.appendChild(style);
}

window.addEventListener('languageChanged', () => {
    import('../state.js').then(module => {
        if (module.state) render(module.state);
    });
});
