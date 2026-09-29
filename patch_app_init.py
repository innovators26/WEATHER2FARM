import re

FILE = r"src\dashboard\static\js\app.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Let's ensure initGlobalChatbot is called unconditionally!
# Sometimes DOMContentLoaded has already fired by the time module script runs.
# We can just call it immediately!
code = code.replace("function initGlobalChatbot() {", """
function initGlobalChatbot() {
    console.log("initGlobalChatbot called");""")

code = code.replace("      if (!btn || !popup) return;", """      if (!btn || !popup) {
          console.error("Chatbot DOM elements missing");
          return;
      }
      console.log("Chatbot DOM elements found, adding listeners");""")

# Remove the call from DOMContentLoaded just in case, and call it globally at the end of the file.
code = code.replace("    initGlobalChatbot();\n  });", "  });")

call_at_end = """
// Initialize chatbot directly (modules are deferred, so DOM is ready)
setTimeout(() => {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initGlobalChatbot);
    } else {
        initGlobalChatbot();
    }
}, 100);
"""

code += call_at_end

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Patched app.js to ensure chatbot initialization runs safely")
