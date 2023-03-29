import os

import PyPDF2
import pyLDAvis
import pyLDAvis.gensim_models as gensimvis
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from gensim.models.phrases import Phrases, Phraser
from gensim.models.ldamodel import LdaModel
from gensim.corpora import Dictionary
import re



directory_path = './data/'

text_data = []
text = ''
for filename in os.listdir(directory_path):
    if filename.endswith('.pdf'):
        with open(os.path.join(directory_path, filename), 'rb') as pdf_file:


            try:
                # Create a PDF reader object
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                print(filename)
            except Exception as e:
                # handle the PdfReadError exception
                print(f"Error reading PDF file {pdf_file}: {e}")

            # Get the number of pages in the PDF document
            num_pages = len(pdf_reader.pages)

            # Loop through each page and extract the text
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                text_data.append(text)

            # print(text_data)

# Load the corpus of scientific papers



# Preprocess the text
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()


def preprocess(text):

    text = re.sub(r'\W+', ' ', text)
    text = re.sub(" \d+", " ", text)
    text = re.sub('(\\b[A-Za-z] \\b|\\b [A-Za-z]\\b)', '', text)
    tokens = word_tokenize(text.lower())
    # Tokenize the text and remove stop words
    tokens = [token for token in tokens if token not in stop_words]

    # Lemmatize the remaining words
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]

    return lemmatized_tokens


preprocessed_corpus = [preprocess(text) for text in text_data]




# Extract phrases
phrases = Phrases(preprocessed_corpus, min_count=5, threshold=10)
bigram = Phraser(phrases)

# Combine bigrams into multi-word expressions
for idx in range(len(preprocessed_corpus)):
    preprocessed_corpus[idx] = bigram[preprocessed_corpus[idx]]

# Create a dictionary and corpus for LDA
dictionary = Dictionary(preprocessed_corpus)
corpus = [dictionary.doc2bow(text) for text in preprocessed_corpus]

# Train LDA model
lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=10)

# Print the top 10 topics and their key phrases
vis = gensimvis.prepare(lda_model, corpus, dictionary)



# Display the visualization
pyLDAvis.save_html(vis, './lda_result2.html')

print('success!')