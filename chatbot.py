import requests

API_URL = 'http://localhost:11434/api/chat'

def chat(msg):
    data = { 'model': 'badminbot',
            'stream': False,
            'messages': [
                { 'role': 'user', 'content': f'{msg}' }
                ]
            }
    resp = requests.post(API_URL, json=data)
    return resp.json()['message']['content']
