import pandas as pd
import re
from nltk.stem import WordNetLemmatizer
import json
try:
    from application.constants import paths
    from application.database import db
except ModuleNotFoundError:
    from dags.application.constants import paths
    from dags.application.database import db

scimago_path = paths.SCIMAGO_PATH
df_scimago = pd.read_csv(scimago_path, delimiter=';')
lemmatizer = WordNetLemmatizer()

metadata_collection = db["metadata"]
data_list = []

def get_top_papers():
    with open('output/metadata/crossref.json') as file:
        crossref_data = json.load(file)

    df = get_data_from_database(crossref_data)
    merged_df = preprocess(df)
    keyword_df, key_phrase_df = find_keyword_matches()
    ranked_df = rank_papers(merged_df, keyword_df, key_phrase_df)
    results = get_results(merged_df, ranked_df)
    print(results)
    return results


def get_data_from_database(crossref_data):
    data_list = []

    for crossref_obj in crossref_data:
        authors = [f"{a.get('family', '')} {a.get('given', '')}".strip() for a in crossref_obj.get("authors", [])]
        title = crossref_obj.get("title", [''])[0]
        doi = crossref_obj.get("doi", "")
        year = pd.NA if (year := crossref_obj.get("published_date", {})) == 'N/A' else year
        publisher = pd.NA if (publisher := crossref_obj.get("publisher", "")) == 'N/A' else publisher
        journal_name = pd.NA if (journal_name := crossref_obj.get("journal_name", "")) == 'N/A' else journal_name
        volume = crossref_obj.get("volume", None)
        issue = crossref_obj.get("issue", None)
        page = crossref_obj.get("page", None)
        citation_count = pd.NA if (citation_count := crossref_obj.get("citation_count",
                                                                      None)) == 'N/A' else citation_count
        issn = ", ".join(crossref_obj.get("ISSN", []))
        url = crossref_obj.get("URL", "")
        abstract = pd.NA if crossref_obj.get('abstract', '') == 'N/A' else crossref_obj.get('abstract', '')
        funders = ", ".join([funder.get("name", "") for funder in crossref_obj.get("funder", [])])

        data_list.append({"doi": doi, "title": title, "authors": authors, "year": year, "publisher": publisher,
                          "journal_name": journal_name, "citation_count": citation_count, 'abstract': abstract})

    df = pd.DataFrame(data_list,
                      columns=["doi", "title", "authors", "year", "journal_name", 'citation_count', 'abstract'])
    return df

def preprocess(df):
    # Preprocessing
    df.loc[pd.notna(df['abstract']), 'abstract'] = df.loc[pd.notna(df['abstract']), 'abstract'].apply(
        lambda x: re.sub('<.*?>', '', str(x)))

    merged_df = pd.merge(df.assign(journal_name_lower=df['journal_name'].str.lower()),
                         df_scimago[['Title', 'H index', 'SJR Best Quartile']].assign(
                             Title_lower=df_scimago['Title'].str.lower()),
                         left_on='journal_name_lower', right_on='Title_lower', how='left')

    merged_df.drop('Title', axis=1, inplace=True)
    merged_df.drop('Title_lower', axis=1, inplace=True)
    merged_df.drop('journal_name_lower', axis=1, inplace=True)
    merged_df.rename(columns={'H index': 'Journal H index', 'SJR Best Quartile': 'Journal SJR Quartile'}, inplace=True)

    merged_df = merged_df.reindex(
        columns=['doi', 'title', 'authors', 'journal_name', 'year', 'Journal H index', 'Journal SJR Quartile',
                 'citation_count', 'abstract'])
    merged_df["original_index"] = merged_df.index

    merged_df.dropna(subset=['Journal SJR Quartile', 'citation_count', 'abstract'], how='all', inplace=True)
    merged_df.dropna(subset=['journal_name', 'citation_count'], how='all', inplace=True)

    merged_df = merged_df.dropna(subset=['citation_count'])
    # Drop when 2 or more missing values
    required_columns = ['journal_name', 'year', 'citation_count']
    merged_df = merged_df.dropna(subset=required_columns, thresh=len(required_columns) - 1)

    return merged_df


def lemmatize_keywords_and_phrases(lemmatizer, keywords, key_phrases):
    lemmatized_keywords = []
    lemmatized_key_phrases = []

    # Lemmatize the keywords
    for keyword in keywords:
        lemmatized_keyword = lemmatizer.lemmatize(keyword)
        lemmatized_keywords.append(lemmatized_keyword)

    # Lemmatize the key_phrases
    for key_phrase in key_phrases:
        lemmatized_key_phrase = lemmatizer.lemmatize(key_phrase)
        lemmatized_key_phrases.append(lemmatized_key_phrase)

    return lemmatized_keywords, lemmatized_key_phrases


