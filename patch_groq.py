import os

FILE = r"src\dashboard\app.py"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

groq_setup = """from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")
client = None
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)

app = FastAPI("""

code = code.replace("app = FastAPI(", groq_setup)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Added GROQ API key setup.")
