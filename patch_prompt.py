import os

APP_FILE = r"src\dashboard\app.py"
with open(APP_FILE, "r", encoding="utf-8") as f:
    code = f.read()

import re

# Find the start of the string
start_str = 'system_prompt = f"""'
start_idx = code.find(start_str)

if start_idx != -1:
    end_idx = code.find('"""', start_idx + len(start_str))
    if end_idx != -1:
        end_idx += 3
        new_prompt = '''system_prompt = f"""You are the Weather2Farm agricultural advisory assistant.

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
"""'''
        code = code[:start_idx] + new_prompt + code[end_idx:]
        with open(APP_FILE, "w", encoding="utf-8") as f:
            f.write(code)
        print("Patched system prompt.")
    else:
        print("Could not find end of system prompt")
else:
    print("Could not find start of system prompt")
