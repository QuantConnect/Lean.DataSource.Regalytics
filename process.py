import json
import pathlib
from datetime import datetime, timedelta
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
# objectives:# download data from API -> temp folder or in memory. Output processed datat  to /temp-output-directory/alternative/regalytics/articles/yyyyMMdd.json
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
# 1. query all data, -> /api/.../all; 2. look at latest_update, add delta of 1/2 days;
# 3. write data to date of latest_update + delta. This date must be on the date we published the article on Regalytics
articles = response['articles']
articles_by_date = {}

for article in articles:
    article['in_federal_register'] = 'yes' in article['in_federal_register'].lower()
    # State -> Dictionary<string, List<string>>
    states = {}
    if 'states' not in article or article['states'] is None:
        continue

    for state in article['states']:
        if 'country' not in state:
            continue

        country = state['country']
        if country is None:
            continue

        if not country['name'] in states:
            country_states = []
            states[country['name']] = country_states
        else:
            country_states = states[country['name']]

        country_states.append(state['name'])

    article['states'] = states
    article['agencies'] = [agency['name'] for agency in article['agencies']]
    
    date = datetime.strptime(article['latest_update'], '%Y-%m-%d')
    date_key = date.strftime('%Y%m%d')

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

    with open(articles_path / f'{date}.json', 'w') as article_file:
        article_file.write(article_lines)
