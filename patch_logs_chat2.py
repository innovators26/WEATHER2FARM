import os

FILE = r"src\dashboard\app.py"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Make sure we have the exact logs
start_idx = code.find("async def chat_with_bot(req: ChatRequest):")
body_start = code.find("\n", start_idx) + 1

# I will just regex replace the whole block until try:
import re
code = re.sub(r'async def chat_with_bot\(req: ChatRequest\):.*?try:', 
    r'''async def chat_with_bot(req: ChatRequest):
    session_key = f"{req.panchayat_id}_{req.crop}"
    
    print("[CHAT] Request received")
    print(f"[CHAT] Panchayat: {req.panchayat_id}")
    print(f"[CHAT] Crop: {req.crop}")
    print(f"[CHAT] Question: {req.message}")
    print("[CHAT] Building Weather2Farm context")
    
    # get history
    history = chat_history.get(session_key, [])
    
    # -------------------------------------------------------------------------
    # BUILD WEATHER2FARM CONTEXT
    # -------------------------------------------------------------------------
    geojson_path = os.path.join(STATIC_DIR, "data", "pune_panchayats_web.geojson")
    pan_props = None
    if os.path.exists(geojson_path):
        with open(geojson_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for feat in data.get("features", []):
                if str(feat.get("properties", {}).get("gp_code")) == str(req.panchayat_id):
                    pan_props = feat["properties"]
                    break
                    
    if not pan_props:
        return {"success": False, "error": "Weather data is currently unavailable for this Panchayat."}
        
    gp_name = pan_props.get("gp_name", "Unknown")
    
    context_str = f"Location: {gp_name}, Block {pan_props.get('block_name')}, District Pune\\n"
    context_str += f"Crop: {req.crop}, Sowing Date: {req.sowing_date}\\n"
    context_str += f"Current Weather: Rain {pan_props.get('downscaled_rain')}mm, Temp {pan_props.get('tmax')}C, Humidity {pan_props.get('rh')}%\\n"
    context_str += f"AI Panchayat Forecast vs IMD Block Forecast: {pan_props.get('downscaled_rain')}mm vs {pan_props.get('block_forecast_rain')}mm\\n"
    
    messages = [
        {"role": "system", "content": "You are Weather2Farm AI, an expert agricultural assistant. Answer the user's questions clearly based strictly on the current weather and forecast context provided below. Keep your answers brief and practical. Do not use markdown headers.\\n\\nCONTEXT:\\n" + context_str},
    ]
    
    messages.extend(history)
    
    messages.append({"role": "user", "content": req.message})

    print("[CHAT] Calling Groq")
    
    try:''', code, flags=re.DOTALL)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Fixed chat logging.")
