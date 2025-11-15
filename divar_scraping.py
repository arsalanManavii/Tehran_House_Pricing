import os
import json
import time
import random
import requests
import pandas as pd
from unidecode import unidecode


# ========================================
# Global Config
# ========================================

BASE_URL = 'https://api.divar.ir/v8/postlist/w/search'
DETAIL_URL = 'https://api.divar.ir/v8/posts-v2/web/'
HEADER = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 11.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/134.0.6998.166 Safari/537.36'
    )
}

# Initial pagination values
enumerate_ = 1
value_count = 26
houses_data = []

# API payload
payload = {
    "city_ids": ["1"],
    "source_view": "CATEGORY",
    "disable_recommendation": False,
    "map_state": {"camera_info": {"bbox": {}}, "page_state": "HALF_STATE"},
    "search_data": {
        "form_data": {"data": {"category": {"str": {"value": "residential-sell"}}}},
        "server_payload": {
            "@type": "type.googleapis.com/widgets.SearchData.ServerPayload",
            "additional_form_data": {"data": {"sort": {"str": {"value": "sort_date"}}}},
        },
    },
}


# ========================================
# Helpers
# ========================================

def convert_farsi_number_to_english(number: int):
    """Convert Persian digits to English digits."""
    return unidecode(number)


def save_links_in_file(links: list):
    """Save list of links into a text file."""
    with open('links.txt', 'w', encoding='utf-8') as f:
        for link in links:
            f.write(f'{link}\n')


def read_links_from_file():
    """Read links back from file."""
    with open('links.txt', 'r', encoding='utf-8') as f:
        return f.read().split()


# ========================================
# Fetching Data
# ========================================

def fetch_detail_house(url: str):
    """Fetch single house details, using cache if available."""
    token = url.split('/')[-1]
    cache_file = f"cache/{token}.json"
    os.makedirs('cache', exist_ok=True)

    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    r = requests.get(url=url, headers=HEADER)
    r.raise_for_status()
    response = r.json()

    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=1)

    time.sleep(random.uniform(1, 3))
    return response


def fetch_detail_all_houses(enumerate_: int, value_count: int):
    """Fetch all houses detail (from links)."""
    if os.path.exists('links.txt'):
        links = read_links_from_file()
    else:
        links = get_links(enumerate_=enumerate_, value_count=value_count)
        save_links_in_file(links)

    result = []
    for link in links:
        detail = fetch_detail_house(link)
        result.append(detail)
    return result


def get_links(enumerate_: int, value_count: int):
    """Scrape house tokens from Divar API and build links."""
    items, links = [], []
    print('Loading...')

    while True:
        print(f'#{enumerate_}')
        r = requests.post(url=BASE_URL, headers=HEADER, json=payload)
        time.sleep(random.uniform(1, 3))
        response = r.json()

        items.extend(response['list_widgets'])

        # Update pagination
        last_post_date = response['pagination']['data']['last_post_date']
        search_uid = response['pagination']['data']['search_uid']
        viewed_tokens = response['pagination']['data']['viewed_tokens']
        payload['pagination_data'] = {
            "@type": "type.googleapis.com/post_list.PaginationData",
            "last_post_date": last_post_date,
            "page": enumerate_,
            "layer_page": enumerate_,
            "search_uid": search_uid,
            "cumulative_widgets_count": value_count,
            "viewed_tokens": viewed_tokens,
        }

        enumerate_ += 1
        value_count += 24

        if len(items) > 1000:
            break

    print(len(items))
    for item in items:
        token = item.get("data", {}).get("action", {}).get("payload", {}).get("token")
        if token:
            links.append(DETAIL_URL + token)
        else:
            print('invalid data')

    return links


# ========================================
# Processing Data
# ========================================

def assign_values(enumerate_: int, value_count: int):
    """Extract structured house data from API response."""
    details = fetch_detail_all_houses(enumerate_=enumerate_, value_count=value_count)
    all_houses = []

    for detail_house in details:
        section_data = detail_house['sections'][4]['widgets'][0]['data']
        items = section_data.get('items', [])

        if not items:
            print("does not have 'items' key")
            continue

        latitude = detail_house['seo']['post_seo_schema']['geo']['latitude']
        longitude = detail_house['seo']['post_seo_schema']['geo']['longitude']
        title = detail_house['seo']['post_seo_schema']['web_info']['title']

        size_of_house = convert_farsi_number_to_english(items[0]['value'])
        year_of_manufacture = convert_farsi_number_to_english(items[1]['value'])
        number_of_room = convert_farsi_number_to_english(items[2]['value'])

        token = (
            detail_house['contact']
            .get('action_log', {})
            .get('server_side_info', {})
            .get('info', {})
            .get('post_token')
        )

        # Handle widget variations
        if len(detail_house['sections'][4]['widgets']) < 8:
            total_price = detail_house['sections'][4]['widgets'][1]['data']['value'].rsplit()
            price_per_meter = detail_house['sections'][4]['widgets'][2]['data']['value'].rsplit()
        else:
            total_price = detail_house['sections'][4]['widgets'][2]['data']['value'].rsplit()
            price_per_meter = detail_house['sections'][4]['widgets'][3]['data']['value'].rsplit()

        total_price_converted = convert_farsi_number_to_english(total_price[0])
        price_per_meter_converted = convert_farsi_number_to_english(price_per_meter[0])

        all_houses.append((
            latitude,
            longitude,
            title,
            size_of_house,
            year_of_manufacture,
            number_of_room,
            total_price_converted,
            price_per_meter_converted,
            token
        ))

    return all_houses


def dataframe_to_excel(houses_data: list):
    dataframe = pd.DataFrame(
        houses_data,
        columns=[
            "latitude", "longitude", "title", "house_size",
            "manufacture_year", "rooms", "total_price",
            "price_per_meter", "token",
        ],
    )
    dataframe.to_excel('data.xlsx', index=False, engine='openpyxl')
    dataframe.to_csv('data.csv', index=False, encoding='utf-8')


def print_values(houses_data: list):
    """Pretty-print house data."""
    for house in houses_data:
        (
            latitude, longitude, title, size_of_house,
            year_of_manufacture, number_of_room,
            total_price, price_per_meter, token
        ) = house

        print(f"""
        latitude : {latitude}
        longitude : {longitude}
        title : {title}
        size_house : {size_of_house}
        manufacture_year : {year_of_manufacture}
        #rooms : {number_of_room}
        total_price : {total_price}
        price_per_meter : {price_per_meter}
        endpoint_url : {DETAIL_URL + token}
        """)


# ========================================
# Main Script
# ========================================

if __name__ == "__main__":
    houses_data = assign_values(enumerate_=enumerate_, value_count=value_count)
    dataframe_to_excel(houses_data=houses_data)
