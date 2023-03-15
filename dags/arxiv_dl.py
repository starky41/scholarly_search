import arxiv
import re
from time import sleep

import database


import arxiv
import re

import itertools



def get_arxiv_results(search_query, max_results, num_pdf_downloads):
    search = arxiv.Search(
        query=search_query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
        sort_order=arxiv.SortOrder.Descending
    )

    results = []
    pdf_downloads = 0
    for idx, result in enumerate(search.results()):
        if len(results) >= max_results:
            break

        file_n = re.sub(r'\W+', ' ', result.title).replace(' ', '_') + ".pdf"
        if pdf_downloads < num_pdf_downloads:
            result.download_pdf(dirpath=f'./data/',
                                filename=file_n)
            print(f'Downloaded article: {result.title} ({result.pdf_url})')
            database.upload_pdf(file_n)
            pdf_downloads += 1

        data = {
            'id': result.entry_id,
            'updated': result.updated,
            'published': result.published,
            'title': result.title,
            'authors': [author.name for author in result.authors],
            'summary': result.summary,
            'primary_category': result.primary_category,
            'categories': result.categories,
            'links': [{'title': link.title, 'href': link.href, 'rel': link.rel, 'content_type': link.content_type} for
                      link in result.links],
            'pdf_url': result.pdf_url,
        }

        print(f'{idx+1}/{max_results}')
        print(data)
        results.append(data)
    return results


def get_kw_results(keywords, num_metadata, num_pdf_downloads, main_query):
    kw_results = []
    for keyword in keywords:
        try:
            # path = services.create_folder(f'keywords/{keyword}')
            print(f'\nDownloading data on {keyword}...')

            # Adding keywords to the main term

            kwrd_query = f'{keyword} AND {main_query}'

            arxiv_results = get_arxiv_results(kwrd_query, max_results=num_metadata, num_pdf_downloads=num_pdf_downloads)
            kw_results.append({'keyword': f'{keyword}',
                               'arxiv': {
                                   'metadata': arxiv_results
                               }
                               })
            sleep(1)


        except Exception as e:
            print(e)

    return kw_results


def save_arxiv_results(path, results):
    results.to_csv(f'./{path}/arxiv.csv', sep=',', index=False,
                   header=True)
