import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class AdvisorySeverity(str, Enum):
    NORMAL = "NORMAL"
    WATCH = "WATCH"
    WARNING = "WARNING"
    SEVERE = "SEVERE"

class CropStage(str, Enum):
    SOWING = "stage_sowing"
    VEGETATIVE = "stage_vegetative"
    FLOWERING = "stage_flowering"
    FRUITING = "stage_fruiting"
    MATURITY = "stage_maturity"
    HARVESTING = "stage_harvesting"

class ActionItem(BaseModel):
    action: str
    why: str
    when: str

class CropRisk(BaseModel):
    risk_name: str
    level: str
    reason: str

class AdvancedAdvisory(BaseModel):
    crop_condition: str
    weather_impact: str
    trend_summary: str
    risks: List[CropRisk]
    actions: List[ActionItem]
    avoid: List[str]
    next_7_days: str
    overall_severity: AdvisorySeverity
    alert_reason: str
    params: Dict[str, Any]

CROP_THRESHOLDS = {
    "Onion": {"stages": [10, 40, 70, 90, 110], "temp_opt": (15, 25), "temp_max": 35, "water_opt_mm": (20, 50), "waterlogging_sensitive": True},
    "Rice": {"stages": [15, 45, 80, 110, 130], "temp_opt": (22, 32), "temp_max": 38, "water_opt_mm": (100, 250), "waterlogging_sensitive": False},
    "Wheat": {"stages": [15, 50, 85, 110, 130], "temp_opt": (15, 25), "temp_max": 32, "water_opt_mm": (20, 40), "waterlogging_sensitive": True},
    "Maize": {"stages": [10, 45, 75, 100, 120], "temp_opt": (20, 30), "temp_max": 35, "water_opt_mm": (30, 60), "waterlogging_sensitive": True},
    "Cotton": {"stages": [15, 50, 90, 130, 160], "temp_opt": (22, 32), "temp_max": 38, "water_opt_mm": (25, 50), "waterlogging_sensitive": True},
    "Sugarcane": {"stages": [40, 120, 200, 280, 365], "temp_opt": (25, 33), "temp_max": 38, "water_opt_mm": (50, 100), "waterlogging_sensitive": False},
    "Tomato": {"stages": [15, 45, 75, 100, 130], "temp_opt": (18, 28), "temp_max": 35, "water_opt_mm": (20, 40), "waterlogging_sensitive": True}
}

def get_crop_stage(crop: str, das: int) -> CropStage:
    if crop not in CROP_THRESHOLDS:
        crop = "Wheat"
    st = CROP_THRESHOLDS[crop]["stages"]
    if das <= st[0]: return CropStage.SOWING
    if das <= st[1]: return CropStage.VEGETATIVE
    if das <= st[2]: return CropStage.FLOWERING
    if das <= st[3]: return CropStage.FRUITING
    if das <= st[4]: return CropStage.MATURITY
    return CropStage.HARVESTING

