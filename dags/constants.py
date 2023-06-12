from paths import metadata_paths

params = {
    'query': 'Quantum Physics',
    'springer': {
        'max_metadata': 100,
        'max_pdfs': 2,
        'num_kw': 5,
        'path': metadata_paths['springer'],
    },
    'arxiv': {
        'main': {'max_metadata': 100, 'max_pdfs': 2},
        'kw': {'max_metadata': 100, 'max_pdfs': 2},
        'path': metadata_paths['arxiv'],
    },
    'crossref': {
        'max_metadata': 100,  # limited by 1000.
        'top_n': 3,
        'path': metadata_paths['crossref'],
        'top_path': metadata_paths['crossref_top']
    }
}
