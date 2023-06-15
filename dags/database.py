import datetime
from pymongo import MongoClient
import gridfs
import os
from constants import params

def mongo_conn():
    try:
        # cluster = 'mongodb+srv://starky:xe97u5wDMS2kcZry@cluster0.jfbfflp.mongodb.net/scholarly_search_db?retryWrites=true&w=majority'
        cluster = 'mongodb://192.168.0.119:27017/'
        client = MongoClient(cluster)
        print(f'Databases: {client.list_database_names()}')
        print(f'Collections: {client.scholarly_search_db.list_collection_names()}')
        return client.scholarly_search_db
    except Exception as e:
        print('Error in MongoDB connection', e)


def upload_file(filename):
    with open(f'./output/{filename}', 'rb') as f:
        fs.put(f, filename=filename)
        print('Upload complete')


def png_to_bson(path='./output/visualizations'):
    png_files = [f for f in os.listdir(path) if f.endswith('.png')]
    documents = []
    for png_file in png_files:
        with open(os.path.join(path, png_file), 'rb') as f:
            png_bytes = f.read()
        document = {
            'name': png_file,
            'data': png_bytes,
            'type': 'image/png'
        }
        documents.append(document)

    return documents


def add_record(springer_data, arxiv_data, crossref_data, kw_data, query=params['query']):
    result = queries.delete_many({})
    visualizations = png_to_bson()
    db_record = {"name": query,
                 "datetime": datetime.datetime.utcnow(),
                 'data': {'query': {'springer': springer_data,
                                    'arxiv':
                                        {
                                            'metadata': arxiv_data
                                        },
                                    'crossref': crossref_data,
                                    },

                          'keywords': kw_data,
                          'visualizations': visualizations
                          }
                 }

    result = queries.insert_one(db_record)

    print(result)
    return result


db = mongo_conn()
fs = gridfs.GridFS(db)

try:
    queries = db.metadata
    print('CONNECTED')
except AttributeError:
    print("Your IP address is not in the database white list, therefore the data will not be saved!")


