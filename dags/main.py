import arxiv_dl
import springer_dl
import database
from pathlib import Path

params = {
    'query': 'Neural network',
    'springer_get': 100,
    'num_kw': 0,
    'arxiv_get_main': 1,
    'arxiv_get_kw': 0
}


def main():
    Path('./data').mkdir(parents=True, exist_ok=True)
    query = params['query']
    springer_results = springer_dl.get_springer_results(query, results_to_get=params['springer_get'])
    keywords = springer_dl.find_keywords(query, springer_results, max_kw=params['num_kw'])
    print(keywords)
    arxiv_results = arxiv_dl.get_arxiv_results(query, params['arxiv_get_main'])
    kw_results = arxiv_dl.get_kw_results(keywords, num_results=params['arxiv_get_kw'])
    database.add_record(name=query,
                        springer_data=springer_results,
                        arxiv_data=arxiv_results,
                        kw_data=kw_results)


if __name__ == '__main__':
    main()
    print('Done!')
