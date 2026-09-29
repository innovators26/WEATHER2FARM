import os

APP_FILE = r"src\dashboard\app.py"
with open(APP_FILE, "r", encoding="utf-8") as f:
    code = f.read()

replacement = """
    # Include Advisory and Risk in Context
    try:
        from src.advisory.rule_engine import evaluate_advanced_advisory
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

    session_key = f"{req.panchayat_id}_{req.crop}" """

if 'context_obj["advisory"]' not in code:
    code = code.replace('session_key = f"{req.panchayat_id}_{req.crop}"', replacement)
    
    with open(APP_FILE, "w", encoding="utf-8") as f:
        f.write(code)
    print("Patched context with advisory and risk.")
else:
    print("Already patched context.")
