import arxiv_dl
import springer_dl
import services
import database

from time import sleep


def main():
    QUERY = str(input('Enter your query >>> '))
    springer_results = springer_dl.get_springer_results(QUERY, 200)
    path = services.create_folder(QUERY)
    keywords = springer_dl.find_keywords(QUERY, springer_results)

    print(keywords)
    print('\n')
    arxiv_results = arxiv_dl.get_arxiv_results(QUERY, path, 3)
    kw_results = []
    for idx, keyword in enumerate(keywords):
        try:
            path = services.create_folder(f'keywords/{keyword}')
            print(f'\nDownloading data on {keyword}...')
            arxiv_results = arxiv_dl.get_arxiv_results(keyword, path, 2)
            kw_results.append({'keyword': f'{keyword}',
                               'arxiv': {
                                   'metadata': arxiv_results
                               }
                               })

            sleep(3)
        except Exception as e:
            print(e)

    database.add_record(name=QUERY,
                        springer_data=springer_results,
                        arxiv_data=arxiv_results,
                        kw_data=kw_results)


if __name__ == '__main__':
    main()
    print('Done!')
