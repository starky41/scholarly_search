import arxiv
import pandas as pd
import pathlib
from datetime import datetime


def get_arxiv_results(search_query):
    search = arxiv.Search(
        query=search_query,
        max_results=100,  # up to 300,000
        sort_by=arxiv.SortCriterion.Relevance,
    )

    data = {
        "id": [],
        "updated": [],
        "published": [],
        "title": [],
        "authors": [],
        "summary": [],
        'primary_category': [],
        'categories': [],
        'links': [],
        'pdf_url': []

    }

    for result in search.results():
        data['id'].append(result.entry_id)
        data['updated'].append(result.updated)
        data['published'].append(result.published)
        data['title'].append(result.title)
        data['authors'].append(result.authors)
        data['summary'].append(result.summary)
        data['primary_category'].append(result.primary_category)
        data['categories'].append(result.categories)
        data['links'].append(result.links)
        data['pdf_url'].append(result.pdf_url)

    df = pd.DataFrame.from_dict(data)
    return df


def save_arxiv_results(path, results):
    # pathlib.Path('./my/directory').mkdir(parents=True, exist_ok=True)


    results.to_csv(f'./{path}/arxiv.csv', sep=',', index=False,
                   header=True)
