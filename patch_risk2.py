import os
FILE = r"src\dashboard\static\js\tabs\risk.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Replace the gp_name and block_name assignments
original = """  const gp_name  = state.panchayat ? state.panchayat.gp_name : 'Unknown';
  const block_name = state.panchayat && state.panchayat.block_name ? state.panchayat.block_name : null;
  const district_name = "Pune";

  // Loading state
  container.innerHTML = `
    <div style="display:flex;align-items:baseline;gap:16px;margin-bottom:24px;">
      <h1 style="font-size:32px;font-weight:700;color:var(--primary);">CROP RISK</h1>
      <span style="color:var(--text-muted);font-size:16px;">Panchayat-level agricultural risk assessment</span>
    </div>
    <div style="padding: 40px; text-align: center; color: var(--text-muted);">
      <i class="ph-fill ph-spinner ph-spin" style="font-size: 32px; margin-bottom: 12px;"></i>
      <div>Loading professional risk intelligence for ${gp_name}...</div>
    </div>
  `;

  const payload = {
    gp_code: state.panchayat ? state.panchayat.gp_code : "273397",
    gp_name: gp_name,
    crop: state.crop || "Onion",
    sowing_date: state.sowingDate || new Date().toISOString().split('T')[0]
  };"""

replacement = """  if (!state.panchayat) {
    container.innerHTML = `
      <div style="display:flex;align-items:baseline;gap:16px;margin-bottom:24px;">
        <h1 style="font-size:32px;font-weight:700;color:var(--primary);">CROP RISK</h1>
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
  const block_name = state.block || "Selected Block";
  const district_name = state.district || "Pune";

  // Loading state
  container.innerHTML = `
    <div style="display:flex;align-items:baseline;gap:16px;margin-bottom:24px;">
      <h1 style="font-size:32px;font-weight:700;color:var(--primary);">CROP RISK</h1>
      <span style="color:var(--text-muted);font-size:16px;">Panchayat-level agricultural risk assessment</span>
    </div>
    <div style="padding: 40px; text-align: center; color: var(--text-muted);">
      <i class="ph-fill ph-spinner ph-spin" style="font-size: 32px; margin-bottom: 12px;"></i>
      <div>Loading professional risk intelligence for ${gp_name}...</div>
    </div>
  `;

  // Always calculate default sowing date to 30 days ago to match the backend / advisory tab
  const today = new Date();
  const defaultSow = new Date(today);
  defaultSow.setDate(today.getDate() - 30);
  const finalSowingDate = state.sowingDate || defaultSow.toISOString().split('T')[0];

  const payload = {
    gp_code: gp_code,
    gp_name: gp_name,
    crop: state.crop || "Onion",
    sowing_date: finalSowingDate
  };"""

code = code.replace(original, replacement)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Patched risk.js top")
