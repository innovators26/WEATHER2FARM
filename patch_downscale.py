import os

FILE = r"src\dashboard\static\js\tabs\downscaling.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

replacement = """      const d = await res.json();
      
      await tick('step4', 300);
      await tick('step5', 300);

      // Update DOM
      document.getElementById('aiResultCard').style.opacity = '1';
      document.getElementById('aiResultCard').innerHTML = `
            <div style="font-size:14px; font-weight:700; color:#064B70; margin-bottom:20px; text-transform:uppercase; border-bottom:1px solid #eee; padding-bottom:10px;">
              Final Result
            </div>
            <div style="text-align:center;">
              <div style="font-size:11px; color:#64748B; font-weight:700; text-transform:uppercase;">IMD Block Forecast</div>
              <div style="font-size:24px; font-weight:700; color:#17324D;">${d.block_forecast} mm</div>
              <div style="font-size:24px; color:#94A3B8; margin:8px 0;">+</div>
              <div style="font-size:11px; color:#64748B; font-weight:700; text-transform:uppercase;">AI Local Correction</div>
              <div style="font-size:24px; font-weight:700; color:#D64545;">${(d.predicted_residual > 0 ? '+' : '')}${d.predicted_residual} mm</div>
              <div style="font-size:24px; color:#94A3B8; margin:8px 0;">=</div>
              <div style="font-size:11px; color:#4F8F3A; font-weight:700; text-transform:uppercase;">Panchayat-level Forecast</div>
              <div style="font-size:32px; font-weight:700; color:#4F8F3A;">${d.panchayat_forecast} mm</div>
              <div style="font-size:13px; font-weight:700; color:#17324D; margin-top:12px; background:#F5FFF5; border:1px solid #CDE2F0; padding:8px; border-radius:4px;">
                Panchayat: ${gp_name}
              </div>
            </div>`;"""

original = """      const d = await res.json();
      
      await tick('step4', 300);
      await tick('step5', 300);

      // In real scenario we'd update the dom with d, but we already pre-loaded it in render()
      // so it's perfectly in sync. We can re-assign just in case.
      
      document.getElementById('aiResultCard').style.opacity = '1';"""

code = code.replace(original, replacement)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Patched downscaling event listener.")
