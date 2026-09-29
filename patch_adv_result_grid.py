import os

CSS = """

/* Advisory Result Grid Layout (No HTML changes needed) */
#advResult {
    display: grid !important;
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
        "crop alert"
        "weather alert"
        "trend risk"
        "actions actions"
        "avoid avoid";
    gap: 24px;
    align-items: start;
}
#advResult > div:nth-child(1) { grid-area: alert; }
#advResult > div:nth-child(2) { grid-area: crop; }
#advResult > div:nth-child(3) { grid-area: weather; }
#advResult > div:nth-child(4) { grid-area: trend; }
#advResult > div:nth-child(5) { grid-area: risk; }
#advResult > div:nth-child(6) { grid-area: actions; }
#advResult > div:nth-child(7) { grid-area: avoid; }

@media (max-width: 1024px) {
    #advResult {
        grid-template-columns: 1fr;
        grid-template-areas:
            "alert"
            "crop"
            "weather"
            "trend"
            "risk"
            "actions"
            "avoid";
    }
}

/* 4. ADVISORY ACTION CARDS */
/* "All recommendation cards must: have equal spacing, align to the same grid" */
#advResActions {
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px !important;
}

/* Ensure the generated action cards (which are injected via JS) match heights */
#advResActions > div {
    height: 100%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
}
"""

FILE = r"src\dashboard\static\css\style.css"
with open(FILE, "a", encoding="utf-8") as f:
    f.write(CSS)

print("Appended CSS grid layout for Advisory Results")
