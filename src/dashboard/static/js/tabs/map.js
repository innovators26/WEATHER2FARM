import { t } from '../i18n.js';
/**
 * Weather2Farm — Weather Map Tab
 *
 * KEY DESIGN:
 *   • NO tile layer. White background only. Map data comes purely from GeoJSON.
 *   • Panchayat polygons: real weather data from GeoJSON fields
 *     (downscaled_rain, tmax, rh, wind, fill_color, advisory_status, risk_label)
 *   • Block boundaries: dark navy lines over panchayats
 *   • Selected panchayat: orange fill, highlighted border
 *   • Bidirectional sync: dropdown ↔ map click
 *
 * GeoJSON fields confirmed by inspection:
 *   gp_code, gp_name, block_name, block_lgd
 *   downscaled_rain, tmax, tmin, rh, wind
 *   advisory_status, risk_label, fill_color
 *   daily_forecasts[]
 */

// ── Module singletons ─────────────────────────────────────────────────────────
let _map           = null;
let _panchayatLayer = null;
let _blockLayer    = null;
let _selectedCode  = null;   // currently selected gp_code
let _selectedBlock = null;   // currently selected block
let _variable      = 'rain'; // rain | tmax | rh | wind
let _layerIndex    = {};     // gp_code → Leaflet layer (fast lookup)

// ── Colour scale for each variable ───────────────────────────────────────────
// Calibrated to actual data ranges (rain 1–30 mm, tmax 23–32 °C, rh 78–91 %, wind 10–30 km/h)
function getRainColor(v) {
  // Colours match the reference image legend
  if (v > 100) return '#C0392B'; // deep red
  if (v >  75) return '#E74C3C'; // red
  if (v >  50) return '#E67E22'; // orange
  if (v >  25) return '#F39C12'; // amber
  if (v >  10) return '#82C341'; // lime green
  if (v >   0) return '#2196A6'; // teal-blue
  return '#D9EDF7';              // very light blue (0)
}
function getTmaxColor(v) {
  if (v > 38) return '#C0392B';
  if (v > 35) return '#E74C3C';
  if (v > 32) return '#E67E22';
  if (v > 28) return '#F39C12';
  if (v > 24) return '#82C341';
  return '#A8D68F';
}
function getRHColor(v) {
  if (v > 90) return '#1A5276';
  if (v > 80) return '#1F618D';
  if (v > 70) return '#2E86C1';
  if (v > 60) return '#7FB3D3';
  if (v > 50) return '#AED6F1';
  return '#D9EDF7';
}
function getWindColor(v) {
  if (v > 60) return '#C0392B';
  if (v > 45) return '#E74C3C';
  if (v > 30) return '#E67E22';
  if (v > 20) return '#F39C12';
  if (v > 10) return '#82C341';
  return '#A8D68F';
}

function getVarColor(props) {
  switch (_variable) {
    case 'tmax': return props.tmax != null ? getTmaxColor(props.tmax) : '#A8D68F';
    case 'rh':   return props.rh != null ? getRHColor(props.rh) : '#A8D68F';
    case 'wind': return props.wind != null ? getWindColor(props.wind) : '#A8D68F';
    default:     return props.downscaled_rain != null ? getRainColor(props.downscaled_rain) : '#A8D68F';
  }
}

// ── Legend data ───────────────────────────────────────────────────────────────
const LEGENDS = {
  rain: {
    label: 'Rainfall (mm)',
    rows: [
      { color: '#C0392B', text: '> 100' },
      { color: '#E74C3C', text: '75 – 100' },
      { color: '#E67E22', text: '50 – 75' },
      { color: '#F39C12', text: '25 – 50' },
      { color: '#82C341', text: '10 – 25' },
      { color: '#2196A6', text: '1 – 10' },
      { color: '#D9EDF7', text: '0', border: true }
    ]
  },
  tmax: {
    label: 'Max Temperature (°C)',
    rows: [
      { color: '#C0392B', text: '> 38' },
      { color: '#E74C3C', text: '35 – 38' },
      { color: '#E67E22', text: '32 – 35' },
      { color: '#F39C12', text: '28 – 32' },
      { color: '#82C341', text: '24 – 28' },
      { color: '#A8D68F', text: '< 24' }
    ]
  },
  rh: {
    label: 'Humidity (%)',
    rows: [
      { color: '#1A5276', text: '> 90' },
      { color: '#1F618D', text: '80 – 90' },
      { color: '#2E86C1', text: '70 – 80' },
      { color: '#7FB3D3', text: '60 – 70' },
      { color: '#AED6F1', text: '50 – 60' },
      { color: '#D9EDF7', text: '< 50', border: true }
    ]
  },
  wind: {
    label: 'Wind Speed (km/h)',
    rows: [
      { color: '#C0392B', text: '> 60' },
      { color: '#E74C3C', text: '45 – 60' },
      { color: '#E67E22', text: '30 – 45' },
      { color: '#F39C12', text: '20 – 30' },
      { color: '#82C341', text: '10 – 20' },
      { color: '#A8D68F', text: '< 10' }
    ]
  }
};

