import sys
from json import dumps
from pathlib import Path
from datetime import datetime, timezone
from os import environ
from concurrent.futures import ThreadPoolExecutor
from requests import Session

URL = environ.get("REGALYTICS_API_BASE_URL", "https://api.regalytics.ai/api/v3")
API_KEY = environ.get("REGALYTICS_API_KEY", "")
DEPLOYMENT_DATE = environ.get('QC_DATAFLEET_DEPLOYMENT_DATE', f'{datetime.now():%Y%m%d}')

# objectives:# download data from API -> temp folder or in memory. Output processed datat  to /temp-output-directory/alternative/regalytics/articles/yyyyMMdd.json
ARTICLE_PATH = Path('/temp-output-directory/alternative/regalytics/articles')
ARTICLE_PATH.mkdir(parents=True, exist_ok=True)
articles_by_date = {}

process_date = datetime.strptime(DEPLOYMENT_DATE, '%Y%m%d').strftime('%Y-%m-%d')

SESSION = Session()

def get_data_from_source(process_date):

    payload = dumps({
        "apikey": API_KEY,
        "search_options": {
            "created_at": {
                "start": process_date,
                "end": process_date
            },
            "page_size": 1000,
        },
    })
    headers = {'Content-Type': 'application/json'}

    def fetch(page):
        url = f"{URL}/search" if page == 1 else f"{URL}/search?page={page}"
        return SESSION.post(url, headers=headers, data=payload).json()

    page_1 = fetch(1)
    if page_1['total_pages'] == 1:
        return [page_1]

    with ThreadPoolExecutor(max_workers=8) as executor:
        remaining = list(executor.map(fetch, range(2, page_1['total_pages'] + 1)))

    return [page_1] + remaining
    
# example of agencies field in the article data:
# On February 3, 2025, the keys in the `agencies` field became `states` and `countries`, instead of `state` and `country`.
# "agencies": [
#     {
#         "name": "Iowa Department of Human Services",
#         "states": [
#             {
#                 "name": "Iowa"
#             }
#         ],
#         "countries": [
#             {
#                 "name": "United States"
#             }
#         ]
#     }
# ]
# if states is more than 0
# loop into state and get the state name
# 1. query all data, -> /api/v2/.../get-all; 2. look at latest_update, add delta of 1/2 days;
# 3. write data to date of latest_update + delta. This date must be on the date we published the article on Regalytics

def process(process_date):
    all_responses = get_data_from_source(process_date)
    print(f'Fetched {len(all_responses)} response page(s) for {process_date}')

    for response in all_responses:
        for article in response.get('results', []):
            # Convert `in_federal_register` field into boolean value, default to False if the field is missing or empty or None.
            article['in_federal_register'] = 'yes' in (article.get('in_federal_register') or '').lower()      
            # State -> Dictionary<string, List<string>>
            states = {}
            agencies = article.get('agencies') or []
            for agency in agencies:
                state = agency.get('states') or agency.get('state') or []
                if not state:
                    continue

                state_names = [x['name'] for x in state]
                countries = agency.get('countries') or agency.get('country') or []
                for country in countries:
                    states.setdefault(country['name'], []).extend(state_names)

            article['states'] = states
            article['agencies'] = [agency['name'] for agency in agencies]

            # search using `created_at` returns all with UTC time between 00:00-23:59 in a single day,
            # so it include some articles created at 20:00-00:00 in EST of the "previous day" (-04:00).
            # Adjust timezone info of `created_at` field into UTC time to avoid overwriting the previous day file
            created_at = datetime.strptime(article['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(timezone.utc)
            article['created_at'] = created_at.strftime('%Y-%m-%dT%H:%M:%S.%f')
            date_key = created_at.strftime('%Y%m%d')

            articles_by_date.setdefault(date_key, []).append(article)

    date_count = len(articles_by_date)
    print(f'Writing {date_count} date file(s)')
    for date, articles in articles_by_date.items():
        print(f'  {date}: {len(articles)} article(s)')
        with open(ARTICLE_PATH / f'{date}.json', 'w') as article_file:
            article_file.write('\n'.join(dumps(article, indent=None) for article in articles))

    if date_count > 1:
        sys.exit(f'ERROR: expected 1 date, got {date_count}: {sorted(articles_by_date)}')

if __name__ == "__main__":
    process(process_date)