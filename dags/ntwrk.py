import os
import PyPDF2
import spacy
import networkx as nx
import matplotlib.pyplot as plt
import re

# Load the spaCy English model
nlp = spacy.load('en_core_web_sm')

# Define a function to preprocess the text and extract citations
def preprocess_and_extract_citations(text):
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    text = ' '.join(tokens)
    matches = re.findall(r'\([A-Za-z]*\d{4}[a-z]?\)', text)
    citations = [match[1:-1] for match in matches]

    print(citations)
    return text, citations

# Define a function to create a network from the corpus
def create_network(directory_path):
    # Initialize the network
    G = nx.Graph()

    # Loop through each file in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.pdf'):
            with open(os.path.join(directory_path, filename), 'rb') as pdf_file:
                # Convert the PDF to text and preprocess it
                try:
                    # Create a PDF reader object
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    print(filename)
                except Exception as e:
                    # handle the PdfReadError exception
                    print(f"Error reading PDF file {pdf_file}: {e}")
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text()
                text, citations = preprocess_and_extract_citations(text)

                # Add the article to the network
                G.add_node(filename, text=text)

                # Add edges to the network for each citation
                for citation in citations:
                    if citation in G.nodes:
                        G.add_edge(filename, citation)

    return G

# Define a function to visualize the network
# def visualize_network(G):
#     # Set node labels
#     node_labels = {node: node.split('.')[0] for node in G.nodes}
#
#     # Set edge labels
#     edge_labels = {}
#     for edge in G.edges:
#         source = edge[0].split('.')[0]
#         target = edge[1].split('.')[0]
#         if source not in edge_labels:
#             edge_labels[source] = {}
#         edge_labels[source][target] = ''
#
#     # Draw the network with labels
#     pos = nx.spring_layout(G, seed=42)
#     nx.draw(G, pos=pos, node_size=800, with_labels=True, labels=node_labels)
#     nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels, font_size=7)
#     plt.show()

def visualize_network(G):
    pos = nx.spring_layout(G, k=0.15)
    nx.draw(G, pos, node_size=50, with_labels=False)

    # Add labels to nodes
    labels = {}
    for node in G.nodes:
        labels[node] = node.split('.')[0]
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_color='black', font_family='serif', verticalalignment='center')

    # Draw edges
    nx.draw_networkx_edges(G, pos, width=0.5, alpha=0.5)

    # Show the plot
    plt.show()

# Example usage
directory_path = './data'
G = create_network(directory_path)
visualize_network(G)