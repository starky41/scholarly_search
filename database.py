import datetime
from pymongo import MongoClient
import gridfs

def mongo_conn():
    try:
        cluster = 'mongodb+srv://starky:xe97u5wDMS2kcZry@cluster0.jfbfflp.mongodb.net/scholarly_search_db?retryWrites=true&w=majority'
        client = MongoClient(cluster)
        print(client.list_database_names())
        return client.scholarly_search_db
    except Exception as e:
        print('Error in MongoDB connection', e)


db = mongo_conn()
print(db.list_collection_names())


def upload_pdf(filename):
    with open(f'./data/{filename}', 'rb') as f:
        fs = gridfs.GridFS(db)
        fs.put(f, filename=filename)
        print('upload completed')


def add_record(name, springer_data, arxiv_data, kw_data):
    result = queries.delete_many({})
    db_record = {"name": name,
                 "datetime": datetime.datetime.utcnow(),
                 'data': {'query': {'springer': springer_data,
                                    'arxiv':
                                        {
                                            'metadata': arxiv_data
                                        }
                                    },

                          'keywords': kw_data
                          }
                 }

    result = queries.insert_one(db_record)

    print(result)
    return result


queries = db.metadata
