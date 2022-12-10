import arxiv
import pandas as pd
import re


def get_arxiv_results(search_query, path, max_results):
    search = arxiv.Search(
        query=search_query,
        max_results=max_results,  # up to 300,000
        sort_by=arxiv.SortCriterion.Relevance,
        sort_order=arxiv.SortOrder.Descending
    )

    results = []
    for idx, result in enumerate(search.results()):
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
                'pdf_url': str(result.pdf_url)
                }

        results.append(data)

    print(results)

    # data = {
    #     "id": [],
    #     "updated": [],
    #     "published": [],
    #     "title": [],
    #     "authors": [],
    #     "summary": [],
    #     'primary_category': [],
    #     'categories': [],
    #     'links': [],
    #     'pdf_url': []
    #
    # }
    #
    # for result in search.results():
    #     data['id'].append(str(result.entry_id))
    #     data['updated'].append(str(result.updated))
    #     data['published'].append(str(result.published))
    #     data['title'].append(str(result.title))
    #     data['authors'].append(str(result.authors))
    #     data['summary'].append(str(result.summary))
    #     data['primary_category'].append(str(result.primary_category))
    #     data['categories'].append(str(result.categories))
    #     data['links'].append(str(result.links))
    #     data['pdf_url'].append(str(result.pdf_url))

    # df = pd.DataFrame.from_dict(data)

    def get_pdf(path):
        print(f'Downloading articles on {search_query}...')
        for result in search.results():
            result.download_pdf(dirpath=f'./{path}/',
                                filename=re.sub(r'\W+', ' ', result.title).replace(' ', '_') + ".pdf")
            print(f'Downloaded article: {result.title} ({result.pdf_url})')

    # get_pdf(path)
    # return df
    return results


def save_arxiv_results(path, results):
    results.to_csv(f'./{path}/arxiv.csv', sep=',', index=False,
                   header=True)
