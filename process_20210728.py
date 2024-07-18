from json import dumps
from pathlib import Path
from datetime import datetime, timedelta, timezone
from os import environ
from requests import post
import threading
import pandas as pd

URL = environ.get("REGALYTICS_API_BASE_URL", "https://api.regalytics.ai/api/v3")
API_KEY = environ.get("REGALYTICS_API_KEY", "")

# objectives:# download data from API -> temp folder or in memory. Output processed datat  to /temp-output-directory/alternative/regalytics/articles/yyyyMMdd.json
ARTICLE_PATH = Path('/temp-output-directory/alternative/regalytics/articles')
ARTICLE_PATH.mkdir(parents=True, exist_ok=True)
articles_by_date = {}
# using sourced_at at payload from 2020-01-01 (start of data) to 2021-07-27 as RegAlytics api has 'created_at' field for all articles mapped to 2021-07-28 (inception date of RegAlytics API)

start_date = datetime(2020,1,1)
end_date = datetime(2021,7,27)
none_sourced_at_date_count = 0

def get_data_from_source(process_date):

    payload = dumps({
        "apikey": API_KEY,
        "search_options": {
            "sourced_at": {
                "start": process_date,
                "end": process_date
            }
        },
    })

    def get_page(p):
        page = post(f"https://api.regalytics.ai/api/v3/search?page={p}", headers={ 'Content-Type': 'application/json' }, data=payload).json()
        all_responses.append(page)

    page_1 = post(f"https://api.regalytics.ai/api/v3/search", headers={ 'Content-Type': 'application/json' }, data=payload).json()
    all_responses = [page_1]

    if page_1['total_pages'] == 1:
        return page_1['total_results'], all_responses
    
    threads = []

    for p in range(2, page_1['total_pages'] + 1):
        threads.append(threading.Thread(target=get_page, args=(p,)))

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    all_responses.sort(key=lambda x: x['page_number'])

    return page_1['total_results'], all_responses
    
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
    global none_sourced_at_date_count
    total_results, all_responses = get_data_from_source(process_date)
    if total_results == 0: return

    try:
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
                # changing the created_at for articles with a delta of 1 day addition to sourced_at data
                manipulated_sourced_at = f"{article['sourced_at'][:10]}T00:00:00+00:00"
                temp_sourced_at = datetime.fromisoformat(manipulated_sourced_at)
                temp_sourced_at+= pd.offsets.BDay()
                manipulated_sourced_at = temp_sourced_at.isoformat()
                print(manipulated_sourced_at)
                article['created_at'] = manipulated_sourced_at[:-3] + manipulated_sourced_at[-2:]       # %z only accepts `-0400` instead of `-04:00` in Python3.6
                
                try:
                    created_at = datetime.strptime(article['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(timezone.utc)
                except:
                    created_at = datetime.strptime(article['created_at'], '%Y-%m-%dT%H:%M:%S%z').astimezone(timezone.utc) # sourced_at sometimes have a different format
                
                article['created_at'] = created_at.strftime('%Y-%m-%dT%H:%M:%S.%f')
                date_key = created_at.strftime('%Y%m%d')

                if date_key not in articles_by_date:
                    date_articles = []
                    articles_by_date[date_key] = date_articles
                else:
                    date_articles = articles_by_date[date_key]

                date_articles.append(article)

        if total_results!=len(date_articles):
            print(f"Data mismatch on {process_date}")
        
        for date, articles in articles_by_date.items():
            with open(ARTICLE_PATH / f'{date}.json', 'w') as article_file:
                article_lines = '\n'.join([dumps(article, indent=None) for article in articles])
                article_file.write(article_lines)
    except Exception as e:
        print(f"Error {e} on {process_date}")

if __name__ == "__main__":
    current_date = start_date
    while current_date <= end_date:
        process_date = current_date
        process(process_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)