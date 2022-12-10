import datetime
from pymongo import MongoClient
import springer_dl
import arxiv_dl

cluster = 'mongodb+srv://starky:xe97u5wDMS2kcZry@cluster0.jfbfflp.mongodb.net/scholarly_search_db?retryWrites=true&w=majority'

client = MongoClient(cluster)

print(client.list_database_names())

db = client.scholarly_search_db

print(db.list_collection_names())


def add_record(name, springer_data, arxiv_data, kw_data):
    result = queries.delete_many({})
    db_record = {"name": name,
                 "datetime": datetime.datetime.utcnow(),
                 'data': {'query': {'springer': springer_data,
                                    'arxiv':
                                        {
                                            'metadata': arxiv_data,
                                            'articles': [{'list of pdfs': 'list_of_pdfs'}]
                                        }
                                    },

                          'keywords': kw_data
                          }
                 }


    result = queries.insert_one(db_record)
    print(result)
    return result


queries = db.metadata

# def db_save(query, springer_results, arxiv_results, keywords):
#
#     search_results = {"name": query,
#              "datetime": datetime.datetime.utcnow(),
#              'data': {'main_term': {'springer': springer_results,
#                                     'arxiv':
#                                         {
#                                             'metadata': arxiv_results,
#                                             'articles': [{'list of pdfs': 'list_of_pdfs'}]
#                                         }
#                                     },
#
#                       'keywords': {'keywords': keywords,
#                                    '0': {'keyword': 'machine learning',
#                                          'arxiv': {
#                                              'metadata': './arxiv.csv',
#                                              'articles': [{'list_of_pdfs': 'list_of_pdfs'}]
#                                          }
#                                          }
#                                    }
#                       }
#                       }
