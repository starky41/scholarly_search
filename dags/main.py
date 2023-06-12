from constants import params
from visualization import create_visualizations
from paths import create_directories
from kw_extraction import extract_keywords
import database
import arxiv_downloader
import springer_dl
import crossref_dl


def main():
    create_directories()
    query = params['query']

    springer_results = springer_dl.get_springer_results(query, metadata_to_download=params['springer']['max_metadata'])

    keywords = springer_dl.find_keywords(query,
                                         springer_results,
                                         max_kw=params['springer']['num_kw'])
    print(keywords)
    arxiv_results = arxiv_downloader.search_and_download_arxiv_papers()

    kw_results = arxiv_downloader.query_arxiv_keywords(keywords,
                                                       params['arxiv']['kw']['max_metadata'],
                                                       params['arxiv']['kw']['max_pdfs'])

    crossref_results = crossref_dl.get_crossref_results(query, max_results=params['crossref']['max_metadata'])
    crossref_dl.get_top_articles(input_file=params['crossref']['path'], top_n=params['crossref']['top_n'],
                                 output_file=params['crossref']['top_path'])

    create_visualizations(springer_results, arxiv_results, crossref_results, query)

    arxiv_results = extract_keywords()

    database.add_record(name=query,
                        springer_data=springer_results,
                        arxiv_data=arxiv_results,
                        crossref_data=crossref_results,
                        kw_data=kw_results)


if __name__ == '__main__':
    main()
    print('Done!')
