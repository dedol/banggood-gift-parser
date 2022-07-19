from typing import NamedTuple
import json
import requests
import time


class Category(NamedTuple):
    id: str
    name: str
    count: int
    item_ids: list


class Item(NamedTuple):
    id: int
    name: str
    image: str
    url: str
    price: float
    category: str
    is_new: bool


def get_categories() -> list[Category]:
    print('Getting categories..')
    r = requests.get('https://banggood.com/load/event/getNewUserIndexData.html',
        params={
            'type': 'free_gift',
            'page': 1,
            'pageSize': 1,
            'cat_id': 0,
        }
    ).json()

    cats = []
    for cat in r['data']['category']:
        id = str(cat['cat_id'])
        if id == '0': 
            continue
        name = cat['name']
        req = requests.get('https://banggood.com/load/event/getNewUserIndexData.html',
            params={
                'type': 'free_gift',
                'page': 1,
                'pageSize': 1500,
                'cat_id': id,
            }
        ).json()
        count = req['data']['total']
        item_ids = [int(item['url'].split('-')[-2]) for item in req['data']['category_data']]
        cats.append(Category(id, name, count, item_ids))
        print(f'{name}: {count}')

    return cats


def load_last_giftlist() -> set:
    r = requests.get('https://dedol.ru/banggood/data.js').text
    data = json.loads(r.replace('var data = ', ''))

    ids = set(item['id'] for item in data)

    print(f'From dedol.ru/banggood/data.js loaded {len(ids)} items')
    return ids


def get_gifts(categories: list[Category], last_giftlist: set) -> list[Item]:
    r = requests.get('https://banggood.com/load/event/getNewUserIndexData.html',
        params={
            'type': 'free_gift',
            'page': 1,
            'pageSize': 1500,
            'cat_id': 0,
        }
    ).json()

    items = []
    for item in r['data']['category_data']:
        id = int(item['url'].split('-')[-2])
        name = item['products_name']
        image = item['image_url']
        url = item['url']
        price = float(item['products_price'])
        category = 'Without category'

        for cat in categories:
            if id in cat.item_ids:
                category = cat.name
                continue

        is_new = False if id in last_giftlist else True
        items.append(Item(id, name, image, url, price, category, is_new))

    total_count = len(items)
    new_count = len([item for item in items if item.is_new])
    print(f'Total: {total_count} | New: {new_count}')
    return items


def export_json(items: list[Item]) -> None:
    data = [i._asdict() for i in items]

    with open('web/data.js', 'w', encoding='utf-8') as file:
        file.write('var data = ')
        json.dump(data, file, ensure_ascii=False, indent=2)

    with open('web/info.js', 'w', encoding='utf-8') as file:
        file.write('var info = {"updated": ' + str(int(time.time())) + '}')


if __name__ == '__main__':
    categories = get_categories()
    last_giftlist = load_last_giftlist()
    gifts = get_gifts(categories, last_giftlist)
    export_json(gifts)