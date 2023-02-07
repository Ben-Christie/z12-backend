import pymongo
import os
from dotenv import load_dotenv

# load .env file to access variables
load_dotenv()

# dotenv variables
username = os.getenv('MONGO_USERNAME')
password = os.getenv('MONGO_PASSWORD')
host = os.getenv('MONGO_HOST')
privileges = os.getenv('MONGO_USER_PRIVILEGES')

connection_string = f"mongodb+srv://{username}:{password}@{host}?{privileges}"

# set a 10-second connection timeout
client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=10000)

try:
    print(
        f'Connection to MongoDB Established Successfully:\n[{client.server_info()}]')

    print(client.server_info())
except Exception as e:
    print(
        f"The following error occurred when trying to connect to the database:\n{e}")

db = client['z12_performance_database']
