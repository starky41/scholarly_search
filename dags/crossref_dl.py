import requests
import json
from pathlib import Path

RESULTS = './output/metadata/crossref.json'
Path('./output/metadata').mkdir(parents=True, exist_ok=True)

def get_crossref_results(query, max_results):
    # set the Crossref API URL
    url = "https://api.crossref.org/works"

    # set the query parameters
    params = {
        "query": query,
        "sort": "relevance",
        "order": "desc",
        "rows": max_results # limit of 1000 per request.
    }

    # send a GET request to the Crossref API
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # raises an HTTPError for 4xx or 5xx status codes
    except requests.exceptions.RequestException as e:
        print(e)
        return []

    # get the JSON response
    json_response = response.json()

    # get the items from the JSON response
    items = json_response['message']['items']

    # create an empty list to store the results
    results = []

    # iterate over the items
    for item in items:
        # get the title
        title = item.get('title', 'N/A')

        # get the authors
        authors = ", ".join([f"{author.get('family', 'N/A')}, {author.get('given', 'N/A')}" for author in
                             item.get('author', [{'family': 'N/A', 'given': 'N/A'}])])

        # get the published date
        published_date = item.get('published-print', {}).get('date-parts', [[None]])[0][0] or \
                         item.get('published-online', {}).get('date-parts', [[None]])[0][0] or "N/A"

        # get the journal name
        journal_name = item.get('container-title', ["N/A"])[0]

        # get the volume
        volume = item.get('volume', 'N/A')

        # get the issue
        issue = item.get('issue', 'N/A')

        # get the page numbers
        page = item.get('page', 'N/A')

        # get the number of citations
        citation_count = item.get('is-referenced-by-count', 'N/A')

        # get the DOI
        doi = item.get('DOI', 'N/A')

        # get the URL
        url = item.get('URL', 'N/A')

        # get the abstract
        abstract = item.get('abstract', 'N/A')

        # get the license URL
        license_url = item.get('license', [{}])[0].get('URL', 'N/A')

        # get the funder information
        funders = ", ".join([f"{funder.get('name', 'N/A')}: {funder.get('award', 'N/A')}" for funder in
                             item.get('funder', [])])

        # create a dictionary to store the results
        result = {
            "title": title,
            "authors": authors,
            "published_date": published_date,
            "journal_name": journal_name,
            "volume": volume,
            "issue": issue,
            "page": page,
            "citation_count": citation_count,
            "doi": doi,
            "url": url,
            "abstract": abstract,
            "license_url": license_url,
            "funders": funders
        }

        # add the result to the results list
        results.append(result)

    for i, result in enumerate(results):
        print(
            f"{i + 1}. Title: {result['title']}\nAuthors: {result['authors']}\nPublished Date: {result['published_date']}\nJournal Name: {result['journal_name']}\nVolume: {result['volume']}\nIssue: {result['issue']}\nPage: {result['page']}\nCitation Count: {result['citation_count']}\nDOI: {result['doi']}\nURL: {result['url']}\nAbstract: {result['abstract']}\n\n")


    # save to json file
    with open(RESULTS, 'w') as f:
        json.dump(results, f)

    return results








def get_top_articles(input_file, top_n, output_file):
    with open(input_file, 'r') as f:
        articles = json.load(f)

    sorted_articles = sorted(articles, key=lambda x: x['citation_count'], reverse=True)
    top_articles = sorted_articles[:top_n]

    with open(output_file, 'w') as f:
        json.dump(top_articles, f)
