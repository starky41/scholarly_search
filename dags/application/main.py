from visualization import create_visualizations
from constants.paths import create_directories
from kw_extraction import extract_keywords
import database

from downloaders.arxiv_downloader import search_and_download_arxiv_papers, query_arxiv_keywords
from downloaders.springer_downloader import get_springer_results, find_keywords
from downloaders.crossref_downloader import get_crossref_results, get_top_articles

def main():
    create_directories()

    springer_results = get_springer_results(download=True)
    keywords = find_keywords(springer_results)
    print(keywords)

    arxiv_results = search_and_download_arxiv_papers()
    kw_results = query_arxiv_keywords(keywords)

    crossref_results = get_crossref_results()
    get_top_articles(crossref_results)

    create_visualizations(springer_results, arxiv_results, crossref_results)

    arxiv_results = extract_keywords(arxiv_results)

    database.add_record(springer_data=springer_results,
                        arxiv_data=arxiv_results,
                        crossref_data=crossref_results,
                        kw_data=kw_results)


if __name__ == '__main__':
    main()
    print('Done!')
