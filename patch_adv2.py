import os
FILE = r"src\dashboard\static\js\tabs\advisory.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

replacement = """  document.getElementById('advCrop').value = initialCrop;

  document.getElementById('advCrop').addEventListener('change', e => {
      updateState({ crop: e.target.value });
  });

  document.getElementById('advDate').addEventListener('change', e => {
      updateState({ sowingDate: e.target.value });
      computeDAS();
  });
"""

code = code.replace("document.getElementById('advDate').addEventListener('change', computeDAS);", replacement)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Patched event listeners")
