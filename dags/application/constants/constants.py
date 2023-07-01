from .paths import metadata_paths

params = {
    'query': 'Machine learning in spam detection',
    'springer': {
        'max_metadata': 1000,
        'max_pdfs': 1,
        'num_kw': 1,
        'path': metadata_paths['springer'],
    },
    'arxiv': {
        'main': {'max_metadata': 100, 'max_pdfs': 1},
        'kw': {'max_metadata': 100, 'max_pdfs': 0},
        'path': metadata_paths['arxiv'],
    },
    'crossref': {
        'max_metadata': 100,  # limited by 1000.
        'top_n': 3,
        'path': metadata_paths['crossref'],
        'top_path': metadata_paths['crossref_top']
    }
}
