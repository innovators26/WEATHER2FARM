import os

FILE = r"src\dashboard\static\css\style.css"
with open(FILE, "r", encoding="utf-8") as f:
    css = f.read()

# Make table styles strict
css = css.replace('th { background: var(--background); font-size: var(--font-label); font-weight: 600; color: var(--muted); padding: var(--space-3) var(--space-4); text-align: left; border-bottom: 1px solid var(--border); white-space: nowrap; }',
                  'th { background: var(--background) !important; font-size: var(--font-label) !important; font-weight: 600 !important; color: var(--muted) !important; padding: var(--space-3) var(--space-4) !important; text-align: left; border-bottom: 1px solid var(--border) !important; white-space: nowrap; height: 44px !important; }')

css = css.replace('td { padding: var(--space-3) var(--space-4); border-bottom: 1px solid var(--border); font-size: var(--font-body); color: var(--text); height: 44px; }',
                  'td { padding: var(--space-3) var(--space-4) !important; border-bottom: 1px solid var(--border) !important; font-size: var(--font-body) !important; color: var(--text) !important; height: 48px !important; vertical-align: middle; }')

# Override any hardcoded card styles that might have been missed
css += "\n/* Catch-all for inline styles */\n"
css += "[style*='font-size:'] { font-family: 'Inter', system-ui, sans-serif; }\n"

with open(FILE, "w", encoding="utf-8") as f:
    f.write(css)

print("Patched style.css tables")
