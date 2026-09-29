import re

FILE = r"src\dashboard\static\js\tabs\risk.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# First, let's restore the first container.innerHTML if it got corrupted.
# Actually, I can just grab risk.js from a clean state or manually fix it.
# Let's see what the first container.innerHTML is now.
# Wait, let's just find the last container.innerHTML which is the actual render.
# I will find all instances of container.innerHTML
matches = list(re.finditer(r'container\.innerHTML = `.*?`;', code, re.DOTALL))
print(f"Found {len(matches)} container.innerHTML matches")

# Since the user specifically wants the ACTIVE RISK CONDITIONS to span the FULL width,
# and they want the grid to be:
# WATERLOGGING                     HIGH
# Assessment    Recommended Action   Trigger
#
# I will completely rewrite the LAST container.innerHTML, which is the final page render.
# Wait! If the first container.innerHTML is currently holding my 100-line layout from the previous prompt, it's completely breaking the loading state!
