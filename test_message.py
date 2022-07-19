import requests

from creds import BOT_TOKEN


r = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
    params={
        'chat_id': 268094109,
        'text': 'test_message'
    }
)

print(r.text)
