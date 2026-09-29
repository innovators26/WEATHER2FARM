import re

FILE = r"src\dashboard\static\js\tabs\risk.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update DICT with missing translations
dict_addition = """
    "alert_reason_severe": "Severe Weather Risk",
    "action_halt_irrigation": "Halt Irrigation",
    "action_delay_fertilizer": "Delay Fertilizer Application",
    "action_clear_drainage": "Clear Drainage Channels",
    "why_heavy_rain": "Heavy rainfall expected",
    "why_rain_leaching": "Rain may cause nutrient leaching",
    "why_waterlogging_sensitive": "Waterlogging risk",
    "timing_24h": "Within 24 hours",
    "timing_3_7d": "3-7 days",
    "timing_now": "Now",
"""
code = code.replace('"risk_disease": "Disease Favorable",', '"risk_disease": "Disease Favorable",\n' + dict_addition)

# 2. Add translation to the raw labels used in the HTML!
# Primary concern: adv.alert_reason -> t(adv.alert_reason)
# Priority action: actions[0].action -> t(actions[0].action)
# Also apply t() inside the actions loop!
# Already in current_risk.html, the actions loop has:
# ${a.action} and ${a.why} and ${a.when}
# Wait, let's see how they are populated. 
# Actually, the user says "DO NOT SHOW raw internal keys... convert them using the semantic translation".
# Let's see how they are generated.
actions_loop = """
      actionsHtml = actions.map((a, idx) => `
        <div style="display:flex; gap:16px; margin-bottom:${idx === actions.length-1 ? '0' : '16px'};">
            <div style="font-size:16px; font-weight:700; color:#064B70; min-width:24px;">0${idx+1}</div>
            <div>
                <div style="font-size:15px; font-weight:700; color:#17324D; margin-bottom:4px;">${t(a.action)}</div>
                <div style="font-size:13px; color:#64748B;">${t(a.why || '')} ${a.when ? '• ' + t(a.when) : ''}</div>
            </div>
        </div>
      `).join('');
"""
# Need to replace the old actionsHtml logic
old_actions_loop_re = re.search(r'actionsHtml = actions\.map\(.*?join\(\'\'\);', code, re.DOTALL)
if old_actions_loop_re:
    code = code.replace(old_actions_loop_re.group(0), actions_loop.strip())
else:
    print("WARNING: Could not find actions map loop")

# Also for risksHtml, currently it's:
# `... ${r.risk} ... Assessment: ${r.reason} ... Recommended Action: ${r.actions.join(', ')} ...`
risks_loop = """
      risksHtml = Object.entries(riskData.risks).map(([riskKey, r]) => {
          const color = r.severity === 'high' ? '#D64545' : r.severity === 'moderate' ? '#E59A17' : '#4F8F3A';
          return `
            <div style="background:#fff; border:1px solid #DDE6ED; border-radius:8px; padding:16px;">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div style="font-size:14px; font-weight:700; color:#17324D; text-transform:uppercase;">${t(riskKey)}</div>
                <div style="font-size:12px; font-weight:700; color:${color}; background:${color}15; padding:4px 8px; border-radius:4px;">${r.severity.toUpperCase()}</div>
              </div>
              <div style="font-size:13px; color:#64748B; margin-bottom:12px;">
                <strong style="color:#17324D;">Assessment:</strong><br>${t(r.reason)}
              </div>
              <div style="font-size:13px; color:#64748B; margin-bottom:12px;">
                <strong style="color:#17324D;">Recommended Action:</strong><br>${r.actions ? r.actions.map(act => t(act)).join(', ') : 'None'}
              </div>
              <div style="font-size:11px; color:#94A3B8;">
                Trigger: ${r.threshold || 'Rule Engine Condition Met'}
              </div>
            </div>
          `;
      }).join('');
"""
old_risks_loop_re = re.search(r'risksHtml = Object\.entries.*?join\(\'\'\);', code, re.DOTALL)
if old_risks_loop_re:
    code = code.replace(old_risks_loop_re.group(0), risks_loop.strip())
else:
    print("WARNING: Could not find risks map loop")

# 3. Restructure container.innerHTML
# I'll create a completely new HTML block to match the user's layout

