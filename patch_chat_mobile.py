import os

FILE = r"src\dashboard\static\css\style.css"
with open(FILE, "a", encoding="utf-8") as f:
    f.write("\n@media (max-width: 400px) { #global-chatbot-popup { width: calc(100vw - 48px) !important; right: 24px !important; } }\n")

print("Added mobile responsiveness for chatbot popup")
