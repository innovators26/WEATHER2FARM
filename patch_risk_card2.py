import re

FILE = r"src\dashboard\static\js\tabs\risk.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

start_idx = code.find('function buildRiskCard(r) {')
if start_idx != -1:
    end_idx = code.find('  let risksHtml =', start_idx)
    
    # We want to replace from start_idx to the end of the function block
    # Actually, let's just find the closing brace before `let risksHtml`
    # Or just use regex to find the end of the return string
    end_of_return = code.find('`;', start_idx)
    end_of_func = code.find('}', end_of_return)
    
    new_func = """function buildRiskCard(r) {
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
          
          <div class="active-risk-card-inner" style="display:grid; grid-template-columns: 1.5fr 1.5fr 1fr; gap:24px; padding:20px; background:#fff;">
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
    }"""
    code = code[:start_idx] + new_func + code[end_of_func+1:]
    
    with open(FILE, "w", encoding="utf-8") as f:
        f.write(code)
    print("Replaced buildRiskCard successfully")
else:
    print("Could not find start_idx")
