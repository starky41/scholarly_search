import arxiv_dl
import springer_dl
import services

from time import sleep


def main():
    QUERY = str(input('Enter your query >>> '))
    results = springer_dl.get_springer_results(QUERY, 200)
    path = services.create_folder(QUERY)
    springer_dl.save_springer_results(path, results)
    keywords = springer_dl.find_keywords(QUERY, results, path)
    results = arxiv_dl.get_arxiv_results(QUERY, path)
    arxiv_dl.save_arxiv_results(path, results)

    print('\n')
    for keyword in keywords:

        path = services.create_folder(f'keywords/{keyword}')
        print(f'Downloading data on {keyword}...')
        results = arxiv_dl.get_arxiv_results(keyword, path)
        arxiv_dl.save_arxiv_results(path, results)
        sleep(3)


if __name__ == '__main__':
    main()
    print('Done!')


