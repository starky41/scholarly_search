from time import sleep
import database
import arxiv
import re
import json
from datetime import datetime
from paths import metadata_paths, paper_paths

ARXIV_METADATA_OUTPUT = metadata_paths['arxiv']


def get_arxiv_results(search_query, num_metadata_to_download, num_files_to_download):
    search = arxiv.Search(
        query=search_query,
        max_results=num_metadata_to_download,
        sort_by=arxiv.SortCriterion.Relevance,
        sort_order=arxiv.SortOrder.Descending
    )

    results = []
    pdf_downloads = 0
    for idx, result in enumerate(search.results()):
        if len(results) >= num_metadata_to_download:
            break
        file_n = re.sub(r'\W+', ' ', result.title) + ".pdf"

        if pdf_downloads < num_files_to_download:
            result.download_pdf(dirpath=f'{paper_paths["arxiv"]}/',
                                filename=file_n)
            print(f'Downloaded article: {result.title} ({result.pdf_url})')
            database.upload_file(f'/arxiv_papers/{file_n}')
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

        print(f"{idx + 1}/{num_metadata_to_download} || Title: {data['title']} || Authors: {data['authors']} || link: {data['id']}")
        results.append(data)

    # Save json
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return json.JSONEncoder.default(self, obj)

    # Save json
    with open(ARXIV_METADATA_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(results, f, cls=DateTimeEncoder, ensure_ascii=False, indent=4)

    return results


def get_kw_results(keywords, num_metadata, num_pdf_downloads, main_query):
    kw_results = []
    for keyword in keywords:
        try:
            print(f'\nDownloading data on {keyword}...')

            # Adding keywords to the main term
            kwrd_query = f'{keyword} AND {main_query}'
            arxiv_results = get_arxiv_results(kwrd_query, num_metadata_to_download=num_metadata,
                                              num_files_to_download=num_pdf_downloads)
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
    results.to_csv(f'/{path}/arxiv.csv', sep=',', index=False,
                   header=True)