new_html = """
  container.innerHTML = `
    <div style="max-width: 1450px; width: calc(100% - 48px); margin: 0 auto; display:flex; flex-direction:column; gap:20px;">
      
      <!-- HEADER -->
      <div style="display:flex; flex-direction:column; gap:4px; border-bottom:1px solid #DDE6ED; padding-bottom:16px;">
        <h1 style="font-size:32px; font-weight:700; color:#064B70; margin:0;">CROP RISK</h1>
        <div style="font-size:16px; color:#64748B;">Panchayat-level agricultural risk assessment</div>
        
        <div style="margin-top:12px; display:flex; justify-content:space-between; align-items:flex-end;">
          <div>
            <div style="font-size:24px; font-weight:700; color:#17324D;">${gp_name.toUpperCase()}</div>
            <div style="font-size:14px; color:#64748B;">${block_name} • Pune</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:12px; color:#64748B;">Last evaluated: ${dateStr}</div>
          </div>
        </div>
      </div>

      <div style="font-size:13px; color:#64748B; background:#F4F7F9; padding:10px 16px; border-radius:4px;">
        Risk assessment is generated from Weather2Farm's rule-based agricultural risk engine using current Panchayat weather, forecast conditions, terrain and crop context.
      </div>

      <!-- TODAY'S FARM RISK (FULL WIDTH) -->
      <div style="background:#fff; border:1px solid #DDE6ED; border-radius:8px; padding:20px;">
        <h2 style="font-size:14px; font-weight:700; color:#64748B; margin:0 0 16px 0; text-transform:uppercase;">Today's Farm Risk</h2>
        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:20px;">
          <div>
            <div style="font-size:12px; color:#64748B; margin-bottom:4px;">Overall Risk</div>
            <div style="font-size:20px; font-weight:700; color:${overallColor};">${overall.toUpperCase()}</div>
          </div>
          <div>
            <div style="font-size:12px; color:#64748B; margin-bottom:4px;">Primary Concern</div>
            <div style="font-size:16px; font-weight:700; color:#17324D;">${adv.alert_reason ? t(adv.alert_reason) : 'None'}</div>
          </div>
          <div>
            <div style="font-size:12px; color:#64748B; margin-bottom:4px;">Priority Action</div>
            <div style="font-size:15px; font-weight:600; color:#17324D;">${actions.length > 0 ? t(actions[0].action) : 'Continue routine monitoring'}</div>
          </div>
        </div>
      </div>

      <!-- TWO-COLUMN MAIN GRID -->
      <div style="display:grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); column-gap: 24px; row-gap: 24px;">
        
        <!-- ROW 1 : LEFT -->
        <div style="display:flex; flex-direction:column; gap:12px;">
          <h2 style="font-size:16px; font-weight:700; color:#064B70; margin:0; border-bottom:2px solid #064B70; padding-bottom:6px;">RISK OVERVIEW</h2>
          <div style="background:#fff; border:1px solid #DDE6ED; border-radius:8px; padding:20px; flex:1;">
            <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
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
            <div style="font-size:13px; color:#64748B; line-height:1.6;">
              <div><strong style="color:#17324D;">High Risk:</strong> Requires immediate attention</div>
              <div><strong style="color:#17324D;">Moderate Risk:</strong> Preventive action recommended</div>
              <div><strong style="color:#17324D;">Low Risk:</strong> Continue monitoring</div>
            </div>
          </div>
        </div>

        <!-- ROW 1 : RIGHT -->
        <div style="display:flex; flex-direction:column; gap:12px;">
          <h2 style="font-size:16px; font-weight:700; color:#064B70; margin:0; border-bottom:2px solid #064B70; padding-bottom:6px;">ACTIVE RISK CONDITIONS</h2>
          <div style="display:flex; flex-direction:column; gap:16px; flex:1;">
            ${risksHtml || '<div style="background:#fff; border:1px solid #DDE6ED; border-radius:8px; padding:20px; color:#64748B;">No active risks detected.</div>'}
          </div>
        </div>

        <!-- ROW 2 : LEFT -->
        <div style="display:flex; flex-direction:column; gap:12px;">
          <h2 style="font-size:16px; font-weight:700; color:#064B70; margin:0; border-bottom:2px solid #064B70; padding-bottom:6px;">RISK EVIDENCE</h2>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px; flex:1;">
            <div style="background:#F4F7F9; border:1px solid #DDE6ED; padding:16px; border-radius:8px; display:flex; flex-direction:column; justify-content:center;">
              <div style="font-size:13px; color:#64748B; margin-bottom:4px;">Rainfall</div>
              <div style="font-size:22px; font-weight:700; color:#17324D;">${weather.rain || 0} mm</div>
            </div>
            <div style="background:#F4F7F9; border:1px solid #DDE6ED; padding:16px; border-radius:8px; display:flex; flex-direction:column; justify-content:center;">
              <div style="font-size:13px; color:#64748B; margin-bottom:4px;">Temperature</div>
              <div style="font-size:22px; font-weight:700; color:#17324D;">${weather.temp || 0} °C</div>
            </div>
            <div style="background:#F4F7F9; border:1px solid #DDE6ED; padding:16px; border-radius:8px; display:flex; flex-direction:column; justify-content:center;">
              <div style="font-size:13px; color:#64748B; margin-bottom:4px;">Humidity</div>
              <div style="font-size:22px; font-weight:700; color:#17324D;">${weather.humidity || 0} %</div>
            </div>
            <div style="background:#F4F7F9; border:1px solid #DDE6ED; padding:16px; border-radius:8px; display:flex; flex-direction:column; justify-content:center;">
              <div style="font-size:13px; color:#64748B; margin-bottom:4px;">Wind</div>
              <div style="font-size:22px; font-weight:700; color:#17324D;">${weather.wind || 0} km/h</div>
            </div>
          </div>
        </div>

        <!-- ROW 2 : RIGHT -->
        <div style="display:flex; flex-direction:column; gap:12px;">
          <h2 style="font-size:16px; font-weight:700; color:#064B70; margin:0; border-bottom:2px solid #064B70; padding-bottom:6px;">RECOMMENDED FARM ACTIONS</h2>
          <div style="background:#fff; border:1px solid #DDE6ED; padding:20px; border-radius:8px; flex:1;">
            ${actionsHtml}
          </div>
        </div>

      </div>
      
      <!-- CROP CONTEXT (FULL WIDTH) -->
      <div style="display:flex; flex-direction:column; gap:12px;">
        <h2 style="font-size:16px; font-weight:700; color:#064B70; margin:0; border-bottom:2px solid #064B70; padding-bottom:6px;">CROP CONTEXT</h2>
        <div style="display:flex; gap:48px; background:#fff; border:1px solid #DDE6ED; padding:16px 20px; border-radius:8px;">
            <div>
                <div style="font-size:12px; color:#64748B; margin-bottom:4px;">Crop</div>
                <div style="font-size:16px; font-weight:700; color:#17324D;">${riskData.crop ? t(riskData.crop) : 'Unknown'}</div>
            </div>
            <div>
                <div style="font-size:12px; color:#64748B; margin-bottom:4px;">Growth Stage</div>
                <div style="font-size:16px; font-weight:700; color:#17324D;">${riskData.stage ? t(riskData.stage) : 'Unknown'}</div>
            </div>
            ${riskData.days_after_sowing !== undefined && riskData.days_after_sowing !== null ? `
            <div>
                <div style="font-size:12px; color:#64748B; margin-bottom:4px;">Days After Sowing (DAS)</div>
                <div style="font-size:16px; font-weight:700; color:#17324D;">${riskData.days_after_sowing}</div>
            </div>` : ''}
        </div>
      </div>

    </div>
  `;
"""

old_html_re = re.search(r'container\.innerHTML = `.*?`;', code, re.DOTALL)
if old_html_re:
    code = code.replace(old_html_re.group(0), new_html.strip())
else:
    print("WARNING: Could not find container.innerHTML assignment!")

# Ensure #risk-tab styling isn't squishing this.
# Previously I might have added scoped CSS for #risk-tab to force a max-width, but I'm handling it directly in HTML here.
# So I should also just add a media query to handle the two-column grid on mobile!
code += """
// Ensure responsive CSS is injected
if (!document.getElementById('risk-grid-style')) {
    const style = document.createElement('style');
    style.id = 'risk-grid-style';
    style.innerHTML = `
        @media (max-width: 900px) {
            #risk-tab .display\\\\:grid {
                grid-template-columns: 1fr !important;
            }
        }
    `;
    document.head.appendChild(style);
}
"""

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Patched risk.js layout and dictionary")
