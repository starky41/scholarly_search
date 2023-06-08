import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import json


def extract_keywords():
    # Load the metadata into a pandas dataframe
    json_path = "output/metadata/arxiv.json"

    with open(json_path, encoding='utf-8') as f:
        metadata = json.load(f)

    # Extract the text data
    text_data = []
    for doc in metadata:
        text_data.append(doc['title'] + " " + doc['summary'])

    # Define the TF-IDF vectorizer with top 10 keywords
    vectorizer = TfidfVectorizer(stop_words='english', max_features=10)

    # Fit and transform the text with the vectorizer
    tfidf = vectorizer.fit_transform(text_data)

    # Get the feature names (top 10 keywords)
    feature_names = vectorizer.get_feature_names_out()

    # Define the TF-IDF vectorizer with top 10 key phrases
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(2, 3), max_features=10)

    # Fit and transform the text with the vectorizer
    tfidf_phrases = vectorizer.fit_transform(text_data)

    # Get the feature names (top 10 key phrases)
    feature_phrases = vectorizer.get_feature_names_out()


    # Add cluster names to metadata
    for i, doc in enumerate(metadata):
        doc['tf_idf'] = {}
        doc['tf_idf']['keywords'] = [feature_names[idx] for idx in tfidf[i].indices]
        doc['tf_idf']['key_phrases'] = [feature_phrases[idx] for idx in tfidf_phrases[i].indices]

    metadata = json.loads(json.dumps(metadata, default=lambda o: int(o) if isinstance(o, np.int32) else o))
    # Save the updated metadata JSON file
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

    return metadata
