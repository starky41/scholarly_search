from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'starky',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}


def greet():
    from constants import params
    from visualization import create_visualizations
    from paths import create_directories
    from kw_extraction import extract_keywords
    import database
    import arxiv_dl
    import springer_dl
    import crossref_dl

    create_directories()
    query = params['query']

    springer_results = springer_dl.get_springer_results(query, metadata_to_download=params['springer']['max_metadata'])

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
    crossref_results = crossref_dl.get_crossref_results(query, max_results=params['crossref']['max_metadata'])
    crossref_dl.get_top_articles(input_file=params['crossref']['path'], top_n=params['crossref']['top_n'],
                                 output_file=params['crossref']['top_path'])

    create_visualizations(springer_results, arxiv_results, crossref_results, query)

    arxiv_results = extract_keywords()

    database.add_record(name=query,
                        springer_data=springer_results,
                        arxiv_data=arxiv_results,
                        crossref_data=crossref_results,
                        kw_data=kw_results)


with DAG(
        default_args=default_args,
        dag_id='v46',
        description='Our first dag using python operator',
        start_date=datetime(2023, 6, 7),
        schedule='@daily'
) as dag:
    task1 = PythonOperator(
        task_id='scholarly_search',
        python_callable=greet
    )
    task1
