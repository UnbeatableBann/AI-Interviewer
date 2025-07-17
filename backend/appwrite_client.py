from appwrite.client import Client
from appwrite.query import Query
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage
from appwrite.id import ID
from dotenv import load_dotenv
import os
import traceback

load_dotenv()
APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")
APPWRITE_REGION = os.getenv("APPWRITE_REGION")
APPWRITE_DATABASE_ID = os.getenv("APPWRITE_DATABASE_ID")
APPWRITE_BUCKET_ID = os.getenv("APPWRITE_BUCKET_ID")

# Limit for appwrite is 25 collections
appwrite = Client()
appwrite.set_endpoint(APPWRITE_REGION)
appwrite.set_project(APPWRITE_PROJECT_ID)
appwrite.set_key(APPWRITE_API_KEY)

db = Databases(appwrite)
storage= Storage(appwrite)

# Dictionary to map collection names to their IDs makes easier to reference
collection_id_map= {"user_info": "68724be2002f4a0c7116",
                    "example_table": "68764059001787e483b0",
                    #"evaluation_table":
                    }

def insert_to_collection(collection_id: str, documents: list[dict]):
    """
    Insert multiple documents into the specified Appwrite collection.
    
    Args:
        database_id (str): The target database ID.
        collection_id (str): The target collection ID.
        documents (list[dict]): List of dicts representing each document's data.
            Each dict may optionally contain:
              - '$id': Custom document ID (use ID.unique() for auto-generated ones)
              - other arbitrary fields for your document

    Returns:
        dict: API response or {'error': ...} on failure.
    """
    try:
        collection_id= collection_id_map.get(collection_id, collection_id)
        # Ensure each document has an $id
        payloads = []
        for doc in documents:
            payload = doc.copy()
            if '$id' not in payload:
                payload['$id'] = ID.unique()
            payloads.append(payload)

        result = db.create_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=collection_id,
            documents=payloads
        )
        return result 

    except Exception as e:
        print("Exception in create_documents_in_collection:", traceback.format_exc())
        return {"error": str(e)}

def fetch_clean_documents(collection_id: str, filters: dict) -> list:
    """
    Fetches documents from the given collection where all field conditions in `filters` match,
    and removes metadata keys (those starting with '$').

    Args:
        collection_id: The collection ID or logical name mapped to a real ID.
        filters: A dictionary of field-value pairs to filter by (e.g., {"name": "ABC", "user_id": "123"}).

    Returns:
        A list of cleaned documents (dicts) with metadata removed.
    """
    try:
        # Resolve mapped collection ID if available
        collection_id = collection_id_map.get(collection_id, collection_id)

        # Build query conditions
        queries = [Query.equal(field, value) for field, value in filters.items()]

        response = db.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=collection_id,
            queries=queries
        )

        documents = response.get('documents', [])

        # Clean out metadata keys starting with '$'
        cleaned_documents = [
            {k: v for k, v in doc.items() if not k.startswith("$")}
            for doc in documents
        ]

        return cleaned_documents

    except Exception as e:
        print("Error in fetch_clean_documents:", traceback.format_exc())
        return {"error": str(e)}

# for now it takes single query to match the rows but change it to dict for mulitple queries
def update_documents_by_field(collection_id: str, field: str, value: str, update_data: dict):
    """
    Update all documents in the given collection where field == value.

    Args:
        collection_id: ID or mapped name of the collection.
        field: Field name to match.
        value: Field value to match.
        update_data: Dictionary of fields to update.

    Returns:
        A list of updated documents or error message.
    """
    try:
        collection_id = collection_id_map.get(collection_id, collection_id)

        # Fetch all documents that match the condition
        result = db.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=collection_id,
            queries=[Query.equal(field, value)]
        )

        documents = result.get("documents", [])
        if not documents:
            return {"error": f"No documents found where {field} = {value}"}

        updated_docs = []

        for doc in documents:
            doc_id = doc["$id"]
            updated = db.update_document(
                database_id=APPWRITE_DATABASE_ID,
                collection_id=collection_id,
                document_id=doc_id,
                data=update_data
            )
            updated_docs.append(updated)

        return updated_docs

    except Exception as e:
        print("Exception in update_documents_by_field:", traceback.format_exc())
        return {"error": str(e)}

def delete_documents_by_fields(collection_id: str, filters: dict):
    """
    Deletes all documents in the given collection that match all key-value pairs in `filters`.

    Args:
        collection_id: ID or mapped name of the collection.
        filters: A dictionary where key = field name, value = value to match.

    Returns:
        A dictionary with deleted document IDs or error info.
    """
    try:
        collection_id = collection_id_map.get(collection_id, collection_id)

        # Build multiple queries
        query_list = [Query.equal(field, value) for field, value in filters.items()]

        # Fetch matching documents
        result = db.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=collection_id,
            queries=query_list
        )

        documents = result.get("documents", [])
        if not documents:
            return {"error": f"No documents found matching: {filters}"}

        deleted_ids = []

        for doc in documents:
            doc_id = doc["$id"]
            db.delete_document(
                database_id=APPWRITE_DATABASE_ID,
                collection_id=collection_id,
                document_id=doc_id
            )
            deleted_ids.append(doc_id)

        return {"deleted_ids": deleted_ids}

    except Exception as e:
        print("Error in delete_documents_by_fields:", traceback.format_exc())
        return {"error": str(e)}
