import requests
import json


# Import necessary constants and paths
try:
    from application.constants.paths import metadata_paths
    from application.constants.constants import params

except ModuleNotFoundError:
    from dags.application.constants.paths import metadata_paths
    from dags.application.constants.constants import params

# Set the path for the crossref results
RESULTS = metadata_paths["crossref"]


# Add function call to save results to file
def get_crossref_results(
        query=params["query"], max_results=params["crossref"]["max_metadata"]
):
    """
    Retrieve metadata of scholarly works from Crossref,
    based on a query and a maximum number of results.
    """

    # Define the query parameters
    params = {
        "query": query,
        "sort": "relevance",
        "order": "desc",
        "rows": max_results,  # limit of 1000 per request
        # "filter": "has-abstract:true"
    }

    # Make request to API and handle exceptions
    try:
        response = requests.get("https://api.crossref.org/works", params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        return []

    # Get the json response and retrieve the items
    json_response = response.json()
    items = json_response["message"]["items"]

    results = []

    # Loop through the items and extract relevant information
    for item in items:
        # Extract title information
        title = item.get("title")

        # Extract author information
        authors = item.get("author", [{"family": "N/A", "given": "N/A"}])
        author_list = []
        for author in authors:
            author_dict = {
                "given": author.get("given"),
                "family": author.get("family"),
                "sequence": author.get("sequence"),
                "affiliation": author.get("affiliation", [])
            }
            author_list.append(author_dict)

        # Extract publication date information
        published_date = None
        if item.get("published-print", {}).get("date-parts"):
            published_date = item["published-print"]["date-parts"][0][0]
        elif item.get("published-online", {}).get("date-parts"):
            published_date = item["published-online"]["date-parts"][0][0]

        # Extract journal name, volume, issue, page information
        journal_name = None
        if item.get("container-title"):
            journal_name = item["container-title"][0]
        volume = item.get("volume")
        issue = item.get("issue")
        page = item.get("page")

        # Extract citation count, DOI, ISSN, URL, abstract,
        # license URL, funders, and publisher information
        citation_count = item.get("is-referenced-by-count")
        doi = item.get("DOI")
        issn = item.get("ISSN")
        url = item.get("URL")
        abstract = item.get("abstract")
        license_url = None
        if item.get("license"):
            license_url = item["license"][0].get("URL")
        funders = ", ".join([f"{funder.get('name', '')}: {funder.get('award', '')}" for funder in
                             item.get('funder', [])]).strip()

        publisher = None
        if item.get("publisher"):
            publisher = item["publisher"]

        result = {
            "title": title or "N/A",
            "authors": author_list,
            "published_date": published_date or "N/A",
            "publisher": publisher or "N/A",
            "journal_name": journal_name or "N/A",
            "volume": volume or "N/A",
            "issue": issue or "N/A",
            "page": page or "N/A",
            # "citation_count": citation_count or "N/A",
            "citation_count": citation_count or 0,
            "doi": doi or "N/A",
            "issn": issn or "N/A",
            "url": url or "N/A",
            "abstract": abstract or "N/A",
            "license_url": license_url or "N/A",
            "funders": funders or "N/A"
        }

        # Append result to the list of results
        results.append(result)


    # Print main information about the results
    for i, result in enumerate(results):
        print(
            f"{i + 1}/{len(results)} "
            f" Title: {result['title']} "
            f" Authors: {result['authors']} "
            f" Citation count: {result['citation_count']}"
            f" Doi: {result['doi']}"
            f"|| URL: {result['url']}"
        )

    # Save results to a JSON
    with open(RESULTS, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    return results


def get_top_articles(articles, top_n=params['crossref']['top_n'],
                     input_file=params['crossref']['path'],
                     output_file=params['crossref']['top_path']):
    # with open(input_file, 'r') as f:
    #     articles = json.load(f)

    sorted_articles = sorted(articles, key=lambda x: int(x['citation_count']), reverse=True)
    top_articles = sorted_articles[:top_n]

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(top_articles, f, ensure_ascii=False, indent=4)

    return top_articles
