from pymongo.asynchronous.mongo_client import AsyncMongoClient
from pymongo.server_api import ServerApi

from bson.objectid import ObjectId

from config.config import get_mongodb_uri

from logger import Log
from constants import STANDARD_LOG_LEVEL

_log = Log("DBManager")
_log.getLogger().setLevel(STANDARD_LOG_LEVEL)
_log.write_logs_to_file()

# Create a new client and connect to the server
class DBManager:

    def __init__(self, db_name: str, collection_name: str = None):
        uri = get_mongodb_uri()
        self.client = AsyncMongoClient(uri, server_api=ServerApi('1'))

        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    async def create_collection(self, collection_name: str) -> bool:
        try:
            _log.getLogger().debug(f"Creating collection '{collection_name}' in the database '{self.db.name}'...")
            await self.db.create_collection(collection_name)
            _log.getLogger().debug(f"Collection '{collection_name}' created successfully!")
            return True
        except Exception as e:
            _log.getLogger().error(f"Something was happened in db_manager.create_collection(): {e}")
            print(e)
            return False

    async def insert_one_data(self, data: dict) -> ObjectId | None:
        try:
            _log.getLogger().debug(f"Inserting the data '{data}' in the '{self.collection.name}' collection...")
            result = (await self.collection.insert_one(data)).inserted_id

            if result is None:
                _log.getLogger().error(f"The '{data}' data was not written to the '{self.collection.name}' collection")
                return None
            
            return result
        except Exception as e:
            _log.getLogger().error(f"Something was happened in db_manager.insert_one_data(): {e}")
            print(e)

    async def insert_many_data(self, data: list) -> list[ObjectId] | None:
        try:
            _log.getLogger().debug(f"Inserting the data '{data}' in the '{self.collection.name}' collection...")
            result = (await self.collection.insert_many(data)).inserted_ids

            if result is None:
                _log.getLogger().error(f"The '{data}' data was not written to the '{self.collection.name}' collection")
                return None
            
            return result
        except Exception as e:
            _log.getLogger().error(f"Something was happened in db_manager.insert_many_data(): {e}")
            print(e)

    async def update_one_data(self, filter: dict, data: dict, upsert: bool = False) -> list[ObjectId] | None:
        try:
            _log.getLogger().debug(f"Updating the data '{data}' in the '{self.collection.name}' collection with filter '{filter}'...")
            result = await self.collection.update_one(filter, data, upsert)

            if result is None:
                _log.getLogger().error(f"The '{data}' data was not written to the '{self.collection.name}' collection")
                return None
            
            _log.getLogger().debug(f"Data updated or added")
            return result
        except Exception as e:
            _log.getLogger().error(f"Something was happened in db_manager.insert_many_data(): {e}")
            print(e)

    async def update_many_data(self, filter: dict, data: dict | list, upsert: bool = False) -> list[ObjectId] | None:
        try:
            _log.getLogger().debug(f"Updating the data '{data}' in the '{self.collection.name}' collection with filter '{filter}'...")
            result = await self.collection.update_many(filter, {"$set": data}, upsert)

            if result is None:
                _log.getLogger().error(f"The '{data}' data was not written to the '{self.collection.name}' collection")
                return None
            
            _log.getLogger().debug(f"Data updated or added")
            return result
        except Exception as e:
            _log.getLogger().error(f"Something was happened in db_manager.insert_many_data(): {e}")
            print(e)

    async def delete_one_data(self, filter: dict) -> bool:
        try:
            _log.getLogger().debug(f"Deleting the data by filter '{filter}' in the '{self.collection.name}' collection...")
            result = await self.collection.delete_one(filter)

            if result.deleted_count == 0:
                _log.getLogger().error(f"No data found to delete with filter '{filter}'")
                return False
            
            _log.getLogger().debug(f"Data deleted successfully")
            return True
        except Exception as e:
            _log.getLogger().error(f"Something was happened in db_manager.delete_one_data(): {e}")
            print(e)

    async def find_data_in_collection_by(self, find_by: dict) -> list:
        try:
            _log.getLogger().debug(f"Find data in the '{self.collection.name}' collection by '{find_by}'")
            data = [d async for d in self.collection.find(find_by)]

            if data is None:
                _log.getLogger().error(f"No data in this collection by '{find_by}'")
                return {}
            
            _log.getLogger().debug(f"Data in the '{self.collection.name}' collection received by filter '{find_by}'!")

            return data
        except Exception as e:
            _log.getLogger().error(f"Something was happened in db_manager.find_data_in_collection_by(): {e}")
            print(e)

    async def get_all_data_in_collection(self) -> list:
        try:
            data = [d async for d in self.collection.find()]

            if data is None:
                _log.getLogger().error(f"No data in this collection")
                return []
            
            _log.getLogger().debug(f"Data from the '{self.collection.name}' collection received! Quantity: {len(data)}")
            
            return data
        except Exception as e:
            _log.getLogger().error(f"Something was happened in db_manager.get_all_data_in_collection(): {e}")
            print(e)

    async def get_count_of_all_documents(self) -> int:
        try:
            _log.getLogger().debug(f"Getting the number of all documents in the collection '{self.collection.name}'...")
            count = await self.collection.count_documents({})

            if count is None:
                _log.getLogger().error("Data not received or missing")
                return 0
            
            _log.getLogger().debug(f"Number of documents received! Values: {count}")
            return count
        except Exception as e:
            _log.getLogger().error(f"Something was happened in db_manager.get_count_of_all_documents(): {e}")
            print(e)

    async def get_count_documents_by_filter(self, data: dict) -> int:
        try:
            _log.getLogger().debug(f"Getting the number of documents by filter in the collection '{self.collection.name}'...")
            count = await self.collection.count_documents(data)

            if count is None:
                _log.getLogger().error("Data not received or missing")
                return 0
            
            _log.getLogger().debug(f"Number of documents by filter received! Values: {count}")
            return count
        except Exception as e:
            _log.getLogger().error(f"Something was happened in db_manager.get_count_documents_by_filter(): {e}")
            print(e)

    async def get_collections(self) -> list:
        try:
            _log.getLogger().debug(f"Getting all collections from the '{self.db.name}' database...")
            collections = await self.db.list_collection_names()

            if collections is None:
                _log.getLogger().error(f"Collections is empty: {collections}")
                return []

            _log.getLogger().debug(f"Collections successfully received: {collections}")

            return collections
        except Exception as e:
            _log.getLogger().error(f"Something was happened in db_manager.get_collections(): {e}")
            print(e)

    # Send a ping to confirm a successful connection (took from MongoDB Documentation)
    async def test_connection(self):
        try:
            _log.getLogger().debug("Starting ping...")

            await self.client.admin.command('ping')

            _log.getLogger().debug("Pinged your deployment. You successfully connected to MongoDB!")
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            _log.getLogger().error(f"Something was happened in db_manager.test_connection(): {e}")
            print(e)

    def get_database_name(self) -> str:
        return self.db.name
    