import json
from appwrite.services.storage import Storage
from core.config import settings
from appwrite.client import Client
from appwrite.services.databases import Databases

appwrite_client = Client()
appwrite_client.set_endpoint(settings.APPWRITE_REGION)
appwrite_client.set_project(settings.APPWRITE_PROJECT_ID)
appwrite_client.set_key(settings.APPWRITE_API_KEY)

clientdb = Databases(appwrite_client)
storage= Storage(appwrite_client)

class CollectionManager:
    def __init__(self, config_path="collection_ids.json"):
        with open(config_path) as f:
            self.collection_map = json.load(f)

    def get_id(self, collection_name):
        return self.collection_map.get(collection_name)

collection_manager = CollectionManager()

