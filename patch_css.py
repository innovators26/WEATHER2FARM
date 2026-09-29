import os
import re

FILE = r"src\dashboard\static\css\style.css"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# I will just match and remove the specific lines since they seem to be one-liners mostly
patterns_to_remove = [
    r"\.adv-box \{.*?\n",
    r"\.adv-box ul \{.*?\n",
    r"\.val-badge \{.*?\n",
    r"\.val-grid \{.*?\n",
    r"\.val-item \.val-label \{.*?\n",
    r"\.val-item \.val-num \{.*?\n",
    r"\.fb-btns \{.*?\n",
    r"\.fb-btns button \{.*?\n",
    r"\.fb-intensity \{.*?\n",
    r"\.btn-intensity \{.*?\n",
    r"\.adv-crop-info \{.*?\n",
    r"\.adv-img \{.*?\n"
]

for p in patterns_to_remove:
    code = re.sub(p, "", code)

# Let me check if there is any other related css block
code = re.sub(r"\.fb-btns \.btn-yes \{.*?\}\n?", "", code, flags=re.DOTALL)
code = re.sub(r"\.fb-btns \.btn-no \{.*?\}\n?", "", code, flags=re.DOTALL)
code = re.sub(r"\.val-item \{.*?\}\n?", "", code, flags=re.DOTALL)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Cleaned CSS.")