function buildLegendHTML() {
  const ld = LEGENDS[_variable];
  const rows = ld.rows.map(r =>
    `<div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
       <div style="width:18px;height:13px;background:${r.color};border-radius:3px;flex-shrink:0;${r.border ? 'border:1px solid #aaa;' : ''}"></div>
       <span style="font-size:12px;color:#374151;">${r.text}</span>
     </div>`
  ).join('');

  return `
    <div style="font-weight:700;font-size:12px;color:#06466B;margin-bottom:9px;letter-spacing:0.03em;">${ld.label.toUpperCase()}</div>
    ${rows}
    <div style="border-top:1px solid #E5E7EB;margin:10px 0 8px;"></div>
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
      <div style="width:18px;height:4px;background:#06466B;border-radius:2px;flex-shrink:0;"></div>
      <span style="font-size:11px;color:#6B7280;">Block Boundary</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;">
      <div style="width:18px;height:1px;background:#FFFFFF;border:1px solid #ccc;border-radius:1px;flex-shrink:0;"></div>
      <span style="font-size:11px;color:#6B7280;">Panchayat Boundary</span>
    </div>`;
}

// ── Panchayat style ───────────────────────────────────────────────────────────
function panchayatStyle(props) {
  const isSelected = props.gp_code === _selectedCode;
  if (isSelected) {
    return { fillColor: '#F28C55', fillOpacity: 1, color: '#06466B', weight: 3 };
  }
  
  const inSelectedBlock = _selectedBlock && props.block_name === _selectedBlock;
  const opacity = (_selectedBlock && !inSelectedBlock) ? 0.3 : 1.0;
  
  return { fillColor: getVarColor(props), fillOpacity: opacity, color: '#FFFFFF', weight: 0.8 };
}

function hoverStyle(props) {
  if (props.gp_code === _selectedCode) return null;
  const base = getVarColor(props);
  // darken by overlaying semi-transparent dark
  return { fillColor: base, fillOpacity: 1, color: '#06466B', weight: 1.5 };
}

