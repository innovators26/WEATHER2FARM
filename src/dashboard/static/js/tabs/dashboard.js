import { t, getLang } from '../i18n.js';
/**
 * Dashboard Tab
 * Renders weather cards, AI downscaling hero, 7-day forecast,
 * advisory preview, model status, feedback preview, system status, and the mini-map.
 */

let dashMap = null;

async function apiFetch(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.warn('[Dashboard] fetch failed:', url, e.message);
    return null;
  }
}

function weatherIcon(icon) {
  const map = {
    'rain': 'ph-fill ph-cloud-rain',
    'sun': 'ph-fill ph-sun',
    'cloud-sun': 'ph-fill ph-cloud-sun',
    'cloud': 'ph-fill ph-cloud',
  };
  return map[icon] || 'ph-fill ph-cloud-rain';
}

function weatherIconColor(icon) {
  return icon === 'sun' ? 'var(--warning)' : icon === 'cloud-sun' ? '#9BB7D4' : '#4B92D4';
}

export async function render(state) {
  const container = document.getElementById('dashboard-tab');
  
  // Show Loading State immediately
  container.innerHTML = `
    <div style="display:flex; justify-content:center; align-items:center; height:300px; color:var(--text-muted);">
      <i class="ph-bold ph-spinner ph-spin" style="font-size:32px; margin-right:12px;"></i>
      <span>${t('dashboard.loading')}</span>
    </div>
  `;

  
  // If no panchayat selected, show empty state immediately and return
  if (!state.panchayat || !state.panchayat.gp_code) {
    container.innerHTML = `
      <div style="display:flex; align-items:baseline; gap:16px; margin-bottom:24px;">
        <h1 style="font-size:32px; font-weight:700; color:var(--primary);">Dashboard</h1>
      </div>
      <div class="dash-layout">
        <div class="dash-left">
          <div class="card weather-metrics-grid">
            <div class="metric-card"><i class="ph-fill ph-cloud-rain metric-icon" style="color:#4B92D4;"></i><div><div style="font-size:13px;font-weight:600;color:var(--text-main);">${t('map.rain')}</div><div class="metric-val">-- <span style="font-size:16px;">mm</span></div><div style="font-size:12px;color:var(--text-muted);">Select a Panchayat</div></div></div>
            <div class="metric-card"><i class="ph-fill ph-thermometer metric-icon" style="color:#D64545;"></i><div><div style="font-size:13px;font-weight:600;color:var(--text-main);">${t('map.tmax')}</div><div class="metric-val">-- <span style="font-size:16px;">°C</span></div><div style="font-size:12px;color:var(--text-muted);">Select a Panchayat</div></div></div>
            <div class="metric-card"><i class="ph-fill ph-drop metric-icon" style="color:#075A8D;"></i><div><div style="font-size:13px;font-weight:600;color:var(--text-main);">${t('map.rh')}</div><div class="metric-val">-- <span style="font-size:16px;">%</span></div><div style="font-size:12px;color:var(--text-muted);">Select a Panchayat</div></div></div>
            <div class="metric-card"><i class="ph-bold ph-wind metric-icon" style="color:#64748B;"></i><div><div style="font-size:13px;font-weight:600;color:var(--text-main);">${t('map.wind')}</div><div class="metric-val">-- <span style="font-size:16px;">km/h</span></div><div style="font-size:12px;color:var(--text-muted);">Select a Panchayat</div></div></div>
          </div>
          <div class="card"><div style="color:var(--text-muted); text-align:center; padding:20px; font-size:13px;">Please select a Panchayat from the dropdown menu to view detailed weather intelligence and forecasts.</div></div>
        </div>
      </div>
    `;
    return;
  }

  const gp_code = state.panchayat.gp_code;
  const gp_name = state.panchayat.gp_name || 'Selected Panchayat';
  const block_name = state.block || 'Selected Block';

  // Fetch all data in parallel, never blocking the render
  const [fc, mc, sys] = await Promise.all([
    apiFetch(`/api/panchayat/${gp_code}/forecast`),
    apiFetch('/api/model-comparison'),
    apiFetch('/api/system-status')
  ]);

  const current = fc?.current || { rain: 'N/A', temp: 'N/A', humidity: 'N/A', wind: 'N/A' };
  const blockVal = fc?.block_forecast_rain ?? 40;
  const downVal  = fc?.downscaled_rain ?? 32;
  const dailyForecasts = fc?.daily_forecasts || [];
  const mcData = mc || { model_mae: 'N/A', model_rmse: 'N/A', skill_score_pct: 'N/A' };
  const sysData = sys || {};

  // Build forecast day HTML
      // Generate 7 consecutive dates in Asia/Kolkata timezone starting from today
  const lang = getLang();
  const dtf = new Intl.DateTimeFormat(lang === 'hi' ? 'hi-IN' : lang === 'mr' ? 'mr-IN' : 'en-IN', {
    day: '2-digit', month: 'short', timeZone: 'Asia/Kolkata'
  });
  
  let forecastDayHTML = '';
  const now = new Date();
  const year = now.toLocaleString('en-US', { year: 'numeric', timeZone: 'Asia/Kolkata' });
  const month = now.toLocaleString('en-US', { month: '2-digit', timeZone: 'Asia/Kolkata' });
  const dayStr = now.toLocaleString('en-US', { day: '2-digit', timeZone: 'Asia/Kolkata' });
  const tzStr = `${year}-${month}-${dayStr}T12:00:00+05:30`;
  const baseDate = new Date(tzStr); // Safe anchor in IST noon
  
  for (let i = 0; i < 7; i++) {
    const targetDate = new Date(baseDate);
    targetDate.setDate(targetDate.getDate() + i);
    const dateStr = dtf.format(targetDate);
    
    // Build ISO string YYYY-MM-DD strictly in Asia/Kolkata timezone
    const y = targetDate.toLocaleString('en-US', { year: 'numeric', timeZone: 'Asia/Kolkata' });
    const m = targetDate.toLocaleString('en-US', { month: '2-digit', timeZone: 'Asia/Kolkata' });
    const d = targetDate.toLocaleString('en-US', { day: '2-digit', timeZone: 'Asia/Kolkata' });
    const targetIso = `${y}-${m}-${d}`;
    
    // Find if the backend returned actual data for THIS exact date
    const dObj = dailyForecasts.find(f => f.date === targetIso);
    let label = i === 0 ? t('map.today') : i === 1 ? t('map.tomorrow') : `${t('dashboard.day')} ${i+1}`;
    
    if (dObj) {
      forecastDayHTML += `
        <div class="fcst-day">
          <div class="fcst-title">${label}</div>
          <div class="fcst-date">${dateStr}</div>
          <i class="${weatherIcon(dObj?.icon || 'cloud')} fcst-icon" style="color:${weatherIconColor(dObj?.icon || 'cloud')};"></i>
          <div class="fcst-rain">${dObj.rain} mm</div>
          <div class="fcst-temp">${dObj.temp} °C</div>
        </div>
      `;
    } else {
      forecastDayHTML += `
        <div class="fcst-day" style="opacity:0.7;">
          <div class="fcst-title">${label}</div>
          <div class="fcst-date">${dateStr}</div>
          <div style="font-size:11px;color:var(--text-muted);margin-top:10px;line-height:1.4;">${t('dashboard.forecast_unavailable')}</div>
        </div>
      `;
    }
  }

  let noForecast = '';
  if (!fc) {

    noForecast = `
      <div style="color:var(--danger); text-align:center; padding:20px; font-size:13px; display:flex; flex-direction:column; align-items:center;">
        <div style="margin-bottom:8px;">${t('dashboard.error')}</div>
        <button onclick="window.dispatchEvent(new Event('hashchange'))" style="padding:6px 12px; background:var(--primary); color:#fff; border:none; border-radius:4px; cursor:pointer;">Retry</button>
      </div>
    `;
  } else if (dailyForecasts.length === 0) {
    noForecast = `<div style="color:var(--text-muted); text-align:center; padding:20px; font-size:13px;">${t('dashboard.forecast_unavailable')}</div>`;
  } else {
    noForecast = forecastDayHTML;
  }



  // System status rows
  function statusDot(val) {
    const online = !val || val === 'Online';
    const color = online ? 'var(--success)' : 'var(--danger)';
    return `<i class="ph-fill ph-circle" style="color:${color}; font-size:10px;"></i>`;
  }
  function statusText(val) {
    return val || 'Online';
  }

  container.innerHTML = `
    <div style="display:flex; align-items:baseline; gap:16px; margin-bottom:24px;">
      <h1 style="font-size:32px; font-weight:700; color:var(--primary);">Dashboard</h1>
      <span style="color:var(--text-muted); font-size:16px;">Panchayat-level weather intelligence and agricultural conditions</span>
    </div>

    <!-- TOP: Left content + Right map -->
    <div class="dash-layout">
      <!-- LEFT -->
      <div class="dash-left">

        <!-- Weather Cards Row -->
        <div class="card weather-metrics-grid">
          <div class="metric-card">
            <i class="ph-fill ph-cloud-rain metric-icon" style="color:#4B92D4;"></i>
            <div>
              <div style="font-size:13px;font-weight:600;color:var(--text-main);">${t('map.rain')}</div>
              <div class="metric-val">${current.rain} <span style="font-size:16px;">mm</span></div>
              <div style="font-size:12px;color:var(--text-muted);">${t('map.today')}</div>
            </div>
          </div>
          <div class="metric-card">
            <i class="ph-fill ph-thermometer metric-icon" style="color:#D64545;"></i>
            <div>
              <div style="font-size:13px;font-weight:600;color:var(--text-main);">${t('map.tmax')}</div>
              <div class="metric-val">${current.temp} <span style="font-size:16px;">°C</span></div>
              <div style="font-size:12px;color:var(--text-muted);">${t('map.today')}</div>
            </div>
          </div>
          <div class="metric-card">
            <i class="ph-fill ph-drop metric-icon" style="color:#075A8D;"></i>
            <div>
              <div style="font-size:13px;font-weight:600;color:var(--text-main);">${t('map.rh')}</div>
              <div class="metric-val">${current.humidity} <span style="font-size:16px;">%</span></div>
              <div style="font-size:12px;color:var(--text-muted);">${t('map.today')}</div>
            </div>
          </div>
          <div class="metric-card">
            <i class="ph-bold ph-wind metric-icon" style="color:#64748B;"></i>
            <div>
              <div style="font-size:13px;font-weight:600;color:var(--text-main);">${t('map.wind')}</div>
              <div class="metric-val">${current.wind} <span style="font-size:16px;">km/h</span></div>
              <div style="font-size:12px;color:var(--text-muted);">${t('map.today')}</div>
            </div>
          </div>
        </div>

        <!-- AI Downscaling Hero -->
        <div class="card">
          <div style="font-size:12px;font-weight:700;color:var(--text-muted);letter-spacing:0.08em;margin-bottom:14px;">
            IMD BLOCK FORECAST &nbsp;→&nbsp; AI DOWNSCALING &nbsp;→&nbsp; PANCHAYAT FORECAST
          </div>
          <div class="hero-flow">
            <div class="flow-box imd">
              <div class="flow-title">IMD BLOCK FORECAST</div>
              <div class="flow-val"><i class="ph-fill ph-cloud-rain" style="color:#075A8D;font-size:24px;"></i> ${blockVal} mm</div>
              <div class="flow-sub">${block_name} Block</div>
            </div>
            <i class="ph-bold ph-arrow-right flow-arrow"></i>
            <div class="flow-box ai">
              <div class="flow-title" style="color:var(--warning);">AI DOWNSCALING</div>
              <div style="display:flex;align-items:center;justify-content:center;gap:8px;margin-top:8px;">
                <i class="ph-fill ph-gear" style="color:var(--warning);font-size:28px;"></i>
                <div style="font-size:11px;color:var(--text-main);text-align:left;max-width:120px;line-height:1.4;">
                  Using Panchayat-level terrain, elevation, land-use &amp; historical data
                </div>
              </div>
            </div>
            <i class="ph-bold ph-arrow-right flow-arrow"></i>
            <div class="flow-box panchayat">
              <div class="flow-title" style="color:var(--success);">PANCHAYAT FORECAST</div>
              <div class="flow-val"><i class="ph-fill ph-cloud-rain" style="color:var(--success);font-size:24px;"></i> ${downVal} mm</div>
              <div class="flow-sub">${gp_name}</div>
            </div>
          </div>
          <div style="text-align:center;font-size:12px;color:var(--text-muted);margin-top:10px;">
            Localized from Block-level forecast using Panchayat-level information.
          </div>
        </div>

        <!-- 7-Day Forecast -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <i class="ph-fill ph-calendar"></i>
              ${t('dashboard.forecast_title')} <span style="color:var(--text-muted);font-weight:400;font-size:14px;text-transform:none;">(${gp_name})</span>
            </div>
            
          </div>
          <div class="forecast-grid">${noForecast}</div>
        </div>

      </div><!-- /dash-left -->

      <!-- RIGHT: MAP -->
      <div class="dash-right">
        <div class="card" style="flex:1;display:flex;flex-direction:column;">
          <div class="card-header" style="margin-bottom:8px;">
            <div>
              <div style="font-size:17px;font-weight:700;color:var(--text-main);">Panchayat Weather Map</div>
              <div style="font-size:13px;color:var(--text-muted);margin-top:2px;">Panchayat-level localized weather (Rainfall - Today)</div>
            </div>
            <div class="map-controls">
              <select><option>Rainfall</option><option>Temperature</option></select>
              <select><option>Today</option><option>Tomorrow</option></select>
              <button class="btn-blue" onclick="window.location.hash='map'">
                <i class="ph-fill ph-chart-bar"></i> Full Map
              </button>
            </div>
          </div>
          <div class="map-container">
            <div id="dashLeafletMap" style="width:100%;height:100%;"></div>
            <div class="map-legend">
              <div style="font-weight:700;margin-bottom:6px;font-size:12px;">Rainfall (mm)</div>
              <div class="legend-item"><div class="legend-color" style="background:#D64545;"></div>&gt; 100</div>
              <div class="legend-item"><div class="legend-color" style="background:#E59A18;"></div>75–100</div>
              <div class="legend-item"><div class="legend-color" style="background:#F6C23E;"></div>50–75</div>
              <div class="legend-item"><div class="legend-color" style="background:#249447;"></div>25–50</div>
              <div class="legend-item"><div class="legend-color" style="background:#4F8F3A;"></div>10–25</div>
              <div class="legend-item"><div class="legend-color" style="background:#075A8D;"></div>1–10</div>
              <div class="legend-item"><div class="legend-color" style="background:#EAF4FA;border:1px solid #ccc;"></div>0</div>
            </div>
          </div>
        </div>
      </div><!-- /dash-right -->
    </div><!-- /dash-layout -->

  `;

      
  // Initialize mini-map
  initDashboardMap(state.panchayat ? state.panchayat.gp_code : null, gp_name);
}

