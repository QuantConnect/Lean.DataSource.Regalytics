import json
import pathlib
from datetime import datetime, timedelta, timezone
import os
import requests

url = os.environ["REGALYTICS_API_BASE_URL"] + "/all"

payload = json.dumps({
    "apikey": os.environ["REGALYTICS_API_KEY"]
})
headers = {
    'Content-Type': 'application/json'
}

response = requests.post(url, headers=headers, data=payload).json()
articles_path = pathlib.Path('/temp-output-directory/alternative/regalytics/articles')
# objectives:# download data from API -> temp folder or in memory. Output processed data to /temp-output-directory/alternative/regalytics/articles/yyyyMMdd.json
articles_path.mkdir(parents=True, exist_ok=True)
# "states": [
#         {
#           "name": "United States",
#           "country": {
#             "name": "United States"
#           }
#         }
#       ],
# if states is more than 0
# loop into state and get the state name
# 1. query all data, -> /api/.../all;
# 2. write data to date of created_time, which is the time that the article was made public
articles = response['articles']
articles_by_date = {}

for article in articles:
    article['in_federal_register'] = 'yes' in article['in_federal_register'].lower()
    # State -> Dictionary<string, List<string>>
    states = {}

    agencies = article['agencies']
    if agencies is None or len(agencies) == 0:
        continue

    for agency in agencies:
        countries = agency.get('countries')
        if countries is None or len(countries) == 0:
            continue

        state_names = []
        agency_states = agency.get('states')

        if agency_states is not None:
            state_names = [state['name'] for state in agency['states'] if state.get('name') is not None]

        for country in countries:
            country_name = country.get('name')
            if country_name is None:
                continue

            country_states = states.get(country_name)
            if country_states is None:
                country_states = []
                states[country_name] = country_states

            country_states.extend(state_names)
            country_states = list(set(country_states))

    article['states'] = states
    article['agencies'] = [agency['name'] for agency in article['agencies']]
    
    date = datetime.strptime(article['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(timezone.utc)
    date_key = date.strftime('%Y%m%d')

    date_articles = articles_by_date.get(date_key)
    if date_articles is None:
        date_articles = []
        articles_by_date[date_key] = date_articles

    date_articles.append(article)

for date, articles in articles_by_date.items():
    lines = []
    for article in articles:
        lines.append(json.dumps(article, indent=None))

    article_lines = '\n'.join(lines)

    with open(articles_path / f'{date}.json', 'w') as article_file:
        article_file.write(article_lines)
