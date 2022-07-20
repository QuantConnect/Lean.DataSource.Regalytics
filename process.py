import json
import pathlib
from datetime import datetime, timedelta
import os
import requests

URL = os.environ["REGALYTICS_API_BASE_URL"]
HEADERS = {
    'Content-Type': 'application/json'
}
ARTICLE_PATH = pathlib.Path('/temp-output-directory/alternative/regalytics/articles')

# objectives:# download data from API -> temp folder or in memory. Output processed datat  to /temp-output-directory/alternative/regalytics/articles/yyyyMMdd.json
ARTICLE_PATH.mkdir(parents=True, exist_ok=True)
articles_by_date = {}

process_datetime = datetime.strptime(os.environ['QC_DATAFLEET_DEPLOYMENT_DATE'], '%Y%m%d').date()
process_date = process_datetime.strftime('%Y-%m-%d')

url = f"{URL}/search"
payload = json.dumps({
    "apikey": os.environ["REGALYTICS_API_KEY"],
    "search_options": {
        "created_at": {
            "start": process_date,
            "end": process_date
        }
    }
})

response = requests.post(url, headers=HEADERS, data=payload).json()
articles = response['articles']
    
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

for article in articles:
    article['in_federal_register'] = 'yes' in article['in_federal_register'].lower()
    # State -> Dictionary<string, List<string>>
    states = {}
    for agency in article['agencies']:
        state = agency['states']
        
        if 'states' not in agency or state is None:
            continue

        if 'countries' not in agency:
            continue

        countries = agency['countries']
        if countries is None:
            continue
        
        for country in countries:
            name = country['name']
            
            if not name in states:
                country_states = []
                states[name] = country_states
            else:
                country_states = states[name]

        country_states.extend([x['name'] for x in state])

    article['states'] = states
    article['agencies'] = [agency['name'] for agency in article['agencies']]
    
    # adjust timezone info (e.g. -04:00) into UTC time
    timezone_adjust = article['created_at'][-5:]
    plus_or_minus = article['created_at'][-6]
    timezone_adjust = datetime.strptime(timezone_adjust, "%H:%M")
    timedelta_adjust = timedelta(hours=timezone_adjust.hour, minutes=timezone_adjust.minute)
    
    created_at = datetime.strptime(article['created_at'][:-6], '%Y-%m-%dT%H:%M:%S.%f')
    if plus_or_minus == "+":
        created_at -= timedelta_adjust
    elif plus_or_minus == "-":
        created_at += timedelta_adjust
    
    # all data received during day T would confer into bar of Time = Day T 00:00; EndTime = Day T+1 00:00 at UTC time
    date_key = created_at.date().strftime('%Y%m%d')
    article['created_at'] = created_at.strftime('%Y-%m-%dT%H:%M:%S.%f')     # UTC Time

    if date_key not in articles_by_date:
        date_articles = []
        articles_by_date[date_key] = date_articles
    else:
        date_articles = articles_by_date[date_key]

    date_articles.append(article)

for date, articles in articles_by_date.items():
    lines = []
    for article in articles:
        lines.append(json.dumps(article, indent=None))

    article_lines = '\n'.join(lines)

    with open(ARTICLE_PATH / f'{date}.json', 'w') as article_file:
        article_file.write(article_lines)