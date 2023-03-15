
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

import datetime
def create_wordcloud(json):
    # create a list of all the keywords
    all_keywords = [keyword for file in json if 'keyword' in file for keyword in file['keyword']]

    # join all the keywords into a single string
    all_keywords_str = ' '.join(all_keywords)

    # generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_keywords_str)

    # plot the word cloud
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Most Frequent Keywords')
    plt.show()

# def plot_articles_by_year(results):
#     years = [datetime.datetime.strptime(str(result['published']), '%Y-%m-%d %H:%M:%S%z').year for result in results]
#     plt.hist(years, bins=range(min(years), max(years)+2), align='left', rwidth=0.8)
#     plt.xticks(range(min(years), max(years)+1, 2), rotation=45, ha='right')
#     plt.xlabel('Year')
#     plt.ylabel('Number of Articles')
#     plt.title('Distribution of Articles by Year')
#     plt.show()

import datetime
import matplotlib.pyplot as plt


def plot_articles_by_year(results, query_name):
    selection_size = len(results)
    years = [datetime.datetime.strptime(str(result['published']), '%Y-%m-%d %H:%M:%S%z').year for result in results]
    plt.hist(years, bins=range(min(years), max(years) + 2), align='left', rwidth=0.8)
    plt.xticks(range(min(years), max(years) + 1, 2), rotation=45, ha='right')
    plt.xlabel('Year')
    plt.ylabel('Number of Articles')
    plt.title('Distribution of Articles by Year')

    # Add additional information
    plt.text(0.02, 0.95,
             f"Query: {query_name}\nSelection size: {selection_size}\nCreated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
             transform=plt.gca().transAxes, fontsize=10, verticalalignment='top',
             bbox=dict(facecolor='white', alpha=0.5))

    plt.show()