def evaluate_advanced_advisory(
    panchayat_id: str,
    panchayat_name: str,
    crop_name: str,
    das: int,
    current_rain: float,
    current_temp: float,
    current_rh: float,
    current_wind: float,
    forecast_7d: List[Dict[str, float]]
) -> AdvancedAdvisory:
    
    stage = get_crop_stage(crop_name, das)
    total_rain = sum(d.get("rain", 0) for d in forecast_7d)
    max_temp = max(d.get("temp", 0) for d in forecast_7d)
    rainy_days = sum(1 for d in forecast_7d if d.get("rain", 0) > 2.5)
    
    crop_info = CROP_THRESHOLDS.get(crop_name, CROP_THRESHOLDS["Wheat"])
    
    params = {
        "crop_name": f"crop_{crop_name.lower()}",
        "stage": stage.value,
        "das": das,
        "current_rain": f"{current_rain:.1f}",
        "current_temp": f"{current_temp:.1f}",
        "current_rh": f"{current_rh:.1f}",
        "current_wind": f"{current_wind:.1f}",
        "total_rain": f"{total_rain:.1f}",
        "max_temp": f"{max_temp:.1f}",
        "rainy_days": rainy_days,
        "temp_max": crop_info["temp_max"],
        "water_opt": crop_info["water_opt_mm"][0]
    }
    
    severity = AdvisorySeverity.NORMAL
    alert_reason = "alert_reason_optimal"
    
    if total_rain > 60 or current_temp > crop_info["temp_max"] + 3:
        severity = AdvisorySeverity.SEVERE
        alert_reason = "alert_reason_severe"
    elif total_rain > 30 or current_wind > 25 or current_temp > crop_info["temp_max"]:
        severity = AdvisorySeverity.WARNING
        alert_reason = "alert_reason_warning"
    elif current_rh > 85 or total_rain < 5:
        severity = AdvisorySeverity.WATCH
        alert_reason = "alert_reason_watch"
    
    if rainy_days >= 4:
        trend = "trend_wetting"
    elif total_rain < 5:
        trend = "trend_drying"
    else:
        trend = "trend_stable"
        
    if max_temp > crop_info["temp_max"]:
        trend += "_heat"

    risks = []
    actions = []
    avoids = []
    
    if total_rain > 30 or current_rain > 10:
        actions.append(ActionItem(action="action_halt_irrigation", why="why_heavy_rain", when="timing_24h"))
        if crop_info["waterlogging_sensitive"]:
            risks.append(CropRisk(risk_name="risk_waterlogging", level="HIGH", reason="reason_waterlogging"))
    elif total_rain < 5 and current_rain < 2:
        actions.append(ActionItem(action="action_critical_irrigation", why="why_dry_forecast", when="timing_now"))
        risks.append(CropRisk(risk_name="risk_water_stress", level="MODERATE", reason="reason_prolonged_dry"))
    else:
        actions.append(ActionItem(action="action_maintain_moisture", why="why_moderate_rain", when="timing_3_7d"))

    if current_wind > 15:
        actions.append(ActionItem(action="action_postpone_spray", why="why_high_wind", when="timing_24h"))
        avoids.append("avoid_high_wind_spray")
    elif current_rh > 85:
        actions.append(ActionItem(action="action_fungicide", why="why_high_humidity", when="timing_24h"))
        risks.append(CropRisk(risk_name="risk_disease", level="MODERATE", reason="reason_high_humidity"))
    else:
        actions.append(ActionItem(action="action_routine_scouting", why="why_stable_humidity", when="timing_3_7d"))

    if total_rain > 40:
        actions.append(ActionItem(action="action_delay_fertilizer", why="why_rain_leaching", when="timing_3_7d"))
        avoids.append("avoid_surface_fertilizer")
    elif stage == CropStage.VEGETATIVE:
        actions.append(ActionItem(action="action_nitrogen_top", why="why_vegetative_nitrogen", when="timing_3_7d"))
    elif stage in [CropStage.FLOWERING, CropStage.FRUITING]:
        actions.append(ActionItem(action="action_k_p_spray", why="why_flowering_spray", when="timing_now"))
    else:
        actions.append(ActionItem(action="action_withhold_n", why="why_late_nitrogen", when="timing_now"))

    if current_temp > crop_info["temp_max"]:
        actions.append(ActionItem(action="action_organic_mulch", why="why_extreme_temp", when="timing_now"))
        risks.append(CropRisk(risk_name="risk_heat_stress", level="HIGH", reason="reason_extreme_temp"))
    elif total_rain > 20 and crop_info["waterlogging_sensitive"]:
        actions.append(ActionItem(action="action_clear_drainage", why="why_waterlogging_sensitive", when="timing_24h"))
    else:
        actions.append(ActionItem(action="action_weeding", why="why_weeding", when="timing_3_7d"))

    if stage == CropStage.SOWING:
        actions.append(ActionItem(action="action_seedbed", why="why_germination", when="timing_now"))
    elif stage == CropStage.VEGETATIVE:
        actions.append(ActionItem(action="action_monitor_tillering", why="why_yield_potential", when="timing_3_7d"))
    elif stage == CropStage.FLOWERING:
        actions.append(ActionItem(action="action_avoid_water_stress", why="why_blossom_drop", when="timing_now"))
    elif stage == CropStage.FRUITING:
        actions.append(ActionItem(action="action_monitor_borer", why="why_pest_attraction", when="timing_3_7d"))
    elif stage == CropStage.MATURITY:
        actions.append(ActionItem(action="action_prep_harvest", why="why_phys_maturity", when="timing_3_7d"))
    elif stage == CropStage.HARVESTING:
        if total_rain > 10:
            actions.append(ActionItem(action="action_postpone_harvest", why="why_wet_quality", when="timing_3_7d"))
            avoids.append("avoid_exposed_produce")
        else:
            actions.append(ActionItem(action="action_proceed_harvest", why="why_dry_storage", when="timing_now"))

    crop_condition = "cond_stage"
    
    weather_impact = "impact_temp_" + ("exceeds" if current_temp > crop_info["temp_max"] else "normal")
    weather_impact += "_rain_" + ("influence" if total_rain > 0 else "lack")

    next_7_days = "next7_"
    if total_rain > 30: next_7_days += "wet"
    elif total_rain < 5: next_7_days += "dry"
    else: next_7_days += "favorable"

    return AdvancedAdvisory(
        crop_condition=crop_condition,
        weather_impact=weather_impact,
        trend_summary=trend,
        risks=risks,
        actions=actions,
        avoid=avoids,
        next_7_days=next_7_days,
        overall_severity=severity,
        alert_reason=alert_reason,
        params=params
    )
