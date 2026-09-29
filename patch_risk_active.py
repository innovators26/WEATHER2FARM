import re

FILE = r"src\dashboard\static\js\tabs\risk.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update the grid-template-columns for the Active Risk Conditions container
old_active_container = r'<div style="display:grid; grid-template-columns: repeat\(auto-fill, minmax\(300px, 1fr\)\); gap:20px;">'
new_active_container = r'<div style="display:grid; grid-template-columns: ${risks.length === 1 ? \'1fr\' : \'repeat(auto-fit, minmax(450px, 1fr))\'}; gap:20px; width: 100%; box-sizing: border-box;">'
code = re.sub(old_active_container, new_active_container, code)

# 2. Re-write buildRiskCard to output the horizontal layout
old_buildRiskCard_re = re.search(r'function buildRiskCard\(r\) \{.*?return `.*?`;\n    \}', code, re.DOTALL)
if old_buildRiskCard_re:
    new_buildRiskCard = """
  function buildRiskCard(r) {
      const s = r.level.toUpperCase();
      let bg = '#F4F7F9';
      let dot = '#4F8F3A';
      
      if (s === 'HIGH' || s === 'SEVERE' || s === 'CRITICAL') { bg = '#FFF5F5'; dot = '#D64545'; }
      else if (s === 'MODERATE' || s === 'WARNING' || s === 'WATCH') { bg = '#FFFDF5'; dot = '#E59A17'; }
      else { bg = '#F5FFF5'; dot = '#4F8F3A'; }
  
      let trigger = "Rule engine condition met";
      let assessment = r.reason;
      if (r.reason.includes("Exceeds")) {
         trigger = r.reason;
      }
      
      let actionStr = "Monitor conditions.";
      if (adv.avoid && adv.avoid.length > 0 && (s === 'HIGH' || s === 'SEVERE')) {
          actionStr = "Avoid: " + adv.avoid.map(a => t(a)).join(', ');
      } else if (actions.length > 0) {
          actionStr = t(actions[0].action); // fallback
      } else {
          actionStr = t(actionStr);
      }
  
      return `
        <div style="background:${bg}; border:1px solid #DDE6ED; border-radius:8px; display:flex; flex-direction:column; overflow:hidden; width:100%; box-sizing:border-box;">
          <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #DDE6ED; padding:16px 20px; background:${bg};">
            <h3 style="margin:0; font-size:16px; font-weight:700; color:#17324D;">${t(r.risk_name).toUpperCase()}</h3>
            <div style="display:flex; align-items:center; gap:6px; background:#fff; padding:4px 10px; border-radius:12px; border:1px solid #DDE6ED;">
              <div style="width:10px; height:10px; border-radius:50%; background:${dot};"></div>
              <span style="font-size:12px; font-weight:700; color:#17324D;">${s}</span>
            </div>
          </div>
          
          <div style="display:grid; grid-template-columns: 1.5fr 1.5fr 1fr; gap:24px; padding:20px; background:#fff;">
            <div>
              <div style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase; margin-bottom:6px;">Assessment</div>
              <div style="font-size:14px; color:#17324D; line-height:1.5;">${t(assessment)}</div>
            </div>
            
            <div>
              <div style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase; margin-bottom:6px;">Recommended Action</div>
              <div style="font-size:14px; color:#17324D; line-height:1.5;">${actionStr}</div>
            </div>
            
            <div>
              <div style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase; margin-bottom:6px;">Trigger</div>
              <div style="font-size:13px; color:#64748B; line-height:1.5;">${t(trigger)}</div>
            </div>
          </div>
        </div>
      `;
    }
"""
    code = code.replace(old_buildRiskCard_re.group(0), new_buildRiskCard.strip())
else:
    print("WARNING: Could not find buildRiskCard")

# Make sure responsive media query for this inner grid exists in style.css or risk.js
responsive_css = """
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
"""
# Apply a class to the inner grid
code = code.replace('<div style="display:grid; grid-template-columns: 1.5fr 1.5fr 1fr;', '<div class="active-risk-card-inner" style="display:grid; grid-template-columns: 1.5fr 1.5fr 1fr;')
code += "\n" + responsive_css

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Patched buildRiskCard layout")
