import os
import json
import re

with open("src/dashboard/app.py", "r", encoding="utf-8") as f:
    code = f.read()

# Add imports if missing
if "from pydantic import BaseModel" not in code:
    code = code.replace("from fastapi import FastAPI, HTTPException", "from fastapi import FastAPI, HTTPException\nfrom pydantic import BaseModel\nfrom typing import Optional")

if "from src.advisory.rule_engine import evaluate_panchayat_advisories" not in code:
    code = code.replace("import pandas as pd", "import pandas as pd\nfrom src.advisory.rule_engine import evaluate_panchayat_advisories, CropStage")

# Define endpoint payloads
models = """
class AdvisoryRequest(BaseModel):
    gp_code: str
    crop: str
    sowing_date: str
    gp_name: Optional[str] = "Selected Panchayat"
    block_name: Optional[str] = "Selected Block"

@app.post("/api/advisory")
async def get_advisory(req: AdvisoryRequest):
    # We mock the weather inputs since we don't have a live DB yet, but we run the REAL rule engine
    # In a real scenario, we'd query the DB for today's forecast for this gp_code
    b = evaluate_panchayat_advisories(
        panchayat_id=req.gp_code,
        panchayat_name=req.gp_name,
        block_name=req.block_name,
        forecast_date=req.sowing_date, # using this just as a date string
        rainfall_mm=62.5,  # Dummy weather inputs to trigger the real rules for prototype
        rainfall_3day_mm=95.0,
        tmax_c=28.5,
        tmin_c=21.0,
        rh_pct=88.0,
        wind_kmh=42.0,
        crop_stage=CropStage.VEGETATIVE,
        crop_name=req.crop
    )
    return {
        "severity": b.overall_status.value,
        "alert_title": b.overall_status.name,
        "stage": b.crop_stage.value,
        "weather": {
            "rain": b.rainfall_mm,
            "temp": b.tmax_c,
            "humidity": b.rh_pct,
            "wind": b.wind_kmh
        },
        "actions": [adv.action_item for adv in b.advisories],
        "rules_applied": [adv.rule_name for adv in b.advisories]
    }

@app.get("/api/geo/hierarchy")
async def get_geo_hierarchy():
    panchayats_file = os.path.join(STATIC_DIR, "data", "pune_panchayats_web.geojson")
    if not os.path.exists(panchayats_file):
        return {}
    with open(panchayats_file, "r") as f:
        data = json.load(f)
    
    hierarchy = {"Pune": {}}
    for feature in data.get("features", []):
        props = feature["properties"]
        block = props.get("block_name")
        gp_code = props.get("gp_code")
        gp_name = props.get("gp_name")
        
        if block not in hierarchy["Pune"]:
            hierarchy["Pune"][block] = []
        hierarchy["Pune"][block].append({"gp_code": gp_code, "gp_name": gp_name})
    
    # Sort for consistency
    for block in hierarchy["Pune"]:
        hierarchy["Pune"][block].sort(key=lambda x: x["gp_name"])
        
    return hierarchy
"""

if "@app.post(\"/api/advisory\")" not in code:
    code = code.replace("if __name__ == \"__main__\":", models + "\n\nif __name__ == \"__main__\":")

with open("src/dashboard/app.py", "w", encoding="utf-8") as f:
    f.write(code)
print("app.py patched")
