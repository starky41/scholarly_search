import matplotlib.pyplot as plt
from wordcloud import WordCloud
import datetime
from collections import Counter
from textwrap import wrap


def create_wordcloud(data):
    # create a list of all the keywords
    all_keywords = [keyword for file in data if 'keyword' in file for keyword in file['keyword']]

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


def plot_articles_by_year(data, query_name):
    selection_size = len(data)
    years = [datetime.datetime.strptime(str(result['published']), '%Y-%m-%d %H:%M:%S%z').year for result in data]
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


def visualize_openaccess_ratio(data):
    """
    Visualizes the ratio between openaccess true and false papers in a list of dictionaries using matplotlib.

    Args:
    data (list): A list of dictionaries representing papers, each with an 'openaccess' key indicating whether the paper is open access or not.
    """
    # Calculate the number of openaccess true and false papers
    num_true = sum(d['openaccess'] == 'true' for d in data)
    num_false = len(data) - num_true

    # Calculate the percentage of openaccess true and false papers
    pct_true = num_true / len(data) * 100
    pct_false = num_false / len(data) * 100

    # Create a pie chart to visualize the ratio
    labels = [f"Open Access True ({num_true})", f"Open Access False ({num_false})"]
    sizes = [num_true, num_false]
    colors = ['#1f77b4', '#ff7f0e']
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
    plt.title('Ratio of Open Access True and False Papers')
    plt.axis('equal')
    plt.show()


def scatter_plot_citations(data):
    years = []
    citations = []
    for item in data:
        year = item['published_date']
        citation = item['citation_count']
        if year != "N/A" and citation != "N/A":
            years.append(year)
            citations.append(citation)

    plt.scatter(years, citations)
    plt.title("Publication Year vs. Citation count")
    plt.xlabel('Publication Year')
    plt.ylabel('Citation Count')
    plt.show()


def plot_subjects(data, n, query_name):
    selection_size = len(data)
    subjects = []
    for d in data:
        subjects += d['subjects']
    subject_counts = Counter(subjects)
    top_subjects = subject_counts.most_common(n)[::-1]  # Reverse order
    labels, values = zip(*top_subjects)

    # Wrap the subject labels
    max_label_len = max([len(label) for label in labels])
    wrapped_labels = [('\n'.join(wrap(label, width=max_label_len // 2))) for label in labels]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(wrapped_labels, values)
    ax.set_xlabel('Number of chapters')
    ax.set_title(f'Top {n} Subjects in papers')

    # Adjust font size and figure size to prevent overlap
    plt.rcParams.update({'font.size': 12})
    plt.tight_layout()
    plt.text(0.55, 0.125,
             f"Query: {query_name}\nSelection size: {selection_size}\nCreated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
             transform=plt.gca().transAxes, fontsize=10, verticalalignment='top',
             bbox=dict(facecolor='white', alpha=0.5))
    plt.show()


def plot_publishers(data, query_name, n=10):
    selection_size = len(data)
    publishers = []
    for d in data:
        publishers.append(d['publisher'])
    publisher_counts = Counter(publishers)
    top_publishers = publisher_counts.most_common(n)[::-1] # Reverse order
    labels, values = zip(*top_publishers)

    # Wrap the publisher labels
    max_label_len = max([len(label) for label in labels])
    wrapped_labels = [('\n'.join(wrap(label, width=max_label_len // 2))) for label in labels]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(wrapped_labels, values)
    ax.tick_params(axis='both', which='major', labelsize=8)
    ax.set_xlabel('Number of publications')
    ax.set_title(f'Top {n} Publishers')

    # Adjust font size and figure size to prevent overlap
    plt.rcParams.update({'font.size': 10})
    plt.tight_layout()

    # Display additional information on the plot
    plt.text(0.55, 0.125,
             f"Query: {query_name}\nSelection size: {selection_size}\nCreated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
             transform=plt.gca().transAxes, fontsize=10, verticalalignment='top',
             bbox=dict(facecolor='white', alpha=0.5))
    plt.show()

def plot_journals(data, query_name, n=10):
    selection_size = len(data)
    journals = []
    for d in data:
        journals.append(d['journal_name'])
    journal_counts = Counter(journals)
    top_journals = journal_counts.most_common(n)[::-1] # Reverse order
    labels, values = zip(*top_journals)

    # Wrap the publisher labels
    max_label_len = max([len(label) for label in labels])
    wrapped_labels = [('\n'.join(wrap(label, width=max_label_len // 2))) for label in labels]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(wrapped_labels, values)
    ax.tick_params(axis='both', which='major', labelsize=8)
    ax.set_xlabel('Number of publications')
    ax.set_title(f'Top {n} Journals')

    # Adjust font size and figure size to prevent overlap
    plt.rcParams.update({'font.size': 10})
    plt.tight_layout()

    # Display additional information on the plot
    plt.text(0.45, 0.125,
             f"Query: {query_name}\nSelection size: {selection_size}\nCreated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
             transform=plt.gca().transAxes, fontsize=10, verticalalignment='top',
             bbox=dict(facecolor='white', alpha=0.5))
    plt.show()