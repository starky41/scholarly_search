import arxiv_dl
import springer_dl
import services

from time import sleep


def main():
    QUERY = str(input('Enter your query >>> '))
    results = springer_dl.get_springer_results(QUERY, 1000)
    path = services.create_folder(QUERY)
    springer_dl.save_springer_results(path, results)
    keywords = springer_dl.find_keywords(QUERY, results, path)
    results = arxiv_dl.get_arxiv_results(QUERY, path, 20)
    arxiv_dl.save_arxiv_results(path, results)
    print(keywords)
    print('\n')
    for keyword in keywords:
        try:
            path = services.create_folder(f'keywords/{keyword}')
            print(f'\nDownloading data on {keyword}...')
            results = arxiv_dl.get_arxiv_results(keyword, path, 10)
            arxiv_dl.save_arxiv_results(path, results)
            sleep(3)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
    print('Done!')


