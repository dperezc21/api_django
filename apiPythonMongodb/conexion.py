from pymongo import MongoClient
from decouple import config

def conexion():
    URL_MONGODB=config('URL_MONGODB')
    con = MongoClient(URL_MONGODB)
    database = con["api_paises"]
    return database

