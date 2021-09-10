import json
import pathlib
import os
import requests
import time

from datetime import datetime, timedelta, timezone

url = os.environ["REGALYTICS_API_BASE_URL"] + "/filter"
processing_date = datetime.strptime(os.environ["QC_DATAFLEET_DEPLOYMENT_DATE"], "%Y%m%d")

# objectives:
# 1. Download data from paginated API
# 2. Output processed data to /temp-output-directory/alternative/regalytics/articles/yyyyMMdd.json

articles_path = pathlib.Path('/temp-output-directory/alternative/regalytics/articles')
articles_path.mkdir(parents=True, exist_ok=True)

payload = json.dumps({
    "apikey": os.environ["REGALYTICS_API_KEY"]
})
headers = {
    'Content-Type': 'application/json'
}

page = 1
total_pages = None
complete = False
output_articles = []

# API response is sorted in descending order using the `created_at` field
while not complete and page != total_pages:
    response = requests.post(url, params={"page": page}, headers=headers, data=payload)
    if total_pages is None:
        total_pages = int(response["all_pages"])

    articles = response["results"]

    for article in articles:
        created_at = datetime.strptime(article['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(timezone.utc)
        if created_at.date() < processing_date.date():
            # We've completed processing all the data that was available
            # for us on the processing date.
            complete = True
            break

        if created_at.date() != processing_date.date():
            continue

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

        output_articles.append(article)

    print(f"Processed page {page} of {total_pages}")
    page += 1
    time.sleep(1)

if len(output_articles) == 0:
    raise Exception(f"No data was processed for deployment date: {processing_date.date()}")

print(f"Writing data to output directory: {articles_path}")

with open(articles_path / f'{processing_date.strftime("%Y%m%d")}.json', 'w') as article_file:
    lines = '\n'.join([json.dumps(article, indent=None) for article in output_articles])
    article_file.write(lines)