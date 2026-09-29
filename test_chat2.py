import requests

url = "http://127.0.0.1:8080/api/chat"
payload = {
    "message": "Will it rain tomorrow?",
    "panchayat_id": "185874",
    "crop": "Onion",
    "sowing_date": "2026-08-20",
    "language": "en"
}
response = requests.post(url, json=payload)
print(response.status_code)
print(response.json())
