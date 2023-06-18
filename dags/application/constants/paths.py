from pathlib import Path

OUTPUT = './output'
METADATA_OUTPUT = f'{OUTPUT}/metadata'
API_KEY = './data'


def create_directories():
    directories = ['metadata', 'visualizations', 'arxiv_papers', 'springer_papers']
    for directory in directories:
        Path(f'{OUTPUT}/{directory}').mkdir(parents=True, exist_ok=True)
    print('Directories created successfully')


metadata_paths = {
    'arxiv': f'{METADATA_OUTPUT}/arxiv.json',
    'springer': f'{METADATA_OUTPUT}/springer.json',
    'crossref': f'{METADATA_OUTPUT}/crossref.json',
    'crossref_top': f'{METADATA_OUTPUT}/crossref_top.json'
}

paper_paths = {
    'arxiv': f'{OUTPUT}/arxiv_papers',
    'springer': f'{OUTPUT}/springer_papers'
}
