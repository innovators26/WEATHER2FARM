import re

FILE = r"src\dashboard\static\js\app.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Add subscription to keep chatbot context synced
subscribe_logic = """
    // Keep context updated
    subscribe((s) => {
        if (locSpan) {
            locSpan.innerText = (s.panchayat && s.panchayat.gp_name) ? s.panchayat.gp_name : 'None Selected';
        }
    });
"""
code = code.replace("locSpan.innerText = panchayat;", "locSpan.innerText = panchayat;\n    " + subscribe_logic)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Added state subscription for global chatbot context")
