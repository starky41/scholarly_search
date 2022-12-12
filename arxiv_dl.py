import arxiv
import re

import database


def get_arxiv_results(search_query, path, max_results):
    search = arxiv.Search(
        query=search_query,
        max_results=max_results,  # up to 300,000
        sort_by=arxiv.SortCriterion.Relevance,
        sort_order=arxiv.SortOrder.Descending
    )

    results = []
    for idx, result in enumerate(search.results()):
        file_n = re.sub(r'\W+', ' ', result.title).replace(' ', '_') + ".pdf"

        result.download_pdf(dirpath=f'./data/',
                            filename=file_n)
        print(f'Downloaded article: {result.title} ({result.pdf_url})')

        data = {
                'id': result.entry_id,
                'updated': result.updated,
                'published': result.published,
                'title': result.title,
                'authors': str(result.authors),
                'summary': result.summary,
                'primary_category': result.primary_category,
                'categories': result.categories,
                'links': str(result.links),
                'pdf_url': str(result.pdf_url),

                }


        database.upload_pdf(file_n)
        results.append(data)
    print(results)

    # def get_pdf(path):
    #
    #     print(f'Downloading articles on {search_query}...')
    #     for result in search.results():
    #         result.download_pdf(dirpath=f'./data/',
    #                             filename=file_n)
    #         print(f'Downloaded article: {result.title} ({result.pdf_url})')

    # get_pdf(path)
    return results


def save_arxiv_results(path, results):
    results.to_csv(f'./{path}/arxiv.csv', sep=',', index=False,
                   header=True)
