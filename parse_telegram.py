import os
import psycopg2
from parse import *

# export $(cat .env | grep -v '#' | sed 's/\r$//' | awk '/=/ {print $1}' )

DB_CREDS = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
}

BOT_TOKEN = os.getenv('BOT_TOKEN')

SHORTLINK_TOKEN = os.getenv('SHORTLINK_TOKEN')


def message(text: str) -> None:
    print(text)
    requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
        params={
            'chat_id': 268094109,
            'text': text
        }
    )


def get_ids() -> list[int]:
    with psycopg2.connect(**DB_CREDS) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ids FROM gifts")
            ids = cursor.fetchone()[0].split(',')
            if ids == ['']: return [] # if empty
            return list(map(int, ids))



def save_ids(ids: list[int]) -> None:
    with psycopg2.connect(**DB_CREDS) as conn:
        with conn.cursor() as cursor:
            ids_string = ','.join(str(id) for id in ids)
            cursor.execute('DELETE FROM gifts')
            cursor.execute('INSERT INTO gifts VALUES(%s)', (ids_string,))
            conn.commit()


def get_shortlink(url: str) -> str:
    r = requests.post('https://dedol.link/api/link',
        data=json.dumps({
            'token': SHORTLINK_TOKEN,
            'url': url,
        })
    ).json()
    return 'dedol.link/' + r['link']


def public_post(gift: Item) -> None:
    print(f'Post: gift {gift.id}')
    chat_id = '@banggoodFreeGifts'
    shortlink = get_shortlink(gift.url)
    requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto',
        params={
            'chat_id': chat_id,
            'photo': gift.image,
            'caption': f'${gift.price} {gift.name}\n{shortlink}',
        }
    )
    time.sleep(5)
    

def handle_new_gifts(saved_ids: list[int], gifts: list[Item]) -> None:
    new = [gift for gift in gifts if gift.id not in saved_ids]
    message(f'Found {len(new)} new gifts')

    save_ids([gift.id for gift in gifts])

    for gift in new:
        if gift.category != "Women's Clothing":
            public_post(gift)


if __name__ == '__main__':
    categories = get_categories()
    last_giftlist = load_last_giftlist()
    gifts = get_gifts(categories, last_giftlist)
    export_json(gifts)

    saved_ids = get_ids()
    handle_new_gifts(saved_ids, gifts)


    # Update database ids from data.js
    # ids = load_last_giftlist()
    # save_ids(ids)
    # print(len(get_ids()))