// ── Popup content ─────────────────────────────────────────────────────────────
function buildPopup(props) {
  const rain = props.downscaled_rain != null ? props.downscaled_rain.toFixed(1) + ' mm' : 'N/A';
  const tmax = props.tmax            != null ? props.tmax.toFixed(1)            + ' °C' : 'N/A';
  const rh   = props.rh              != null ? props.rh.toFixed(1)              + ' %'  : 'N/A';
  const wind = props.wind            != null ? props.wind.toFixed(1)            + ' km/h': 'N/A';
  const risk = props.risk_label      || props.advisory_status || 'N/A';

  const riskColor = {
    'Normal / Favorable': '#27AE60',
    'Normal': '#27AE60',
    'WARNING': '#E67E22',
    'DANGER':  '#C0392B'
  }[props.advisory_status] || '#E67E22';

  return `
    <div style="min-width:210px;font-family:Inter,system-ui,sans-serif;padding:2px;">
      <div style="font-weight:700;font-size:15px;color:#06466B;border-bottom:2px solid #E5E7EB;padding-bottom:8px;margin-bottom:10px;">
        ${props.gp_name}
        <div style="font-size:11px;font-weight:400;color:#9CA3AF;margin-top:2px;">${props.block_name} ${t("loc.block")}</div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">
        <div>
          <div style="font-size:11px;color:#9CA3AF;margin-bottom:2px;">${t("map.var_rain")}</div>
          <div style="font-size:14px;font-weight:700;color:#1F2937;">${rain}</div>
        </div>
        <div>
          <div style="font-size:11px;color:#9CA3AF;margin-bottom:2px;">Temperature</div>
          <div style="font-size:14px;font-weight:700;color:#1F2937;">${tmax}</div>
        </div>
        <div>
          <div style="font-size:11px;color:#9CA3AF;margin-bottom:2px;">${t("map.var_hum")}</div>
          <div style="font-size:14px;font-weight:700;color:#1F2937;">${rh}</div>
        </div>
        <div>
          <div style="font-size:11px;color:#9CA3AF;margin-bottom:2px;">${t("map.var_wind")}</div>
          <div style="font-size:14px;font-weight:700;color:#1F2937;">${wind}</div>
        </div>
      </div>
      <div style="background:#F9FAFB;border-radius:6px;padding:8px 10px;margin-bottom:10px;font-size:12px;display:flex;justify-content:space-between;align-items:center;">
        <span style="color:#6B7280;">Status</span>
        <span style="font-weight:700;color:${riskColor};">${risk}</span>
      </div>
      <div style="display:flex;gap:8px;">
        <button onclick="window.location.hash='dashboard'"
          style="flex:1;background:#06466B;color:#fff;border:none;border-radius:7px;padding:8px;font-size:12px;font-weight:600;cursor:pointer;font-family:inherit;">
          View Forecast
        </button>
        <button onclick="window.location.hash='advisory'"
          style="flex:1;background:transparent;color:#06466B;border:2px solid #06466B;border-radius:7px;padding:8px;font-size:12px;font-weight:600;cursor:pointer;font-family:inherit;">
          Advisory
        </button>
      </div>
    </div>`;
}

// ── Restyle all panchayat layers ──────────────────────────────────────────────
function restyleAll() {
  if (!_panchayatLayer) return;
  _panchayatLayer.eachLayer(l => l.setStyle(panchayatStyle(l.feature.properties)));
}

// ── Select a panchayat ────────────────────────────────────────────────────────
function selectPanchayat(gpCode, fromMapClick) {
  const prev = _selectedCode;
  _selectedCode = gpCode;

  // Restyle previous
  if (prev && _layerIndex[prev]) {
    _layerIndex[prev].setStyle(panchayatStyle(_layerIndex[prev].feature.properties));
  }
  // Restyle new
  if (_layerIndex[gpCode]) {
    const l = _layerIndex[gpCode];
    l.setStyle(panchayatStyle(l.feature.properties));
    l.bringToFront();
    _map.flyToBounds(l.getBounds(), { padding: [50, 50], maxZoom: 13, duration: 0.5 });
    l.openPopup();
  }

  // Propagate to global dropdowns if this came from a map click
  if (fromMapClick) {
    const props = _layerIndex[gpCode]?.feature?.properties;
    if (props) {
      window.dispatchEvent(new CustomEvent('agroscale:select-panchayat', {
        detail: { gp_code: props.gp_code, gp_name: props.gp_name, block_name: props.block_name }
      }));
    }
  }
}

