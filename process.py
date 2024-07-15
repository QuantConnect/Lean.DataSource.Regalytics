from json import dumps
from pathlib import Path
from datetime import datetime, timezone
from os import environ
from requests import post
import threading

URL = environ.get("REGALYTICS_API_BASE_URL", "https://api.regalytics.ai/api/v3")
API_KEY = environ.get("REGALYTICS_API_KEY", "0f63222e69a5e25957c4fcf2c739b3b66c102910")
DEPLOYMENT_DATE = environ.get('QC_DATAFLEET_DEPLOYMENT_DATE', f'{datetime.now():%Y%m%d}')

# objectives:# download data from API -> temp folder or in memory. Output processed datat  to /temp-output-directory/alternative/regalytics/articles/yyyyMMdd.json
ARTICLE_PATH = Path('temp-output-directory_temp/alternative/regalytics/articles')
ARTICLE_PATH.mkdir(parents=True, exist_ok=True)
articles_by_date = {}

process_date = datetime.strptime(DEPLOYMENT_DATE, '%Y%m%d').strftime('%Y-%m-%d')

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

    def get_page(p):
        page = post(f"https://api.regalytics.ai/api/v3/search?page={p}", headers={ 'Content-Type': 'application/json' }, data=payload).json()
        all_responses.append(page)

    page_1 = post(f"https://api.regalytics.ai/api/v3/search", headers={ 'Content-Type': 'application/json' }, data=payload).json()
    all_responses = [page_1]

    if page_1['total_pages'] == 1:
        return all_responses
    
    threads = []

    for p in range(2, page_1['total_pages'] + 1):
        threads.append(threading.Thread(target=get_page, args=(p,)))

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    all_responses.sort(key=lambda x: x['page_number'])

    return all_responses
    
# "agencies": [
#     {
#         "name": "Iowa Department of Human Services",
#         "state": [
#             {
#                 "name": "Iowa"
#             }
#         ],
#         "country": [
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

    for response in all_responses:
        for article in response.get('results', []):
            article['in_federal_register'] = 'yes' in article['in_federal_register'].lower()
            # State -> Dictionary<string, List<string>>
            states = {}
            agencies = article.get('agencies', [])
            if not agencies:
                agencies = []
            for agency in agencies:
                state = agency.get('state')
                if not state:
                    continue

                for country in agency.get('country', []):
                    name = country['name']

                    if not name in states:
                        country_states = []
                        states[name] = country_states
                    else:
                        country_states = states[name]

                country_states.extend([x['name'] for x in state])

            article['states'] = states
            article['agencies'] = [agency['name'] for agency in agencies]
            
            # search using `created_at` returns all with UTC time between 00:00-23:59 in a single day, 
            # so it include some articles created at 20:00-00:00 in EST of the "previous day" (-04:00).
            # Adjust timezone info of `created_at` field into UTC time to avoid overwriting the previous day file
            article['created_at'] = article['created_at'][:-3] + article['created_at'][-2:]       # %z only accepts `-0400` instead of `-04:00` in Python3.6
            created_at = datetime.strptime(article['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(timezone.utc)
            article['created_at'] = created_at.strftime('%Y-%m-%dT%H:%M:%S.%f')
            date_key = created_at.strftime('%Y%m%d')

            if date_key not in articles_by_date:
                date_articles = []
                articles_by_date[date_key] = date_articles
            else:
                date_articles = articles_by_date[date_key]

            date_articles.append(article)

        for date, articles in articles_by_date.items():
            with open(ARTICLE_PATH / f'{date}.json', 'w') as article_file:
                article_lines = '\n'.join([dumps(article, indent=None) for article in articles])
                article_file.write(article_lines)

if __name__ == "__main__":
    process(process_date)