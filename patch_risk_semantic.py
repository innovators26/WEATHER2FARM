import os

FILE = r"src\dashboard\static\js\tabs\risk.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

DICT_INJECTION = """
const DICT = {
    // Risks
    "risk_water_stress": "Water Stress",
    "risk_heavy_rain": "Heavy Rainfall",
    "risk_waterlogging": "Waterlogging",
    "risk_heat_stress": "Heat Stress",
    "risk_disease": "Disease Favorable",

    // Reasons
    "reason_prolonged_dry": "Extended period of low rainfall leading to potential soil moisture deficit.",
    "reason_high_rain": "Forecast predicts significant rainfall exceeding safe thresholds.",
    "reason_high_humidity": "Persistently high humidity increases the risk of disease outbreaks.",
    "reason_extreme_temp": "Temperatures exceeding the crop's threshold cause severe physiological stress.",

    // Explanations
    "why_dry_forecast": "Current and forecasted weather indicates insufficient precipitation for normal crop requirements.",
    "why_high_wind": "High wind speeds can cause physical damage or interfere with spraying.",
    "why_late_nitrogen": "Late nitrogen application during reproductive stages may delay maturity.",
    "why_weeding": "Weed management should be planned according to the crop stage and field moisture conditions.",
    "why_germination": "Moisture conditions during establishment are important for uniform seed germination.",
    "alert_reason_watch": "Conditions require continued monitoring.",
    "reason_waterlogging": "Excessive rainfall may lead to waterlogging, depriving roots of oxygen.",

    // Actions
    "action_critical_irrigation": "Check soil moisture and irrigate only when the crop requires additional moisture.",
    "action_postpone_spray": "Postpone pesticide or foliar applications when rainfall or unsuitable weather is expected.",
    "action_withhold_n": "Avoid unnecessary nitrogen application until the crop stage and weather conditions are suitable.",
    "action_weeding": "Plan weed management during the recommended crop-stage window when field conditions permit.",
    "action_seedbed": "Monitor soil moisture and establishment conditions during the early crop stage.",

    // Timings
    "timing_now": "Now",
    "timing_24h": "Next 24 hours",
    "timing_3_7d": "Next 3-7 days",

    // Stages
    "stage_sowing": "Sowing / Establishment",
    "stage_vegetative": "Vegetative",
    "stage_flowering": "Flowering",
    "stage_fruiting": "Fruiting",
    "stage_maturity": "Maturity",
    "stage_harvesting": "Harvesting"
};

function t(key) {
    if (!key) return '';
    const lkey = key.toLowerCase();
    if (DICT[lkey]) return DICT[lkey];
    if (DICT['risk_' + lkey]) return DICT['risk_' + lkey];
    if (DICT['reason_' + lkey]) return DICT['reason_' + lkey];
    if (DICT['why_' + lkey]) return DICT['why_' + lkey];
    if (DICT['action_' + lkey]) return DICT['action_' + lkey];
    if (DICT['timing_' + lkey]) return DICT['timing_' + lkey];
    if (DICT['stage_' + lkey]) return DICT['stage_' + lkey];
    
    // Capitalize properly if no mapping found (fallback)
    return key.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
}

export async function render(state) {
"""

code = code.replace("export async function render(state) {", DICT_INJECTION)

EARLY_RETURN = """  const container = document.getElementById('risk-tab');
  
  if (!state.panchayat) {
    container.innerHTML = `
      <div style="display:flex;align-items:baseline;gap:16px;margin-bottom:24px;">
        <h1 style="font-size:32px;font-weight:700;color:var(--primary);">Crop Risk</h1>
        <span style="color:var(--text-muted);font-size:16px;">Panchayat-level agricultural risk assessment</span>
      </div>
      <div style="padding:40px;text-align:center;color:#64748B;background:#F4F7F9;border-radius:8px;border:1px solid #DDE6ED;">
        <i class="ph-fill ph-map-pin" style="font-size: 32px; margin-bottom: 12px; color:#0B5E8E;"></i>
        <h3 style="margin-bottom:8px;color:#17324D;">NO PANCHAYAT SELECTED</h3>
        <p>Please select a Panchayat from the top navigation to view its localized risk assessment.</p>
      </div>
    `;
    return;
  }

  const gp_code = state.panchayat.gp_code;
  const gp_name  = state.panchayat.gp_name;
  const block_name = state.block || "Selected Block";"""

original_top = """  const container = document.getElementById('risk-tab');
  const gp_name  = state.panchayat ? state.panchayat.gp_name : 'Unknown';
  const block_name = state.panchayat ? state.panchayat.block_name || 'Selected Block' : 'Unknown';"""

code = code.replace(original_top, EARLY_RETURN)

# Fix payload missing gp_code variable if original used state.panchayat.gp_code
code = code.replace('gp_code: state.panchayat ? state.panchayat.gp_code : "273397"', 'gp_code: gp_code')

# Fix translations for cards
code = code.replace('${r.risk_name.toUpperCase()}', '${t(r.risk_name).toUpperCase()}')
code = code.replace('${assessment}', '${t(assessment)}')
code = code.replace('${actionStr}', '${t(actionStr)}')
code = code.replace('${trigger}', '${t(trigger)}')

# Fix CROP CONTEXT translation
code = code.replace("${riskData.stage || 'Unknown'}", "${t(riskData.stage || 'Unknown')}")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Applied semantic mappings to risk.js")
