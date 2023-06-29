import arxiv
import json
from datetime import datetime
import re
from time import sleep


try:
    from application.constants.constants import params
    from application.database import upload_file
    from application.constants.paths import metadata_paths, paper_paths
except ModuleNotFoundError:
    from dags.application.constants.constants import params
    from dags.application.database import upload_file
    from dags.application.constants.paths import metadata_paths, paper_paths


ARXIV_METADATA_OUTPUT = metadata_paths['arxiv']


def query_arxiv(search_term=params['query'], num_metadata_to_download=params['arxiv']['main']['max_metadata']):
    search = arxiv.Search(
        query=search_term,
        max_results=num_metadata_to_download,
        sort_by=arxiv.SortCriterion.Relevance,
        sort_order=arxiv.SortOrder.Descending
    )
    return search


def generate_arxiv_metadata(search, num_metadata_to_download):
    results = list()
    try:
        for result in search.results():
            data = {
                'id': result.entry_id,
                'updated': result.updated,
                'published': result.published,
                'title': result.title,
                'authors': [author.name for author in result.authors],
                'summary': result.summary,
                'primary_category': result.primary_category,
                'categories': result.categories,
                'links': [{'title': link.title,
                           'href': link.href,
                           'rel': link.rel,
                           'content_type': link.content_type}
                          for link in result.links],
                'pdf_url': result.pdf_url,
            }

            results.append(data)
            print(
                f"{len(results)}/{num_metadata_to_download} "
                f" Title: {data['title']} "
                f" Authors: {data['authors']} "
                f"|| ID: {data['id']}"
            )
    except arxiv.arxiv.UnexpectedEmptyPageError:
        print('ERROR: UnexpectedEmptyPageError')

    return results


def dump_to_json(results):
    with open(ARXIV_METADATA_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(results, f,
                  cls=DateTimeEncoder,
                  ensure_ascii=False, indent=4)


def download_pdf_files(search,
                       num_metadata_to_download=params['arxiv']['main']['max_metadata'],
                       num_pdf_files_to_download=params['arxiv']['main']['max_pdfs']):
    if num_pdf_files_to_download <= num_metadata_to_download:
        num_files_downloaded = 0
        for result in search.results():
            if num_files_downloaded == num_pdf_files_to_download:
                break
            filename = re.sub(r'\W+', ' ', result.title) + ".pdf"
            result.download_pdf(dirpath=f'{paper_paths["arxiv"]}/',
                                filename=filename)
            print(
                f'Downloaded article [{num_files_downloaded + 1}/{num_pdf_files_to_download}]: {result.title} ({result.pdf_url})')
            upload_file(f'/arxiv_papers/{filename}')
            num_files_downloaded += 1


def query_arxiv_keywords(keywords,
                         main_query=params['query']):
    all_keywords_results = []
    for keyword in keywords:
        print(f'\nDownloading data on keyword {keyword}...')
        keyword_query_results = search_and_download_arxiv_papers(query=f'{keyword} AND {main_query}',
                                                                 num_metadata_to_download=params['arxiv']['kw'][
                                                                     'max_metadata'],
                                                                 num_pdf_files_to_download=params['arxiv']['kw'][
                                                                     'max_pdfs'],
                                                                 save_to_json=False, download_files=False)
        all_keywords_results.append({'keyword': f'{keyword}',
                                     'arxiv': {
                                         'metadata': keyword_query_results
                                     }})
        sleep(1)

    return all_keywords_results


def search_and_download_arxiv_papers(query=params['query'],
                                     num_metadata_to_download=params['arxiv']['main']['max_metadata'],
                                     num_pdf_files_to_download=params['arxiv']['main']['max_pdfs'],
                                     save_to_json=True, download_files=True):

    search = query_arxiv(query, num_metadata_to_download)


    metadata = generate_arxiv_metadata(search, num_metadata_to_download)


    if save_to_json:
        dump_to_json(metadata)

    if download_files:
        download_pdf_files(search, num_pdf_files_to_download)

    return metadata


def serialize(metadata):
    # serialize data using custom JSON encoder
    # ! IMPORTANT airflow dags cannot store unserialized data in xcoms
    serialized_metadata = json.dumps(metadata, cls=DateTimeEncoder)

    return serialized_metadata


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        # Check for other types you need to serialize here
        return super().default(obj)

# class DateTimeEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if obj is None:
#             return None
#         if isinstance(obj, datetime.datetime):
#             return obj.isoformat()
#         return super().default(obj)