// ── Initialize Leaflet (called once) ─────────────────────────────────────────
async function initLeafletMap() {
  if (!document.getElementById('weatherMapEl')) return;

  // ── Create map — NO tile layer, white canvas background ──────────────────
  _map = L.map('weatherMapEl', {
    zoomControl:       true,
    attributionControl: false,   // no attr bar needed without tiles
    preferCanvas:      true      // better perf for 1390 polygons
  });

  // White background via CSS on the map container (set below in HTML)
  // Leaflet itself doesn't set a bg color — we just don't add any tileLayer

  // ── Load both GeoJSON files in parallel ──────────────────────────────────
  const [pRes, bRes] = await Promise.all([
    fetch('/static/data/pune_panchayats_web.geojson'),
    fetch('/static/data/pune_blocks_web.geojson')
  ]);

  if (!pRes.ok || !bRes.ok) {
    document.getElementById('weatherMapEl').innerHTML =
      '<div style="display:flex;align-items:center;justify-content:center;height:100%;font-weight:700;color:#C0392B;">GeoJSON failed to load. Check file paths.</div>';
    return;
  }

  const panchayatsGeo = await pRes.json();
  const blocksGeo     = await bRes.json();

  // ── LAYER 1: Panchayat fill polygons ─────────────────────────────────────
  _panchayatLayer = L.geoJSON(panchayatsGeo, {
    style: f => panchayatStyle(f.properties),
    onEachFeature: (feature, layer) => {
      const props = feature.properties;
      _layerIndex[props.gp_code] = layer;

      // Popup
      layer.bindPopup(buildPopup(props), { maxWidth: 280, closeButton: true });

      // Hover
      layer.on('mouseover', () => {
        const hs = hoverStyle(props);
        if (hs) { layer.setStyle(hs); layer.bringToFront(); }
      });
      layer.on('mouseout', () => {
        layer.setStyle(panchayatStyle(props));
        if (_blockLayer) _blockLayer.bringToFront();
      });

      // Click → select
      layer.on('click', () => selectPanchayat(props.gp_code, true));
    }
  }).addTo(_map);

  // ── LAYER 2: Block boundaries (on top, non-interactive) ──────────────────
  _blockLayer = L.geoJSON(blocksGeo, {
    style: () => ({
      fill:      false,
      color:     '#06466B',
      weight:    2.8,
      opacity:   1
    }),
    interactive: false
  }).addTo(_map);

  // ── Fit to full Pune extent ───────────────────────────────────────────────
  _map.fitBounds(_panchayatLayer.getBounds(), { padding: [12, 12] });

  // ── Apply initial selection if state has one ──────────────────────────────
  if (_selectedCode && _layerIndex[_selectedCode]) {
    const l = _layerIndex[_selectedCode];
    l.setStyle(panchayatStyle(l.feature.properties));
    _map.flyToBounds(l.getBounds(), { padding: [50, 50], maxZoom: 13 });
  }
}

