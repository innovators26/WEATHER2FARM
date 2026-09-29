import os
import re

FILE = r"src\dashboard\static\css\style.css"
with open(FILE, "r", encoding="utf-8") as f:
    css = f.read()

# Fix flex overflow
css = css.replace('.dash-left { flex: 0 0 54%; display: flex; flex-direction: column; gap: 20px; }',
                  '.dash-left { flex: 1.2; min-width: 300px; display: flex; flex-direction: column; gap: 20px; }')
css = css.replace('.dash-right { flex: 0 0 46%; display: flex; flex-direction: column; }',
                  '.dash-right { flex: 1; min-width: 300px; display: flex; flex-direction: column; gap: 20px; }')
css = css.replace('.dash-layout { display: flex; gap: 20px; margin-bottom: 20px; }',
                  '.dash-layout { display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap; }')

# Fix responsive layout
css += "\n@media (max-width: 1024px) {\n  .dash-layout { flex-direction: column; }\n}\n"

with open(FILE, "w", encoding="utf-8") as f:
    f.write(css)

print("Patched style.css flex layout overflow")
