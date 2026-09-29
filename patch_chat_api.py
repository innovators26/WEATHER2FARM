import os
import sys

APP_FILE = r"src\dashboard\app.py"

with open(APP_FILE, "r", encoding="utf-8") as f:
    code = f.read()

if "from groq import Groq" not in code:
    code = code.replace("from fastapi import FastAPI, HTTPException", "from fastapi import FastAPI, HTTPException\nfrom groq import Groq")

chat_api_code = """
# ─── CHATBOT INTEGRATION ─────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    panchayat_id: str
    crop: str
    sowing_date: str
    language: str

# Keep a simple in-memory session history (for production, use redis or DB)
# Key: panchayat_id + crop
chat_history = {}

@app.post("/api/chat")
async def chat_with_bot(req: ChatRequest):
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        return {"success": False, "error": "AI assistant is not configured."}

    client = Groq(api_key=groq_api_key)
    model_name = os.getenv("GROQ_MODEL", "llama3-8b-8192")

    from src.advisory.rule_engine import get_crop_stage
    import datetime
    
    # Context building
    try:
        sow = datetime.date.fromisoformat(req.sowing_date)
        das = (datetime.date.today() - sow).days
    except Exception:
        das = 30
    if das < 0: das = 0
    stage_enum = get_crop_stage(req.crop, das)

    # Fetch weather data for panchayat
    geojson_path = os.path.join(STATIC_DIR, "data", "pune_panchayats_web.geojson")
    pan_props = None
    if os.path.exists(geojson_path):
        import json
        with open(geojson_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for feat in data.get("features", []):
                if str(feat.get("properties", {}).get("gp_code")) == str(req.panchayat_id):
                    pan_props = feat["properties"]
                    break

    if not pan_props:
        return {"success": False, "error": "Weather data is currently unavailable for this Panchayat."}

    rain = float(panchayat_rain := pan_props.get("downscaled_rain", 0))
    temp = float(pan_props.get("tmax", 0))
    rh = float(pan_props.get("rh", 0))
    wind = float(panchayat_wind := pan_props.get("wind", 0))
    block_name = pan_props.get("block_name", "Unknown Block")
    gp_name = pan_props.get("gp_name", "Unknown Panchayat")

    context_obj = {
        "location": {
            "district": "Pune",
            "block": block_name,
            "panchayat": gp_name
        },
        "crop": {
            "name": req.crop,
            "sowing_date": req.sowing_date,
            "das": das,
            "stage": stage_enum.value
        },
        "weather": {
            "rainfall_mm": rain,
            "temperature_c": temp,
            "humidity_percent": rh,
            "wind_kmh": wind
        },
        "forecast": [], # simplified
        "downscaling": {
            "block_rainfall_mm": float(pan_props.get("block_forecast_rain", 0)),
            "predicted_residual_mm": float(pan_props.get("residual_rain", 0)),
            "panchayat_rainfall_mm": rain
        }
    }

    # Add 7-day forecast
    base_rain = float(pan_props.get("downscaled_rain", 0))
    base_temp = float(pan_props.get("tmax", 25.0))
    elevation = float(pan_props.get("elevation_mean", 500))
    dist_coast = float(pan_props.get("dist_to_coast_km", 100))
    forest = float(pan_props.get("forest_pct", 10))
    rain_persistence = 0.9 if (elevation > 700 or dist_coast < 70) else 0.6
    temp_modulation = 0.1 if forest > 30 else 0.25
    today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
    
    for i in range(7):
        target_date = today + datetime.timedelta(days=i)
        step_rain = round(base_rain * (rain_persistence ** i), 1)
        step_temp = round(base_temp + (i * temp_modulation), 1)
        context_obj["forecast"].append({
            "date": target_date.strftime("%Y-%m-%d"),
            "rain": step_rain,
            "temp": step_temp
        })

    session_key = f"{req.panchayat_id}_{req.crop}"
    if session_key not in chat_history:
        chat_history[session_key] = []
        
    history = chat_history[session_key]
    
    system_prompt = f\"\"\"You are the Weather2Farm agricultural weather assistant.
You answer questions using only the Weather2Farm context provided by the backend.
Never invent weather values, forecast values, Panchayat information, crop information, model results, risk thresholds, or measurements.
The Weather2Farm XGBoost model is responsible for Panchayat-level weather downscaling.
The Weather2Farm crop-risk engine is responsible for risk calculation.
The Weather2Farm advisory engine is responsible for agricultural rule-based recommendations.
Your role is to explain these results clearly and answer farmer questions conversationally in language '{req.language}'.
If required information is unavailable, explicitly say that it is unavailable.
Never guess missing weather data.
When discussing weather, mention the relevant Panchayat and forecast period where appropriate.
When discussing crops, consider: selected crop, sowing date, DAS, crop growth stage, current weather, forecast, crop risk, existing advisory rules.
Do not claim certainty beyond the supplied data.
Give concise, practical answers.
Do not fabricate fertilizer dosage, pesticide dosage, irrigation quantity, disease diagnosis, or other technical recommendations unless that information is explicitly present in the supplied Weather2Farm agricultural rules.
This assistant provides decision support and does not replace local agricultural expertise.

CURRENT CONTEXT:
{json.dumps(context_obj, indent=2)}
\"\"\"
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Append last 10 messages from history
    for msg in history[-10:]:
        messages.append(msg)
        
    messages.append({"role": "user", "content": req.message})

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=500
        )
        answer = response.choices[0].message.content
        
        # update history
        history.append({"role": "user", "content": req.message})
        history.append({"role": "assistant", "content": answer})
        
        # trim history
        if len(history) > 20:
            chat_history[session_key] = history[-20:]

        return {
            "success": True,
            "answer": answer,
            "language": req.language,
            "panchayat": gp_name,
            "crop": req.crop,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    except Exception as e:
        if "rate_limit" in str(e).lower() or "429" in str(e):
            return {"success": False, "error": "AI assistant is temporarily busy. Please try again shortly."}
        return {"success": False, "error": "AI assistant is temporarily unavailable."}
"""

if "class ChatRequest" not in code:
    code = code.replace("if __name__ == \"__main__\":", chat_api_code + "\nif __name__ == \"__main__\":")
    with open(APP_FILE, "w", encoding="utf-8") as f:
        f.write(code)
    print("Chat API inserted.")
else:
    print("Chat API already exists.")
