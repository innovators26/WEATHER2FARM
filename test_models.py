import os
from groq import Groq
client = Groq(api_key="gsk_YOUR_API_KEY_HERE")
for model in client.models.list().data:
    print(model.id)
