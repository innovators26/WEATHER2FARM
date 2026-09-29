import os
APP_FILE = r"src\dashboard\app.py"
with open(APP_FILE, "r", encoding="utf-8") as f:
    code = f.read()

log_str1 = """    print(f"[CHAT] Panchayat: {gp_name}")
    print(f"[CHAT] Crop: {req.crop}")
    print(f"[CHAT] Question: {req.message}")
    print(f"[CHAT] Context built: YES")
    print(f"[CHAT] Calling Groq:")
    
    try:"""

code = code.replace("    try:\n        response = client.chat.completions.create(", log_str1 + "\n        response = client.chat.completions.create(")

log_str2 = """        answer = response.choices[0].message.content
        print(f"[CHAT] Groq response received: {answer[:50]}...")"""

code = code.replace("        answer = response.choices[0].message.content", log_str2)

with open(APP_FILE, "w", encoding="utf-8") as f:
    f.write(code)
print("Patched logging.")
