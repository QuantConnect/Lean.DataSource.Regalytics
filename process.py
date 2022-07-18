import json
import pathlib
from datetime import datetime
import os
import requests
import sys

URL = os.environ["REGALYTICS_API_BASE_URL"]
HEADERS = {
    'Content-Type': 'application/json'
}
ARTICLE_PATH = pathlib.Path('/temp-output-directory/alternative/regalytics/articles')

def main(date):
    # objectives:# download data from API -> temp folder or in memory. Output processed datat  to /temp-output-directory/alternative/regalytics/articles/yyyyMMdd.json
    ARTICLE_PATH.mkdir(parents=True, exist_ok=True)
    articles_by_date = {}

    if date == "all":
        url = f"{URL}/get-all"
        payload = json.dumps({
            "apikey": os.environ["REGALYTICS_API_KEY"]
        })
        
        response = requests.post(url, headers=HEADERS, data=payload).json()
        max_page = response['all_pages']
        articles = response['results']

        for i in range(2, max_page + 1):
            response = requests.post(f'{url}?page={i}', headers=HEADERS, data=payload).json()
            articles += response['results']
            
    else:
        url = f"{URL}/search"
        payload = json.dumps({
            "apikey": os.environ["REGALYTICS_API_KEY"],
            "search_options": {
                "created_at": {
                    "start": date,
                    "end": date
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
        
        # remove timezone info (-04:00) [NewYork]
        article['created_at'] = article['created_at'][:-6]
        
        # all data received during day T would confer into day T+1 00:00
        date = datetime.strptime(article['created_at'], '%Y-%m-%dT%H:%M:%S.%f').date()
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

        with open(ARTICLE_PATH / f'{date}.json', 'w') as article_file:
            article_file.write(article_lines)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise ValueError("process.py only takes 1 argument.")
    main(sys.argv[-1])