import os
FILE = r"src\dashboard\static\js\tabs\risk.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

target = """      <!-- CROP CONTEXT -->
      <div>
        <h2 style="font-size:18px; font-weight:700; color:#064B70; margin-bottom:16px; border-bottom:2px solid #064B70; padding-bottom:8px; display:inline-block;">CROP CONTEXT</h2>
        <div style="display:flex; gap:32px; background:#fff; border:1px solid #DDE6ED; padding:20px; border-radius:8px;">
            <div>
                <div style="font-size:12px; color:#64748B; margin-bottom:4px;">Crop</div>
                <div style="font-size:16px; font-weight:700; color:#17324D;">${riskData.crop || 'Unknown'}</div>
            </div>
            <div>
                <div style="font-size:12px; color:#64748B; margin-bottom:4px;">Growth Stage</div>
                <div style="font-size:16px; font-weight:700; color:#17324D;">${t(riskData.stage || 'Unknown')}</div>
            </div>
            <div>
                <div style="font-size:12px; color:#64748B; margin-bottom:4px;">Days After Sowing</div>
                <div style="font-size:16px; font-weight:700; color:#17324D;">${riskData.days_after_sowing || '0'} days</div>
            </div>
        </div>
      </div>"""

if target in code:
    code = code.replace(target, "")
    with open(FILE, "w", encoding="utf-8") as f:
        f.write(code)
    print("Removed Crop Context from risk.js")
else:
    print("Target not found.")
