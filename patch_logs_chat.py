import os

FILE = r"src\dashboard\app.py"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# I will replace the current logging setup in chat_with_bot
# First, insert start logs at the very beginning of chat_with_bot
start_idx = code.find("async def chat_with_bot(req: ChatRequest):")
if start_idx != -1:
    body_start = code.find("\n", start_idx) + 1
    new_start_logs = """    print("[CHAT] Request received")\n    print(f"[CHAT] Panchayat: {req.panchayat_id}")\n    print(f"[CHAT] Crop: {req.crop}")\n    print(f"[CHAT] Question: {req.message}")\n    print("[CHAT] Building Weather2Farm context")\n"""
    # Insert new start logs if not already there
    if "[CHAT] Request received" not in code:
        code = code[:body_start] + new_start_logs + code[body_start:]

# Remove old logs
code = code.replace('    print(f"[CHAT] Panchayat: {gp_name}")\n', '')
code = code.replace('    print(f"[CHAT] Crop: {req.crop}")\n', '')
code = code.replace('    print(f"[CHAT] Question: {req.message}")\n', '')
code = code.replace('    print(f"[CHAT] Context built: YES")\n', '')
code = code.replace('    print(f"[CHAT] Calling Groq:")\n', '    print("[CHAT] Calling Groq")\n')

# Find where answer is printed
old_resp_log = "        print(f\"[CHAT] Groq response received: {answer[:50].encode('ascii', 'ignore').decode('ascii')}...\")"
new_resp_log = "        print(\"[CHAT] Groq response received\")\n        print(\"[CHAT] Sending response to frontend\")"
code = code.replace(old_resp_log, new_resp_log)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Patched app.py logging.")
