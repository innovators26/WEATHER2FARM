import os
import re

FILE = r"src\dashboard\static\js\tabs\dashboard.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Change attributionControl: true to false
code = code.replace("attributionControl: true", "attributionControl: false")

# Remove attribution line in L.tileLayer
code = re.sub(r"attribution: '&copy; OpenStreetMap contributors',\n\s*", "", code)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Removed Leaflet attribution.")