// ── Public render() — called by app.js on every tab switch ───────────────────
export async function render(state) {
  const container = document.getElementById('map-tab');

  // Build DOM only once
  if (!_map) {
    container.innerHTML = `
      <!-- PAGE HEADER ROW -->
      <div style="display:flex;align-items:center;gap:16px;margin-bottom:16px;flex-wrap:wrap;">
        <div>
          <h1 style="font-size:28px;font-weight:700;color:#06466B;margin:0;">Weather Map</h1>
          <div style="font-size:13px;color:#9CA3AF;margin-top:2px;">
            Pune District Panchayats &mdash; Actual model output data
          </div>
        </div>

        <!-- Variable + Forecast selectors aligned right -->
        <div style="margin-left:auto;display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
          <div style="display:flex;align-items:center;gap:8px;">
            <label style="font-size:13px;font-weight:600;color:#374151;white-space:nowrap;">Variable</label>
            <select id="mapVarSelect"
              style="height:38px;border-radius:8px;border:1px solid #D1D5DB;padding:0 12px;
                     font-size:13px;background:#fff;color:#1F2937;cursor:pointer;outline:none;">
              <option value="rain">Rainfall (mm)</option>
              <option value="tmax">Temperature (°C)</option>
              <option value="rh">Humidity (%)</option>
              <option value="wind">Wind Speed (km/h)</option>
            </select>
          </div>
          <div style="display:flex;align-items:center;gap:8px;">
            <label style="font-size:13px;font-weight:600;color:#374151;white-space:nowrap;">Forecast Period</label>
            <select id="mapPeriodSelect"
              style="height:38px;border-radius:8px;border:1px solid #D1D5DB;padding:0 12px;
                     font-size:13px;background:#fff;color:#1F2937;cursor:pointer;outline:none;">
              <option value="today">Today</option>
              <option value="tomorrow">Tomorrow</option>
              <option value="3days">Next 3 Days</option>
            </select>
          </div>
        </div>
      </div>

      <!-- MAP CARD -->
      <div style="background:#fff;border-radius:14px;border:1px solid #E5E7EB;
                  box-shadow:0 1px 6px rgba(0,0,0,0.06);overflow:hidden;position:relative;">

        <!-- Leaflet map — white bg, no tiles -->
        <div id="weatherMapEl"
          style="width:100%;height:580px;background:#FFFFFF;"></div>

        <!-- Legend panel (top-right, inside map) -->
        <div id="mapLegend"
          style="position:absolute;top:16px;right:16px;z-index:1000;
                 background:rgba(255,255,255,0.97);border:1px solid #E5E7EB;
                 border-radius:10px;padding:14px 16px;min-width:145px;
                 box-shadow:0 2px 12px rgba(0,0,0,0.10);">
          <div id="mapLegendInner"></div>
        </div>

        <!-- Selection label (bottom-left) -->
        <div id="mapSelLabel"
          style="display:none;position:absolute;bottom:16px;left:16px;z-index:1000;
                 background:rgba(255,255,255,0.95);border:1px solid #E5E7EB;
                 border-radius:8px;padding:8px 14px;font-size:13px;
                 box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        </div>
      </div>
    `;

    // Render legend
    document.getElementById('mapLegendInner').innerHTML = buildLegendHTML();

    // Variable selector
    document.getElementById('mapVarSelect').addEventListener('change', e => {
      _variable = e.target.value;
      restyleAll();
      document.getElementById('mapLegendInner').innerHTML = buildLegendHTML();
    });

    // Listen for selection dispatched by map click → update global state
    window.addEventListener('agroscale:select-panchayat', evt => {
      const { gp_code, gp_name, block_name } = evt.detail;

      // Update global state via selectors
      const blockSel = document.getElementById('blockSelect');
      const panSel   = document.getElementById('panchayatSelect');

      if (blockSel && blockSel.value !== block_name) {
        blockSel.value = block_name;
        blockSel.dispatchEvent(new Event('change'));
      }
      setTimeout(() => {
        if (panSel) {
          panSel.value = gp_code;
          panSel.dispatchEvent(new Event('change'));
        }
      }, 160);

      // Update selection label
      const lbl = document.getElementById('mapSelLabel');
      if (lbl) {
        lbl.style.display = 'block';
        lbl.innerHTML = `<span style="color:#9CA3AF;font-size:11px;">Selected</span>
          <strong style="color:#06466B;margin-left:6px;">${gp_name}</strong>
          <span style="color:#9CA3AF;font-size:11px;margin-left:6px;">${block_name}</span>`;
      }
    });

    // Init Leaflet
    await initLeafletMap();
  }

  // ── Every time tab becomes visible ────────────────────────────────────────
  // Sync selected panchayat from global state
  const newCode = state.panchayat ? state.panchayat.gp_code : null;
  const newBlock = state.block || null;

  let changed = false;

  if (newBlock !== _selectedBlock) {
    _selectedBlock = newBlock;
    changed = true;
    if (_selectedBlock && _blockLayer) {
      _blockLayer.eachLayer(l => {
        if (l.feature.properties.block_name === _selectedBlock) {
          _map.flyToBounds(l.getBounds(), { padding: [20, 20], maxZoom: 11, duration: 0.5 });
        }
      });
    } else if (!_selectedBlock && _panchayatLayer) {
      _map.flyToBounds(_panchayatLayer.getBounds(), { padding: [12, 12], duration: 0.5 });
    }
  }

  if (newCode !== _selectedCode) {
    _selectedCode = newCode;
    changed = true;
    if (newCode && _layerIndex[newCode]) {
      const l = _layerIndex[newCode];
      l.bringToFront();
      _map.flyToBounds(l.getBounds(), { padding: [50, 50], maxZoom: 13, duration: 0.5 });
      l.openPopup();

      // Show label
      const lbl = document.getElementById('mapSelLabel');
      if (lbl) {
        lbl.style.display = 'block';
        const props = l.feature.properties;
        lbl.innerHTML = `<span style="color:#9CA3AF;font-size:11px;">Selected</span>
          <strong style="color:#06466B;margin-left:6px;">${props.gp_name}</strong>
          <span style="color:#9CA3AF;font-size:11px;margin-left:6px;">${props.block_name}</span>`;
      }
    } else if (!newCode) {
      const lbl = document.getElementById('mapSelLabel');
      if (lbl) lbl.style.display = 'none';
    }
  }

  if (changed) {
    restyleAll();
    if (_blockLayer) {
      _blockLayer.setStyle(f => ({
        fill:      false,
        color:     '#06466B',
        weight:    f.properties.block_name === _selectedBlock ? 4 : 2.8,
        opacity:   f.properties.block_name === _selectedBlock ? 1 : 0.6
      }));
    }
  }

  // Always invalidate after tab becomes visible (fixes grey/blank tiles from hidden container)
  setTimeout(() => { if (_map) _map.invalidateSize(); }, 100);
}
