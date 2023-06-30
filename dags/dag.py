from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import json

default_args = {
    'owner': 'starky',
    'retries': 5,
    'retry_delay': timedelta(minutes=5),
    'executor': 'LocalExecutor',
}


def create_directories():
    from application.constants.paths import create_directories
    create_directories()


class SpringerDownloadMetadataOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        from application.downloaders import springer_downloader
        springer_results = springer_downloader.get_springer_results()
        context['ti'].xcom_push(key='springer_results', value=springer_results)
        return springer_results


class SpringerDownloadPdfFilesOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        from application.downloaders.springer_downloader import download_papers
        springer_results = context['ti'].xcom_pull(task_ids='springer_download_metadata_task')
        download_papers(springer_results)


class GetKeywordsOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        from application.downloaders.springer_downloader import find_keywords
        springer_results = context['ti'].xcom_pull(task_ids='springer_download_metadata_task')
        keywords = find_keywords(springer_results)
        print(keywords)

        return keywords


class ArxivDownloadMetadataOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        from application.downloaders.arxiv_downloader import serialize, search_and_download_arxiv_papers
        arxiv_results = search_and_download_arxiv_papers(save_to_json=False, download_files=False)
        serialized_results = serialize(arxiv_results)

        context['ti'].xcom_push(key='arxiv_results', value=serialized_results)

        return serialized_results


class ArxivDownloadPdfFilesOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        from application.downloaders.arxiv_downloader import download_pdf_files, query_arxiv
        search = query_arxiv()
        download_pdf_files(search)


class ArxivDownloadKeywordsMetadataOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        from application.downloaders.arxiv_downloader import query_arxiv_keywords, serialize
        keywords = context['ti'].xcom_pull(task_ids='get_keywords_task')
        print(keywords)
        kw_results = query_arxiv_keywords(keywords)
        serialized_results = serialize(kw_results)
        context['ti'].xcom_push(key='kw_results', value=serialized_results)
        return serialized_results


class ArxivDownloadKeywordsPdfFilesOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        from application.constants.constants import params
        from application.downloaders.arxiv_downloader import download_pdf_files, query_arxiv
        keywords = context['ti'].xcom_pull(task_ids='get_keywords_task')
        for keyword in keywords:
            search_term = f"{keyword} AND {params['query']}"
            print(f"Looking for files on >> {search_term}")
            search = query_arxiv(search_term, params['arxiv']['kw']['max_metadata'])
            download_pdf_files(search)


class CrossrefDownloadOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        from application.downloaders.crossref_downloader import get_crossref_results
        crossref_results = get_crossref_results()
        context['ti'].xcom_push(key='crossref_results', value=crossref_results)
        return crossref_results





class CreateVisualisationsOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        from application.visualization import create_visualizations
        import json
        springer_results = context['ti'].xcom_pull(task_ids='springer_download_metadata_task')
        crossref_results = context['ti'].xcom_pull(task_ids='crossref_download_task')

        serialized_arxiv_results = context['ti'].xcom_pull(task_ids='arxiv_download_metadata_task')
        arxiv_results = json.loads(serialized_arxiv_results)
        create_visualizations(springer_results, arxiv_results, crossref_results)


class KeywordExtractionOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        import json
        from application.kw_extraction import extract_keywords
        from application.downloaders.arxiv_downloader import serialize
        serialized_arxiv_results = context['ti'].xcom_pull(task_ids='arxiv_download_metadata_task')
        arxiv_results = json.loads(serialized_arxiv_results)
        arxiv_results_with_keywords = extract_keywords(arxiv_results)
        arxiv_results_with_keywords = serialize(arxiv_results_with_keywords)
        context['ti'].xcom_push(key='arxiv_results_with_keywords', value=arxiv_results_with_keywords)
        return arxiv_results_with_keywords


class RankPapersOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        from application.ranking import get_top_papers
        crossref_results = context['ti'].xcom_pull(task_ids='crossref_download_task')
        ranked_papers = get_top_papers(crossref_results)
        context['ti'].xcom_push(key='ranked_papers', value=ranked_papers)
        return ranked_papers


class DatabaseAddRecordOperator(PythonOperator):

    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        from application import database
        springer_results = context['ti'].xcom_pull(task_ids='springer_download_metadata_task')
        serialized_arxiv_results = context['ti'].xcom_pull(task_ids='extract_keywords_task')
        arxiv_results = json.loads(serialized_arxiv_results)
        crossref_results = context['ti'].xcom_pull(task_ids='crossref_download_task')
        ranked_papers = context['ti'].xcom_pull(task_ids='rank_papers_task')
        serialized_kw_data = context['ti'].xcom_pull(task_ids='arxiv_download_keywords_metadata')
        kw_data = json.loads(serialized_kw_data)
        database.add_record(springer_results, arxiv_results, crossref_results, kw_data, ranked_papers)


with DAG(
        default_args=default_args,
        dag_id='v144',
        description='Our first dag using python operator',
        start_date=datetime(2023, 6, 7),
        schedule='@once'

) as dag:
    op_create_directories = PythonOperator(task_id='create_directories', python_callable=create_directories)
    springer_download_metadata_task = SpringerDownloadMetadataOperator(
        task_id='springer_download_metadata_task',
        dag=dag
    )
    springer_download_pdfs_task = SpringerDownloadPdfFilesOperator(
        task_id='springer_download_pdfs_task',
        dag=dag
    )
    get_keywords_task = GetKeywordsOperator(
        task_id='get_keywords_task',
        dag=dag
    )
    arxiv_download_metadata_task = ArxivDownloadMetadataOperator(
        task_id='arxiv_download_metadata_task',
        dag=dag
    )
    arxiv_download_pdf_files_task = ArxivDownloadPdfFilesOperator(
        task_id='arxiv_download_pdfs_task',
        dag=dag
    )
    arxiv_download_keywords_metadata = ArxivDownloadKeywordsMetadataOperator(
        task_id='arxiv_download_keywords_metadata',
        dag=dag
    )
    arxiv_download_keywords_pdf_files_task = ArxivDownloadKeywordsPdfFilesOperator(
        task_id='arxiv_download_keywords_pdfs_task',
        dag=dag
    )
    crossref_download_task = CrossrefDownloadOperator(
        task_id='crossref_download_task',
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
    rank_papers_task = RankPapersOperator(
        task_id='rank_papers_task',
        dag=dag
    )
    database_add_record_task = DatabaseAddRecordOperator(
        task_id='database_add_record_task',
        dag=dag
    )

    op_create_directories >> [arxiv_download_metadata_task, springer_download_metadata_task, crossref_download_task]
    springer_download_metadata_task >> get_keywords_task
    springer_download_metadata_task >> springer_download_pdfs_task
    get_keywords_task >> arxiv_download_keywords_metadata
    [arxiv_download_metadata_task, springer_download_metadata_task] >> arxiv_download_keywords_metadata
    [arxiv_download_metadata_task, crossref_download_task,
     springer_download_metadata_task] >> create_visualizations_task
    arxiv_download_metadata_task >> extract_keywords_task
    arxiv_download_keywords_metadata >> rank_papers_task
    rank_papers_task >> database_add_record_task
    arxiv_download_metadata_task >> arxiv_download_pdf_files_task
    arxiv_download_keywords_metadata >> arxiv_download_keywords_pdf_files_task
