from pathlib import Path

import database
import arxiv_dl
import springer_dl
import visualization

import crossref_dl

metadata_path = './output/metadata'

params = {
    'query': 'Natural language processing',
    'springer': {
        'max_metadata': 200,
        'max_pdfs': 2,
        'num_kw': 2,
        'path': metadata_path + '/springer.json',
    },
    'arxiv': {
        'main': {'max_metadata': 100, 'max_pdfs': 2},
        'kw': {'max_metadata': 100, 'max_pdfs': 2},
        'path': metadata_path + '/arxiv.json',
    },
    'crossref': {
        'max_metadata': 100,  # limited by 1000.
        'top_n': 10,
        'path': metadata_path + '/crossref.json',
        'top_path': metadata_path + '/crossref_top.json',
    }
}


def main():
    Path('./output/metadata').mkdir(parents=True, exist_ok=True)

    query = params['query']

    springer_results = springer_dl.get_springer_results(query,
                                                        results_to_get=params['springer']['max_metadata'])
    visualization.create_wordcloud(springer_results)

    springer_dl.download_articles(springer_results,
                                  params['springer']['max_pdfs'])

    keywords = springer_dl.find_keywords(query,
                                         springer_results,
                                         max_kw=params['springer']['num_kw'])
    print(keywords)
    arxiv_results = arxiv_dl.get_arxiv_results(query,
                                               max_results=params['arxiv']['main']['max_metadata'],
                                               num_pdf_downloads=params['arxiv']['main']['max_pdfs'])

    visualization.plot_articles_by_year(arxiv_results, query)
    kw_results = arxiv_dl.get_kw_results(
        keywords,
        num_metadata=params['arxiv']['kw']['max_metadata'],
        num_pdf_downloads=params['arxiv']['kw']['max_pdfs'],
        main_query=params['query']
    )
    crossref_results = crossref_dl.get_crossref_results(params['query'], max_results=params['crossref']['max_metadata'])
    crossref_dl.get_top_articles(input_file=params['crossref']['path'], top_n=params['crossref']['top_n'],
                                 output_file=params['crossref']['top_path'])

    database.add_record(name=query,
                        springer_data=springer_results,
                        arxiv_data=arxiv_results,
                        crossref_data=crossref_results,
                        kw_data=kw_results)


if __name__ == '__main__':
    main()
    print('Done!')
