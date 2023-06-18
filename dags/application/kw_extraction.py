import json
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer

try:
    from application.downloaders.arxiv_downloader import dump_to_json
except ModuleNotFoundError:
    from dags.application.downloaders.arxiv_downloader import dump_to_json

# Custom JSON encoder that can handle datetime objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        return json.JSONEncoder.default(self, obj)


def extract_keywords(metadata):

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

    # Serialize with custom JSON encoder
    metadata = json.loads(json.dumps(metadata, cls=CustomJSONEncoder))

    # Save the updated metadata JSON file
    dump_to_json(metadata)

    return metadata