import math
import requests
import json
from time import sleep
import pandas as pd
import os

try:
    from application.database import upload_file
    from application.constants.paths import paper_paths
    from application.constants.apikey import API_KEY
    from application.constants.constants import *
except ModuleNotFoundError:
    from dags.application.database import upload_file
    from dags.application.constants.paths import paper_paths
    from dags.application.constants.apikey import API_KEY
    from dags.application.constants.constants import *
# Constants
START = 1
MAX_RESULTS = 100

springer_params = params['springer']


def get_springer_results(query=params['query'], metadata_to_download=springer_params['max_metadata'],
                         pdfs_to_download=springer_params['max_pdfs'], download=False):
    create_query(query)
    results = springer_find(metadata_to_download, query)
    with open(metadata_paths['springer'], 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    if download:
        download_papers(results, pdfs_to_download)
    return results


def create_query(query):
    query = '%22' + f'{query}'.replace(' ', '+') + '%22'
    return query


def springer_find(results_to_get, query):
    list_of_results = []
    for i in range(math.ceil(results_to_get / MAX_RESULTS)):
        try:
            print('Requesting a page...')
            response = requests.get(
                f'http://api.springernature.com/meta/v2/json?'
                f'q={query}&'
                f's={1 + i * 100}&'
                f'p={MAX_RESULTS}&'
                f'api_key={API_KEY}&',
                timeout=20)

            result = json.loads(response.text)
            list_of_results.append(result['records'])
            print(
                f'Page retrieved: {i + 1}/{math.ceil(results_to_get / MAX_RESULTS)}'
                f'\nTime elapsed: {response.elapsed.total_seconds():.2f} sec.\n')
            sleep(3)
        except requests.exceptions.Timeout:
            print("Timeout occurred\n")
        except ValueError as e:
            print(e)

    print(f'{len(list_of_results) * 100} results were retrieved successfully')
    flattened_list = [item for sublist in list_of_results for item in sublist]
    return flattened_list


def find_keywords(results, query=params['query'], max_kw=springer_params['num_kw']):
    results = pd.DataFrame.from_dict(results)
    keywords = results['keyword'].apply(pd.Series).stack().reset_index(drop=True)
    keywords = list(keywords.value_counts().index[:30])
    keywords = [keyword.rstrip() for keyword in keywords]

    while '' in keywords:
        keywords.remove('')
    keywords = keywords[:max_kw]
    query = query.replace("%22", "")
    query.replace("+", "_")
    return keywords


def download_papers(articles, num_articles=params['springer']['max_pdfs']):
    folder_name = paper_paths['springer']
    count = 0
    for article in articles:
        if article['openaccess'] == 'true':
            for url in article['url']:
                if url['format'] == 'pdf':
                    response = requests.get(url['value'])
                    file_name = os.path.join(folder_name, article['title'] + '.pdf')
                    with open(file_name, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded: {article['title']} to {folder_name}.")
                    upload_file(f"springer_papers/{article['title']}.pdf")
                    count += 1
                    if count == num_articles:
                        return
                    break
