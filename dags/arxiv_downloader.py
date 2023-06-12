from paths import metadata_paths, paper_paths
import os
import constants
import arxiv
import json
from datetime import datetime
import re
import database
from constants import params
from time import sleep

ARXIV_METADATA_OUTPUT = metadata_paths['arxiv']


def query_arxiv(search_term, num_metadata_to_download):
    search = arxiv.Search(
        query=search_term,
        max_results=num_metadata_to_download,
        sort_by=arxiv.SortCriterion.Relevance,
        sort_order=arxiv.SortOrder.Descending
    )

    return search


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def generate_arxiv_metadata(search, num_metadata_to_download):
    results = list()

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

    return results


def dump_to_json(results):
    with open(ARXIV_METADATA_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(results, f, cls=DateTimeEncoder, ensure_ascii=False, indent=4)


def download_pdf_files(search, num_metadata_to_download, num_pdf_files_to_download):
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
            database.upload_file(f'/arxiv_papers/{filename}')
            num_files_downloaded += 1


def query_arxiv_keywords(keywords,
                         num_metadata_to_download,
                         num_pdf_files_to_download,
                         main_query=params['query']):
    keyword_results = list()

    for keyword in keywords:
        print(f'\nDownloading data on keyword {keyword}...')
        keyword_query = f'{keyword} AND {main_query}'
        search = query_arxiv(keyword_query, num_metadata_to_download)
        generate_arxiv_metadata(search, num_metadata_to_download)
        download_pdf_files(search, num_metadata_to_download, num_pdf_files_to_download)
        keyword_results.append({'keyword': f'{keyword}',
                                'arxiv': {
                                    'metadata': keyword_results
                                }
                                })
        sleep(1)


def search_and_download_arxiv_papers():
    search = query_arxiv(params['query'], params['arxiv']['main']['max_metadata'])
    metadata = generate_arxiv_metadata(search, params['arxiv']['main']['max_metadata'])
    dump_to_json(metadata)
    download_pdf_files(search, params['arxiv']['main']['max_metadata'], params['arxiv']['main']['max_pdfs'])

    return metadata

