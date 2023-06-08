from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'starky',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

metadata_path = './output/metadata'
params = {
    'query': 'Classical music',
    'springer': {
        'max_metadata': 100,
        'max_pdfs': 5,
        'num_kw': 5,
        'path': metadata_path + '/springer.json',
    },
    'arxiv': {
        'main': {'max_metadata': 100, 'max_pdfs': 2},
        'kw': {'max_metadata': 100, 'max_pdfs': 2},
        'path': metadata_path + '/arxiv.json',
    },
    'crossref': {
        'max_metadata': 100,  # limited by 1000.
        'top_n': 10,
        'path': metadata_path + '/crossref.json',
        'top_path': metadata_path + '/crossref_top.json',
    }
}


def greet():
    from pathlib import Path
    import database
    import arxiv_dl
    import springer_dl
    import visualization
    import crossref_dl
    import kw_extraction

    Path('./output/metadata').mkdir(parents=True, exist_ok=True)
    Path('./output/visualizations').mkdir(parents=True, exist_ok=True)

    query = params['query']

    springer_results = springer_dl.get_springer_results(query, metadata_to_download=params['springer']['max_metadata'])
    springer_dl.download_papers(springer_results,
                                params['springer']['max_pdfs'])

    keywords = springer_dl.find_keywords(query,
                                         springer_results,
                                         max_kw=params['springer']['num_kw'])
    print(keywords)
    arxiv_results = arxiv_dl.get_arxiv_results(query,
                                               num_metadata_to_download=params['arxiv']['main']['max_metadata'],
                                               num_files_to_download=params['arxiv']['main']['max_pdfs'])

    kw_results = arxiv_dl.get_kw_results(
        keywords,
        num_metadata=params['arxiv']['kw']['max_metadata'],
        num_pdf_downloads=params['arxiv']['kw']['max_pdfs'],
        main_query=params['query']
    )
    crossref_results = crossref_dl.get_crossref_results(params['query'], max_results=params['crossref']['max_metadata'])
    crossref_dl.get_top_articles(input_file=params['crossref']['path'], top_n=params['crossref']['top_n'],
                                 output_file=params['crossref']['top_path'])

    visualization.create_visualizations(springer_results, arxiv_results, crossref_results, query)

    arxiv_results = kw_extraction.extract_keywords()

    database.add_record(name=query,
                        springer_data=springer_results,
                        arxiv_data=arxiv_results,
                        crossref_data=crossref_results,
                        kw_data=kw_results)


with DAG(
        default_args=default_args,
        dag_id='v39',
        description='Our first dag using python operator',
        start_date=datetime(2023, 6, 7),
        schedule='@daily'
) as dag:
    task1 = PythonOperator(
        task_id='scholarly_search',
        python_callable=greet
    )
    task1
