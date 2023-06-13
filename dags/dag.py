from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from constants import params
import json
import arxiv_downloader
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
        springer_results = springer_dl.get_springer_results(params['query'],
                                                            metadata_to_download=params['springer']['max_metadata'])
        return springer_results


class GetKeywordsOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        import springer_dl
        from constants import params
        springer_results = context['ti'].xcom_pull(task_ids='springer_download_task')
        keywords = springer_dl.find_keywords(params['query'], springer_results, max_kw=params['springer']['num_kw'])
        print(keywords)
        return keywords


class ArxivDownloadOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        arxiv_results = arxiv_downloader.search_and_download_arxiv_papers(save_to_json=False)

        # create custom JSON encoder that converts datetime to ISO-format string
        class CustomJSONEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, datetime):
                    return o.isoformat()
                return super().default(o)

        # serialize data using custom JSON encoder
        serialized_results = json.dumps(arxiv_results, cls=CustomJSONEncoder)

        # set serialized data to XCom variable
        context['ti'].xcom_push(key='arxiv_results', value=serialized_results)

        return serialized_results

class ArxivDownloadKeywordsMetadataOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=self.execute, *args, **kwargs)

    def execute(self, context):
        keywords = context['ti'].xcom_pull(task_ids='get_keywords_task')
        kw_results = arxiv_downloader.query_arxiv_keywords(keywords,
                                                           params['arxiv']['kw']['max_metadata'],
                                                           params['arxiv']['kw']['max_pdfs'])
        # create custom JSON encoder that converts datetime to ISO-format string
        class CustomJSONEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, datetime):
                    return o.isoformat()
                return super().default(o)

        # serialize data using custom JSON encoder
        serialized_results = json.dumps(kw_results, cls=CustomJSONEncoder)

        # set serialized data to XCom variable
        context['ti'].xcom_push(key='kw_results', value=serialized_results)

        return serialized_results

# class ProcessArxivOperator(PythonOperator):
#     def execute(self, context):
#         serialized_results = context['ti'].xcom_pull(key='arxiv_results')
#
#         # deserialize JSON string into Python object
#         arxiv_results = json.loads(serialized_results,
#                                    object_hook=lambda d: {k: parser.parse(v) if isinstance(v, str) and ':' in v else v
#                                                           for k, v in d.items()})
#
#         # process the arxiv results as needed
#         # ...
#
#         return arxiv_results


with DAG(
        default_args=default_args,
        dag_id='dv32',
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

    op_create_directories >> springer_download_task >> get_keywords_task >> arxiv_download_task >> arxiv_download_keywords_metadata
