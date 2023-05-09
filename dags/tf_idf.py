import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import json

# Load the metadata into a pandas dataframe
json_path = "output/metadata/arxiv.json"
json_output = "output/metadata/arxiv_tf.json"
with open(json_path) as f:
    metadata = json.load(f)

#
# Extract the text data
text_data = []
for doc in metadata:
    text_data.append(doc['title'] + " " + doc['summary'])

# Define the TF-IDF vectorizer with top 10 keywords
vectorizer = TfidfVectorizer(stop_words='english', max_features=10)

# Fit and transform the text with the vectorizer
tfidf = vectorizer.fit_transform(text_data)

# Get the feature names (i.e., the top 10 keywords)
feature_names = vectorizer.get_feature_names()

# Define the TF-IDF vectorizer with top 10 key phrases
vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(2, 3), max_features=10)

# Fit and transform the text with the vectorizer
tfidf_phrases = vectorizer.fit_transform(text_data)

# Get the feature names (i.e., the top 10 key phrases)
feature_phrases = vectorizer.get_feature_names()

# Apply k-means clustering
kmeans_model = KMeans(n_clusters=5)
kmeans_model.fit(tfidf.toarray())

# Define cluster names based on keywords
cluster_names = {}
for i in range(5):
    cluster = kmeans_model.cluster_centers_[i]
    top_keywords = [feature_names[idx] for idx in cluster.argsort()[-10:]]
    name = " ".join(top_keywords)
    cluster_names[i] = name

# Add cluster names to metadata
for i, doc in enumerate(metadata):
    doc['tf_idf'] = {}
    doc['tf_idf']['keywords'] = [feature_names[idx] for idx in tfidf[i].indices]
    doc['tf_idf']['key_phrases'] = [feature_phrases[idx] for idx in tfidf_phrases[i].indices]
    doc['tf_idf']['cluster_name'] = cluster_names[kmeans_model.labels_[i]]
    doc['tf_idf']['cluster_number'] = kmeans_model.labels_[i]

metadata = json.loads(json.dumps(metadata, default=lambda o: int(o) if isinstance(o, np.int32) else o))
# Save the updated metadata JSON file
with open(json_output, 'w') as f:
    json.dump(metadata, f)