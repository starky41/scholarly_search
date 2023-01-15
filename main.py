import arxiv_dl
import springer_dl
import database
from pathlib import Path


def main():
    Path('./data').mkdir(parents=True, exist_ok=True)
    query = str(input('Enter your query >>> '))
    springer_results = springer_dl.get_springer_results(query, results_to_get=200)
    keywords = springer_dl.find_keywords(query, springer_results, max_kw=2)
    print(keywords)
    arxiv_results = arxiv_dl.get_arxiv_results(query, 2)
    kw_results = arxiv_dl.get_kw_results(keywords)
    database.add_record(name=query,
                        springer_data=springer_results,
                        arxiv_data=arxiv_results,
                        kw_data=kw_results)


if __name__ == '__main__':
    main()
    print('Done!')
