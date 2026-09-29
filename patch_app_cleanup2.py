import os
import re

FILE = r"src\dashboard\app.py"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

start_idx = code.find("async def chat_with_bot(req: ChatRequest):")

# Cut off everything from the first occurrence to the end.
code = code[:start_idx]

# Now append the correct version.
correct_func = """async def chat_with_bot(req: ChatRequest):
    print("[CHAT] Request received")
    print(f"[CHAT] Panchayat: {req.panchayat_id}")
    print(f"[CHAT] Crop: {req.crop}")
    print(f"[CHAT] Question: {req.message}")
    print("[CHAT] Building Weather2Farm context")
    
    if not GROQ_API_KEY:
        return {"success": False, "error": "AI assistant is not configured."}
        
    try:
        from src.advisory.rule_engine import evaluate_advanced_advisory, get_crop_stage
        import datetime
        import json
        
        try:
            sow = datetime.date.fromisoformat(req.sowing_date)
            das = (datetime.date.today() - sow).days
        except Exception:
            das = 30
        if das < 0: das = 0
        stage_enum = get_crop_stage(req.crop, das)

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
            "forecast": [],
            "downscaling": {
                "block_rainfall_mm": float(pan_props.get("block_forecast_rain", 0)),
                "predicted_residual_mm": float(pan_props.get("residual_rain", 0)),
                "panchayat_rainfall_mm": rain
            }
        }

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
        
        try:
            bulletin = evaluate_advanced_advisory(
                panchayat_id=req.panchayat_id,
                panchayat_name=gp_name,
                crop_name=req.crop,
                das=das,
                current_rain=rain,
                current_temp=temp,
                current_rh=rh,
                current_wind=wind,
                forecast_7d=context_obj["forecast"]
            )
            context_obj["advisory"] = {
                "severity": bulletin.overall_severity.value,
                "reason": bulletin.alert_reason,
                "recommendations": bulletin.recommended_actions,
                "avoid": bulletin.avoid_actions
            }
            context_obj["risk"] = [
                {"risk_name": r.risk_name, "level": r.level, "reason": r.reason} for r in bulletin.risks
            ]
        except Exception as e:
            context_obj["advisory"] = {"error": str(e)}
            
        session_key = f"{req.panchayat_id}_{req.crop}" 
        if session_key not in chat_history:
            chat_history[session_key] = []
            
        history = chat_history[session_key]
        
        system_prompt = f\"\"\"You are the Weather2Farm agricultural advisory assistant.

Answer the farmer's question using ONLY the Weather2Farm context supplied to you.

Use:
- Panchayat location
- crop
- crop growth stage
- current weather
- Panchayat-level forecast
- 7-day forecast
- rainfall trend
- Weather2Farm agricultural rules

Give practical, concise, crop-specific answers.

When the farmer asks whether they should irrigate, spray, sow, harvest, or perform another farm operation, evaluate the current and forecast weather before answering.

Do not invent weather values.
Do not invent rainfall.
Do not claim that rainfall will occur unless it exists in the supplied forecast.

If the available data is insufficient to make a reliable recommendation, clearly say that the available Weather2Farm data is insufficient.
Do not tell the farmer to click Generate Advisory.
Generate Advisory is independent of this conversation.
Answer naturally like an agricultural assistant, not like a software system. Language: {req.language}.

For actionable questions:
1. Give the direct answer first.
2. Explain the weather/crop reason.
3. Give a practical action.
4. Mention an important condition or caution if relevant.

Keep answers concise but useful.

CURRENT CONTEXT:
{json.dumps(context_obj, indent=2)}
\"\"\"
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-10:]:
            messages.append(msg)
            
        messages.append({"role": "user", "content": req.message})

        print("[CHAT] Calling Groq")
        
        try:
            response = client.chat.completions.create(
                messages=messages,
                model=GROQ_MODEL,
                temperature=0.3,
                max_tokens=500
            )
            answer = response.choices[0].message.content
            print("[CHAT] Groq response received")
            print("[CHAT] Sending response to frontend")
            
            history.append({"role": "user", "content": req.message})
            history.append({"role": "assistant", "content": answer})
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
            if "429" in str(e) or "rate_limit" in str(e).lower():
                return {"success": False, "error": "AI assistant is temporarily busy. Please try again shortly."}
            return {"success": False, "error": "AI assistant is temporarily unavailable."}
            
    except Exception as e:
        print('GROQ ERROR:', e)
        return {"success": False, "error": "AI assistant is temporarily unavailable."}
"""

code += correct_func

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Cleaned up duplicated chat_with_bot.")
