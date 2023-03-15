from pathlib import Path

import arxiv_dl
import database
import springer_dl
import visualization

params = {
    'query': 'Natural language processing',
    'springer_get': 200,
    'num_kw': 3,
    'arxiv_metadata_download_main': 200,
    # 'arxiv_get_main': 4,
    'arxiv_pdf_download_main': 1,
    # 'arxiv_get_kw': 2
    'arxiv_metadata_download_kw':10 ,
    'arxiv_pdf_download_kw': 2,
}


def main():
    Path('./data').mkdir(parents=True, exist_ok=True)
    query = params['query']
    springer_results = springer_dl.get_springer_results(query, results_to_get=params['springer_get'])
    visualization.create_wordcloud(springer_results)
    springer_dl.download_articles(springer_results)
    keywords = springer_dl.find_keywords(query, springer_results, max_kw=params['num_kw'])
    print(keywords)
    arxiv_results = arxiv_dl.get_arxiv_results(query,
                                               max_results=params['arxiv_metadata_download_main'],
                                               num_pdf_downloads=params['arxiv_pdf_download_main'])

    visualization.plot_articles_by_year(arxiv_results, query)
    kw_results = arxiv_dl.get_kw_results(keywords,
                                         num_metadata=params['arxiv_metadata_download_kw'],
                                         num_pdf_downloads=params['arxiv_pdf_download_kw'],
                                         main_query=params['query'])
    database.add_record(name=query,
                        springer_data=springer_results,
                        arxiv_data=arxiv_results,
                        kw_data=kw_results)


if __name__ == '__main__':
    main()
    print('Done!')
