import re

FILE = r"src\dashboard\static\js\app.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Fix the bug
code = code.replace("""        // Update context label whenever opened
        if (chatbotOpen) {
            const st = state;
            const panchayat = (st.panchayat && st.panchayat.gp_name) ? st.panchayat.gp_name : 'None Selected';
            locSpan.innerText = panchayat;
    
    // Keep context updated
    subscribe((s) => {
        if (locSpan) {
            locSpan.innerText = (s.panchayat && s.panchayat.gp_name) ? s.panchayat.gp_name : 'None Selected';
        }
    });
            input.focus();
        }""", """        // Update context label whenever opened
        if (chatbotOpen) {
            const st = state;
            const panchayat = (st.panchayat && st.panchayat.gp_name) ? st.panchayat.gp_name : 'None Selected';
            locSpan.innerText = panchayat;
            input.focus();
        }""")

# Add subscribe safely outside
code = code.replace("if (!btn || !popup) return;", """if (!btn || !popup) return;

    // Keep context updated
    subscribe((s) => {
        if (locSpan) {
            locSpan.innerText = (s.panchayat && s.panchayat.gp_name) ? s.panchayat.gp_name : 'None Selected';
        }
    });
    
    // Initial setup
    const st = state;
    locSpan.innerText = (st.panchayat && st.panchayat.gp_name) ? st.panchayat.gp_name : 'None Selected';
""")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Fixed state subscription for global chatbot")
