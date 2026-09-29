import os

CSS = """

/* =========================================================
   PAGE SPECIFIC ALIGNMENTS (ADVISORY, VALIDATION, RISK)
   ========================================================= */

#advisory-tab, #validation-tab, #risk-tab {
    max-width: 1400px;
    width: calc(100% - 48px);
    margin: 0 auto;
    padding-top: 24px;
}

@media (max-width: 1024px) {
    #advisory-tab, #validation-tab, #risk-tab { width: calc(100% - 40px); }
}

@media (max-width: 768px) {
    #advisory-tab, #validation-tab, #risk-tab { width: calc(100% - 32px); }
}

/* Common Page Headers */
#advisory-tab > div:first-child, 
#validation-tab > div:first-child, 
#risk-tab > div:first-child {
    display: flex;
    align-items: baseline;
    gap: 16px;
    margin-bottom: 24px;
}

#advisory-tab h1, #validation-tab h1, #risk-tab h1 {
    font-size: 26px !important;
    font-weight: 700;
    color: var(--primary);
    margin: 0;
    line-height: 1.2;
}

#advisory-tab > div:first-child span, 
#validation-tab > div:first-child span, 
#risk-tab > div:first-child span {
    font-size: 15px;
    color: var(--text-muted);
}

/* =========================================================
   ADVISORY PAGE
   ========================================================= */

#advisory-tab .dash-layout {
    display: flex;
    gap: 24px;
    margin-bottom: 24px;
    flex-wrap: wrap;
    align-items: flex-start;
}

#advisory-tab .dash-left {
    flex: 1;
    min-width: 320px;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

#advisory-tab .dash-right {
    flex: 2;
    min-width: 400px;
}

#advisory-tab input, #advisory-tab select, #advisory-tab button {
    height: 44px !important;
    border-radius: 6px !important;
    font-size: 14px !important;
    box-sizing: border-box;
}

/* =========================================================
   VALIDATION PAGE
   ========================================================= */

#validation-tab .weather-metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}

#validation-tab .metric-card {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    height: 100%;
}

#validation-tab .dash-layout {
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
}

#validation-tab .dash-left {
    flex: 1.5;
    min-width: 400px;
}

#validation-tab .dash-right {
    flex: 1;
    min-width: 350px;
}

/* Validation Table */
#validation-tab table {
    width: 100%;
    border-collapse: collapse;
}

#validation-tab th {
    padding: 12px;
    background: #F4F7F9;
    font-size: 13px;
    color: var(--text-muted);
    border-bottom: 1px solid var(--border);
}

#validation-tab td {
    padding: 12px;
    font-size: 14px;
    border-bottom: 1px solid var(--border);
}

#validation-tab tbody tr:last-child td {
    border-bottom: none;
}

/* =========================================================
   CROP RISK PAGE
   ========================================================= */

#risk-tab .dash-layout {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 20px;
    margin-bottom: 24px;
}

#risk-tab > div > div[style*="display:grid"] {
    grid-template-columns: repeat(3, 1fr) !important;
    gap: 20px !important;
}

#risk-tab .risk-card {
    height: 100%;
    display: flex;
    flex-direction: column;
}

@media (max-width: 1024px) {
    #advisory-tab .dash-layout,
    #validation-tab .dash-layout {
        flex-direction: column;
    }
    #risk-tab > div > div[style*="display:grid"] {
        grid-template-columns: 1fr !important;
    }
}
"""

FILE = r"src\dashboard\static\css\style.css"
with open(FILE, "a", encoding="utf-8") as f:
    f.write(CSS)

print("Appended targeted CSS for Advisory, Validation, Risk")
