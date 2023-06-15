from datetime import timedelta
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
        print(keywords)
        kw_results = query_arxiv_keywords(keywords)
        serialized_results = serialize(kw_results)
        context['ti'].xcom_push(key='kw_results', value=serialized_results)
        return serialized_results


class CrossrefDownloadOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        from crossref_dl import get_crossref_results
        crossref_results = get_crossref_results()
        context['ti'].xcom_push(key='crossref_results', value=crossref_results)
        return crossref_results


class CrossrefTopResultsOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        from crossref_dl import get_top_articles
        crossref_results = context['ti'].xcom_pull(task_ids='crossref_download_task')
        crossref_top_results = get_top_articles(crossref_results)

        context['ti'].xcom_push(key='crossref_top_results', value=crossref_top_results)
        return crossref_results


class CreateVisualisationsOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        from visualization import create_visualizations
        import json
        springer_results = context['ti'].xcom_pull(task_ids='springer_download_task')
        crossref_results = context['ti'].xcom_pull(task_ids='crossref_download_task')

        serialized_arxiv_results = context['ti'].xcom_pull(task_ids='arxiv_download_task')
        arxiv_results = json.loads(serialized_arxiv_results)
        create_visualizations(springer_results, arxiv_results, crossref_results)


class KeywordExtractionOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        import json
        from kw_extraction import extract_keywords
        serialized_arxiv_results = context['ti'].xcom_pull(task_ids='arxiv_download_task')
        arxiv_results = json.loads(serialized_arxiv_results)

        extract_keywords(arxiv_results)


with DAG(
        default_args=default_args,
        dag_id='dv64',
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
    crossref_download_task = CrossrefDownloadOperator(
        task_id='crossref_download_task',
        dag=dag
    )
    crossref_get_top_results_task = CrossrefTopResultsOperator(
        task_id='crossref_get_top_results_task',
        dag=dag
    )
    create_visualizations_task = CreateVisualisationsOperator(
        task_id='create_visualizations_task',
        dag=dag
    )
    extract_keywords_task = KeywordExtractionOperator(
        task_id='extract_keywords_task',
        dag=dag
    )

    # op_create_directories >> [arxiv_download_task, springer_download_task, crossref_download_task] >> \
    # get_keywords_task >> arxiv_download_keywords_metadata >> crossref_get_top_results_task

    op_create_directories >> [arxiv_download_task, springer_download_task, crossref_download_task]
    springer_download_task >> get_keywords_task
    get_keywords_task >> arxiv_download_keywords_metadata
    [arxiv_download_task, springer_download_task] >> arxiv_download_keywords_metadata
    crossref_download_task >> crossref_get_top_results_task
    [arxiv_download_task, crossref_download_task, springer_download_task] >> create_visualizations_task
    arxiv_download_task >> extract_keywords_task
