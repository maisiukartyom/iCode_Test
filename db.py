from pymongo import MongoClient
from pymongo.server_api import ServerApi


def connect_to_db():
    uri = "mongodb+srv://moyart:moyart@cluster0.db6cie9.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Успешное подключение к MongoDB!")
    except Exception as e:
        print(e)

    return client





