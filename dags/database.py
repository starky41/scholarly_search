import datetime
from pymongo import MongoClient
import gridfs


def mongo_conn():
    try:
        cluster = 'mongodb+srv://starky:xe97u5wDMS2kcZry@cluster0.jfbfflp.mongodb.net/scholarly_search_db?retryWrites=true&w=majority'
        client = MongoClient(cluster)
        print(f'Databases: {client.list_database_names()}')
        print(f'Collections: {client.scholarly_search_db.list_collection_names()}')
        return client.scholarly_search_db
    except Exception as e:
        print('Error in MongoDB connection', e)


db = mongo_conn()



def upload_file(filename):
    with open(f'./output/{filename}', 'rb') as f:
        fs = gridfs.GridFS(db)
        fs.put(f, filename=filename)
        print('Upload complete')


def add_record(name, springer_data, arxiv_data, crossref_data, kw_data):
    result = queries.delete_many({})
    db_record = {"name": name,
                 "datetime": datetime.datetime.utcnow(),
                 'data': {'query': {'springer': springer_data,
                                    'arxiv':
                                        {
                                            'metadata': arxiv_data
                                        },
                                    'crossref': crossref_data,
                                    },

                          'keywords': kw_data
                          }
                 }

    result = queries.insert_one(db_record)

    print(result)
    return result

try:
    queries = db.metadata
    print('CONNECTED')
except AttributeError:
    print("Your IP address is not in the database white list, therefore the data will not be saved!")
