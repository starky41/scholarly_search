from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

default_args = {
    'owner': 'starky',
    'retries': 5,
    'retry_delay': timedelta(minutes=5),
    'executor': 'LocalExecutor',
}


def create_directories():
    from paths import create_directories
    create_directories()


class SpringerDownloadOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        import springer_dl
        springer_results = springer_dl.get_springer_results()
        context['ti'].xcom_push(key='springer_results', value=springer_results)
        return springer_results


class GetKeywordsOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        import springer_dl
        springer_results = context['ti'].xcom_pull(task_ids='springer_download_task')
        keywords = springer_dl.find_keywords(springer_results)
        print(keywords)

        return keywords


class ArxivDownloadOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        from arxiv_downloader import serialize, search_and_download_arxiv_papers
        arxiv_results = search_and_download_arxiv_papers(save_to_json=False)
        serialized_results = serialize(arxiv_results)

        context['ti'].xcom_push(key='arxiv_results', value=serialized_results)

        return serialized_results


class ArxivDownloadKeywordsMetadataOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        from arxiv_downloader import query_arxiv_keywords, serialize
        keywords = context['ti'].xcom_pull(task_ids='get_keywords_task')
        kw_results = query_arxiv_keywords(keywords)
        serialized_results = serialize(kw_results)
        context['ti'].xcom_push(key='kw_results', value=serialized_results)
        return serialized_results


with DAG(
        default_args=default_args,
        dag_id='dv47',
        description='Our first dag using python operator',
        start_date=datetime(2023, 6, 7),
        schedule='@once'

) as dag:
    op_create_directories = PythonOperator(task_id='create_directories', python_callable=create_directories)
    springer_download_task = SpringerDownloadOperator(
        task_id='springer_download_task',
        dag=dag
    )
    get_keywords_task = GetKeywordsOperator(
        task_id='get_keywords_task',
        dag=dag
    )
    arxiv_download_task = ArxivDownloadOperator(
        task_id='arxiv_download_task',
        dag=dag
    )
    arxiv_download_keywords_metadata = ArxivDownloadKeywordsMetadataOperator(
        task_id='arxiv_download_keywords_metadata',
        dag=dag
    )

    op_create_directories >> [arxiv_download_task, springer_download_task] >> \
    get_keywords_task >> arxiv_download_keywords_metadata
