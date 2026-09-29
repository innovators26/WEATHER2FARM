import os
FILE = r"src\dashboard\static\js\tabs\advisory.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

replacement1 = """  const today = new Date();
  const defaultSow = new Date(today);
  defaultSow.setDate(today.getDate() - 30);
  const defaultSowStr = state.sowingDate || defaultSow.toISOString().split('T')[0];
  const initialCrop = state.crop || 'Onion';"""

code = code.replace("""  const today = new Date();
  const defaultSow = new Date(today);
  defaultSow.setDate(today.getDate() - 30);
  const defaultSowStr = defaultSow.toISOString().split('T')[0];""", replacement1)

code = code.replace('<select id="advCrop" style="', '<select id="advCrop" data-value="${initialCrop}" style="')

replacement3 = """
  // Sync to state without full re-render
  document.getElementById('advCrop').value = initialCrop;
  
  // NOTE: updateState must be imported at top level, but it's not. 
  // Let's use window or just dynamically import it, or since state is passed in, maybe we don't have it.
  // Actually, we can import updateState at the top of advisory.js!
"""

if "import { updateState }" not in code:
    code = code.replace("import { t } from '../i18n.js';", "import { t } from '../i18n.js';\nimport { updateState } from '../state.js';")

listener_patch = """
  document.getElementById('advCrop').addEventListener('change', e => {
      updateState({ crop: e.target.value });
  });
  document.getElementById('advDate').addEventListener('change', e => {
      updateState({ sowingDate: e.target.value });
      
"""

code = code.replace("""  document.getElementById('advDate').addEventListener('change', e => {""", listener_patch)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Patched advisory.js")
