import arxiv_dl
import springer_dl
import services


def main():
    QUERY = str(input('Enter your query >>> '))
    results = springer_dl.get_springer_results(QUERY, 200)
    path = services.create_folder(QUERY)
    springer_dl.save_springer_results(path, results)
    springer_dl.find_keywords(QUERY, results, path)
    results = arxiv_dl.get_arxiv_results(QUERY)
    arxiv_dl.save_arxiv_results(path, results)


if __name__ == '__main__':
    main()
    print('Done!')


