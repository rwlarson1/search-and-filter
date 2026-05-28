import requests, json

url = "http://127.0.0.1:5000/api/search"

body = {
    "data": [
        {
            "name": "Cookie",
            "price": "3.50",
            "quantity": "10"
            },
        {
            "name": "Muffin",
            "price": "Cookie",
            "quantity": "8"
            },
        {
            "name": "Cookie2",
            "price": "3.55",
            "quantity": "15"
            },
        {
            "name": "Brownie",
            "price": None,
            "quantity": "4"
            }
        ],
    "search_text": "Name"
    }

response = requests.post(url, json=body)

print(json.dumps(response.json(), indent=4))