function getRainColor(rain) {
  if (rain > 100) return '#B03535';
  if (rain > 75)  return '#D45A1E';
  if (rain > 50)  return '#E59A18';
  if (rain > 25)  return '#A8C93A';
  if (rain > 10)  return '#6CA02D';
  if (rain > 0)   return '#3D8F6E';
  return '#C5E4D8';
}

async function initDashboardMap(selectedGPCode, selectedGPName) {
  if (dashMap) { dashMap.remove(); dashMap = null; }

  const el = document.getElementById('dashLeafletMap');
  if (!el) return;

  dashMap = L.map('dashLeafletMap', {
    zoomControl: true, attributionControl: false, preferCanvas: true
  }).setView([18.45, 73.65], 10);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    opacity: 0.45
  }).addTo(dashMap);

  try {
    const res = await fetch('/static/data/pune_panchayats_web.geojson');
    if (res.ok) {
      const geo = await res.json();
      const layer = L.geoJSON(geo, {
        style: (f) => {
          const props = f.properties;
          const isSelected = props.gp_code === selectedGPCode;
          return isSelected
            ? { fillColor: '#E88B5B', fillOpacity: 0.95, color: '#063E5B', weight: 3 }
            : { fillColor: getRainColor(props.downscaled_rain || 0), weight: 0.8, color: '#fff', fillOpacity: 0.82 };
        },
        onEachFeature: (f, l) => {
          const props = f.properties;
          const rain = props.downscaled_rain != null ? props.downscaled_rain.toFixed(1) + ' mm' : 'N/A';
          const tmax = props.tmax != null ? props.tmax.toFixed(1) + ' °C' : 'N/A';
          const rh   = props.rh  != null ? props.rh.toFixed(1)   + ' %'  : 'N/A';
          const wind = props.wind != null ? props.wind.toFixed(1) + ' km/h': 'N/A';
          l.bindPopup(`
          <div style="font-size:11px;font-weight:700;color:var(--text-muted);margin-bottom:4px;">${t("loc.panchayat")}</div>
            <div style="min-width:160px;font-family:inherit;">
              <div style="font-weight:700;color:#06466A;border-bottom:1px solid #dde6ed;padding-bottom:6px;margin-bottom:8px;">${props.gp_name}</div>
              <div style="font-size:11px;color:#64748B;margin-bottom:6px;">${props.block_name} Block</div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:12px;">
                <div><span style="color:#64748B;">Rain</span><br><strong>${rain}</strong></div>
                <div><span style="color:#64748B;">Temp</span><br><strong>${tmax}</strong></div>
                <div><span style="color:#64748B;">Humidity</span><br><strong>${rh}</strong></div>
                <div><span style="color:#64748B;">Wind</span><br><strong>${wind}</strong></div>
              </div>
            </div>`);
        }
      }).addTo(dashMap);

      dashMap.fitBounds(layer.getBounds(), { padding: [10, 10] });
    }
  } catch (e) {
    console.warn('[Dashboard Map] GeoJSON load failed:', e);
  }
}
