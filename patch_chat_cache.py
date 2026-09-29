import re

FILE = r"src\dashboard\static\js\app.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Export state to window unconditionally for the chatbot functions
code = code.replace("import { state, updateState, loadState, subscribe } from './state.js';",
                    "import { state, updateState, loadState, subscribe } from './state.js';\nwindow.__state_cache = state;\nsubscribe(s => window.__state_cache = s);")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Exported __state_cache reliably")
