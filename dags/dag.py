from datetime import datetime, timedelta
import pandas
from airflow import DAG
from airflow.operators.python import PythonOperator
import springer_dl
import arxiv_dl
import database
import arxiv
import pymongo

from pathlib import Path
default_args = {
    'owner': 'starky',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}


def greet():
    print('Hello World!')
    print(f'pandas version is {pandas.__version__}')
    query = 'clown fish'
    springer_results = springer_dl.get_springer_results(query, results_to_get=200)
    keywords = springer_dl.find_keywords(query, springer_results, max_kw=2)
    print(keywords)
    arxiv_results = arxiv_dl.get_arxiv_results(query, 2)
    kw_results = arxiv_dl.get_kw_results(keywords)
    database.add_record(name=query,
                        springer_data=springer_results,
                        arxiv_data=arxiv_results,
                        kw_data=kw_results)

with DAG(
        default_args=default_args,
        dag_id='check_dag11',
        description='Our first dag using python operator',
        start_date=datetime(2023, 1, 13),
        schedule='@daily'
) as dag:
    task1 = PythonOperator(
        task_id='greet',
        python_callable=greet
    )
    task1
