import requests
import json
try:
    from application.constants.paths import metadata_paths
    from application.constants.constants import params
except ModuleNotFoundError:
    from dags.application.constants.paths import metadata_paths
    from dags.application.constants.constants import params

RESULTS = metadata_paths['crossref']


def get_crossref_results(query=params['query'], max_results=params['crossref']['max_metadata']):
    url = "https://api.crossref.org/works"

    params = {
        "query": query,
        "sort": "relevance",
        "order": "desc",
        "rows": max_results,  # limit of 1000 per request.
        "filter": "has-references:true"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        return []

    json_response = response.json()

    items = json_response['message']['items']

    results = []

    for item in items:
        title = item.get('title', 'N/A')
        author = ", ".join([f"{author.get('family', 'N/A')}, {author.get('given', 'N/A')}" for author in
                            item.get('author', [{'family': 'N/A', 'given': 'N/A'}])])
        authors = item.get('author', [{'family': 'N/A', 'given': 'N/A', 'sequence': 'N/A', 'affiliation': []}])
        author_list = []
        for author in authors:
            author_dict = {
                'given': author.get('given', 'N/A'),
                'family': author.get('family', 'N/A'),
                'sequence': author.get('sequence', 'N/A'),
                'affiliation': author.get('affiliation', [])
            }
            author_list.append(author_dict)
        authors_info = author_list
        published_date = item.get('published-print', {}).get('date-parts', [[None]])[0][0] or \
                         item.get('published-online', {}).get('date-parts', [[None]])[0][0] or "N/A"

        journal_name = item.get('container-title', ["N/A"])[0]
        volume = item.get('volume', 'N/A')
        issue = item.get('issue', 'N/A')
        page = item.get('page', 'N/A')
        citation_count = item.get('is-referenced-by-count', 'N/A')
        doi = item.get('DOI', 'N/A')
        issn = item.get('ISSN', 'N/A')
        url = item.get('URL', 'N/A')
        abstract = item.get('abstract', 'N/A')
        license_url = item.get('license', [{}])[0].get('URL', 'N/A')
        funders = ", ".join([f"{funder.get('name', 'N/A')}: {funder.get('award', 'N/A')}" for funder in
                             item.get('funder', [])])
        publisher = item.get('publisher', 'N/A')

        result = {
            "title": title,
            "author": author,
            "authors": authors_info,
            "published_date": published_date,
            "publisher": publisher,
            "journal_name": journal_name,
            "volume": volume,
            "issue": issue,
            "page": page,
            "citation_count": citation_count,
            "doi": doi,
            "issn": issn,
            "url": url,
            "abstract": abstract,
            "license_url": license_url,
            "funders": funders
        }
        results.append(result)

    for i, result in enumerate(results):
        print(
            # f"{i + 1}. Title: {result['title']}\nAuthors: {result['authors']}\nPublished Date: {result[
            # 'published_date']}\nJournal Name: {result['journal_name']}\nVolume: {result['volume']}\nIssue: {result[
            # 'issue']}\nPage: {result['page']}\nCitation Count: {result['citation_count']}\nDOI: {result[
            # 'doi']}\nURL: {result['url']}\nAbstract: {result['abstract']}\n\n")
            f"{i + 1}/{len(results)} "
            f"|| Title: {result['title']} "
            f"|| Authors: {result['authors']} "
            f"|| Citation count: {result['citation_count']}"
            f"|| Doi: {result['doi']}"
            f"|| URL: {result['url']}")


    # save to json file
    with open(RESULTS, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    return results


def get_top_articles(articles, top_n=params['crossref']['top_n'],
                     input_file=params['crossref']['path'],
                     output_file=params['crossref']['top_path']):
    # with open(input_file, 'r') as f:
    #     articles = json.load(f)

    sorted_articles = sorted(articles, key=lambda x: x['citation_count'], reverse=True)
    top_articles = sorted_articles[:top_n]

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(top_articles, f, ensure_ascii=False, indent=4)

    return top_articles
