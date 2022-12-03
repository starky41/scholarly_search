import math
import requests
import json
from time import sleep
import pandas as pd

# Constants
START = 1
MAX_RESULTS = 100
API_KEY = ""
with open("apikey.txt", "r") as apikey_file:
    API_KEY = apikey_file.readlines()[0].strip()


def get_springer_results(query, results_to_get):

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
                    f'api_key={API_KEY}',
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

    create_query(query)
    results = springer_find(results_to_get, query)
    results = pd.DataFrame.from_dict(results)

    return results


def save_springer_results(path, results):
    results.to_csv(f'./{path}/springer.csv', sep=',', index=False,
                   header=True)


def find_keywords(query, results, path):
    keywords = results['keyword'].apply(pd.Series).stack().reset_index(drop=True)
    keywords = list(keywords.value_counts().index[:30])
    keywords = [keyword.rstrip() for keyword in keywords]

    while '' in keywords:
        keywords.remove('')
    keywords = keywords[:10]
    query = query.replace("%22", "")
    query.replace("+", "_")
    with open(f'./{path}/keywords.txt', 'w') as f:
        f.write(str(keywords))
    return keywords
