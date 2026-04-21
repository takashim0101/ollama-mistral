import requests
import json

response = requests.post('http://localhost:11434/api/generate', 
    json={
        'model': 'mistral',
        'prompt': 'Hello!',
        'stream': False
    }
)
print(response.json()['response'])