def find_keyword_matches():
    # Keywords
    # Create an empty dictionary to hold the keyword and key phrase counts
    keyword_counts = {}
    key_phrase_counts = {}

    all_docs = metadata_collection.find()

    # Loop over each document
    for doc in all_docs:
        # Extract the crossref objects
        arxiv_objs = doc.get("data", {}).get("query", {}).get("arxiv", {}).get('metadata', [])

        # Loop over each crossref object
        for arxiv_obj in arxiv_objs:
            # Extract the tf_idf information from the arxiv object
            tf_idf = arxiv_obj.get("tf_idf", {})

            # Get the keywords and key_phrases lists from the tf_idf dictionary
            keywords = tf_idf.get("keywords", [])
            key_phrases = tf_idf.get("key_phrases", [])

            # Lemmatize the keywords and key_phrases using a stemmer/lemmatizer of your choice
            lemmatized_keywords, lemmatized_key_phrases = lemmatize_keywords_and_phrases(lemmatizer, keywords,
                                                                                         key_phrases)

            # Add the lemmatized keywords and key phrases to the dictionary
            for lemmatized_keyword in lemmatized_keywords:
                if lemmatized_keyword not in keyword_counts:
                    keyword_counts[lemmatized_keyword] = 0
                keyword_counts[lemmatized_keyword] += 1
            for lemmatized_key_phrase in lemmatized_key_phrases:
                if lemmatized_key_phrase not in key_phrase_counts:
                    key_phrase_counts[lemmatized_key_phrase] = 0
                key_phrase_counts[lemmatized_key_phrase] += 1

    # Create a list of dictionaries containing the keyword and key phrase data
    keyword_data = [{"keyword": k, "count": v} for k, v in keyword_counts.items()]
    key_phrase_data = [{"key_phrase": k, "count": v} for k, v in key_phrase_counts.items()]

    # Append the data dictionaries to the data list
    data_list.append({"keywords": keyword_data, "key_phrases": key_phrase_data})

    keyword_df = pd.DataFrame(keyword_data).sort_values('count', ascending=False)
    key_phrase_df = pd.DataFrame(key_phrase_data).sort_values('count', ascending=False)

    return keyword_df, key_phrase_df


def rank_papers(merged_df, keyword_df, key_phrase_df):
    # Ranking
    factor_importance = {
        'citation_count': 0.5,
        'h_index': 0.3,
        'year': 0.2,
        'original_index': 0.5,
        'keyword': 0.3,
        'key_phrase': 0.10
    }

    # Fill missing H-index values with the average H-index
    average_h_index = merged_df['Journal H index'].mean()
    merged_df['Journal H index'] = merged_df['Journal H index'].fillna(average_h_index)

    merged_df['lemmatized_title'] = merged_df['title'].apply(
        lambda x: ' '.join([lemmatizer.lemmatize(word) for word in x.split()]))

    # Create keyword_score and key_phrase_score columns with initial value 0
    merged_df['keyword_score'] = 0
    merged_df['key_phrase_score'] = 0

    # Iterate over each row in merged_df
    for index, row in merged_df.iterrows():
        # Iterate over each keyword in keyword_df
        for k, v in keyword_df.iterrows():
            # If keyword is present in lemmatized title, add its count to keyword_score
            if v['keyword'] in row['lemmatized_title']:
                merged_df.at[index, 'keyword_score'] += v['count']

        # Iterate over each key phrase in key_phrase_df
        for k, v in key_phrase_df.iterrows():
            # If key phrase is present in lemmatized title, add its count to key_phrase_score
            if v['key_phrase'] in row['lemmatized_title']:
                merged_df.at[index, 'key_phrase_score'] += v['count']

    # Normalize keyword_score and key_phrase_score between 0 and 1
    merged_df['keyword_score'] = (merged_df['keyword_score'] - merged_df['keyword_score'].min()) / (
            merged_df['keyword_score'].max() - merged_df['keyword_score'].min())
    merged_df['key_phrase_score'] = (merged_df['key_phrase_score'] - merged_df['key_phrase_score'].min()) / (
            merged_df['key_phrase_score'].max() - merged_df['key_phrase_score'].min())

    # Weight keyword_score and key_phrase_score
    merged_df['keyword_score'] *= factor_importance['keyword']
    merged_df['key_phrase_score'] *= factor_importance['key_phrase']

    # Calculate other ranking factors and weight accordingly
    merged_df['citation_count_norm'] = (merged_df['citation_count'] - merged_df['citation_count'].min()) / (
            merged_df['citation_count'].max() - merged_df['citation_count'].min())
    merged_df['citation_count_weighted'] = merged_df['citation_count_norm'] * factor_importance['citation_count']

    ceiling = 30  # set a ceiling limit
    merged_df['H_index_score'] = merged_df['Journal H index'].clip(upper=ceiling) / ceiling * factor_importance[
        'h_index']

    current_year = 2023  # update this with the current year
    merged_df['year_score'] = (current_year - pd.to_numeric(merged_df['year'], errors='coerce').fillna(
        0)) / current_year * \
                              factor_importance['year']
    merged_df['original_index_score'] = 1 / pd.to_numeric(merged_df['original_index'], errors='coerce') * \
                                        factor_importance[
                                            'original_index']

    # Calculate ranking score by adding all factors
    merged_df['ranking_score'] = merged_df['citation_count_weighted'] + merged_df['H_index_score'] + merged_df[
        'year_score'] + merged_df['original_index_score'] + merged_df['keyword_score'] + merged_df['key_phrase_score']

    # Sort merged_df by ranking_score in descending order
    merged_df = merged_df.sort_values(by='ranking_score', ascending=False)
    return merged_df


def get_results(df, ranked_df):
    # Return results
    top_10_records = ranked_df[:10]
    # Find records with the same indices in 'df'
    common_records = df[df.index.isin(top_10_records.index)]

    # Remove '\' from DOI fields
    common_records.loc[:, 'doi'] = common_records['doi'].str.replace('\\', '')

    # Convert DataFrame to a list of dictionaries
    records = common_records.to_dict(orient='records')

    # Save records to a JSON file
    with open('my_json_file.json', 'w') as file:
        json.dump(records, file)

    # print(records)

    return records



get_top_papers()