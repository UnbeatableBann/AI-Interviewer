import json
import httpx
import traceback

from core.logger import loggers
from core.config import settings
from appwrite.id import ID
from db.client import collection_manager

BASE_URL = settings.APPWRITE_REGION
PROJECT_ID = settings.APPWRITE_PROJECT_ID
API_KEY = settings.APPWRITE_API_KEY
DATABASE_ID = settings.APPWRITE_DATABASE_ID

HEADERS = {
    "X-Appwrite-Project": PROJECT_ID,
    "X-Appwrite-Key": API_KEY,
    "Content-Type": "application/json"
}


# ------------------ CREATE ------------------ #
async def insert_to_collection(collection_name: str, documents: list):
    """
    Inserts multiple documents into the specified Appwrite collection.

    Args:
        collection_name (str): Logical collection name mapped to Appwrite collection ID.
        documents (list[dict]): List of document data dictionaries. Each dict may include a custom '$id' key; 
                                if omitted, a unique ID will be generated.

    Returns:
        list[dict]: List of inserted document responses or {'error': ...} if an exception occurs.
    """
    try:
        loggers.db.info(f"Inserting documents into collection: {collection_name}")
        collection_id = collection_manager.get_id(collection_name)

        payloads = []
        for doc in documents:
            payload = doc.copy()
            if "$id" not in payload:
                payload["$id"] = ID.unique()
            payloads.append(payload)

        results = []
        async with httpx.AsyncClient() as client:
            for doc in payloads:
                payload = {
                    "documentId": doc["$id"],
                    "data": doc
                }
                url = f"{BASE_URL}/databases/{DATABASE_ID}/collections/{collection_id}/documents"
                response = await client.post(url, headers=HEADERS, json=payload)
                response.raise_for_status()
                results.append(response.json())

        loggers.db.info(f"Inserted {len(results)} documents into collection {collection_name}")
        return results

    except Exception as e:
        loggers.db.error(
            f"Database insertion failed for collection: {collection_name} and documents: {documents}",
            extra={"Error": traceback.format_exc()}
        )
        return {"error": str(e)}


# ------------------ READ ------------------ #
async def fetch_all_documents(collection_name: str):
    """
    Fetches all documents from a specified collection without applying filters.

    Args:
        collection_name (str): Logical collection name mapped to Appwrite collection ID.

    Returns:
        list[dict]: List of raw documents including metadata, or {'error': ...} on failure.
    """
    try:
        loggers.db.info(f"Fetching all documents from collection: {collection_name}")
        collection_id = collection_manager.get_id(collection_name)

        url = f"{BASE_URL}/databases/{DATABASE_ID}/collections/{collection_id}/documents"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
            data = response.json()

        documents = data.get("documents", [])
        loggers.db.info(f"Fetched {len(documents)} documents from collection {collection_name}")
        return documents

    except Exception as e:
        loggers.db.error(
            f"Database fetch failed for collection: {collection_name}",
            extra={"Error": traceback.format_exc()}
        )
        return {"error": str(e)}


async def fetch_clean_documents(collection_name: str, filters: dict):
    """
    Fetches documents from a collection that match all provided filters and removes metadata keys starting with '$'.

    Args:
        collection_name (str): Logical collection name mapped to Appwrite collection ID.
        filters (dict): Dictionary of field-value pairs to filter by.

    Returns:
        list[dict]: List of cleaned documents without metadata, or {'error': ...} on failure.
    """
    try:
        loggers.db.info(f"Fetching documents from collection: {collection_name} with filters: {filters}")
        collection_id = collection_manager.get_id(collection_name)

        query_params = []
        for field, value in filters.items():
            query = {"method": "equal", "attribute": field, "values": [value]}
            query_params.append(("queries[]", json.dumps(query, separators=(',', ':'))))

        url = f"{BASE_URL}/databases/{DATABASE_ID}/collections/{collection_id}/documents"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=HEADERS, params=query_params)
            response.raise_for_status()
            data = response.json()

        documents = data.get("documents", [])
        cleaned_documents = [{k: v for k, v in doc.items() if not k.startswith("$")} for doc in documents]
        loggers.db.info(f"Fetched {len(cleaned_documents)} documents from collection {collection_name}")
        return cleaned_documents

    except Exception as e:
        loggers.db.error(
            f"Database fetch failed for collection: {collection_name} with filters: {filters}",
            extra={"Error": traceback.format_exc()}
        )
        return {"error": str(e)}


# ------------------ UPDATE ------------------ #
async def update_documents_by_field(collection_name: str, field: str, value: str, update_data: dict):
    """
    Updates all documents in a collection where a specific field matches a given value.

    Args:
        collection_name (str): Logical collection name mapped to Appwrite collection ID.
        field (str): Document field to match.
        value (str): Value to match for the field.
        update_data (dict): Dictionary of fields to update.

    Returns:
        list[dict]: List of updated document responses, or {'error': ...} if no documents match or on failure.
    """
    try:
        collection_id = collection_manager.get_id(collection_name)

        # Fetch all matching documents first
        query_params = [("queries[]", json.dumps({"method": "equal", "attribute": field, "values": [value]}, separators=(',', ':')))]
        url = f"{BASE_URL}/databases/{DATABASE_ID}/collections/{collection_id}/documents"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=HEADERS, params=query_params)
            response.raise_for_status()
            documents = response.json().get("documents", [])

            if not documents:
                return {"error": f"No documents found where {field} = {value}"}

            updated_docs = []
            for doc in documents:
                doc_id = doc["$id"]
                update_url = f"{url}/{doc_id}"
                payload = {"data": update_data}
                update_response = await client.patch(update_url, headers=HEADERS, json=payload)
                update_response.raise_for_status()
                updated_docs.append(update_response.json())

        return updated_docs

    except Exception as e:
        loggers.db.error(
            f"Database update failed for collection: {collection_name}, field: {field}, value: {value}, update_data: {update_data}",
            extra={"Error": traceback.format_exc()}
        )
        return {"error": str(e)}


# ------------------ DELETE ------------------ #
async def delete_documents_by_fields(collection_name: str, filters: dict):
    """
    Deletes all documents from a collection that match all provided filter conditions.

    Args:
        collection_name (str): Logical collection name mapped to Appwrite collection ID.
        filters (dict): Dictionary of field-value pairs to match.

    Returns:
        dict: {'deleted_ids': [...]} with list of deleted document IDs, or {'error': ...} if no documents match or on failure.
    """
    try:
        collection_id = collection_manager.get_id(collection_name)

        query_params = []
        for field, value in filters.items():
            query = {"method": "equal", "attribute": field, "values": [value]}
            query_params.append(("queries[]", json.dumps(query, separators=(',', ':'))))

        url = f"{BASE_URL}/databases/{DATABASE_ID}/collections/{collection_id}/documents"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=HEADERS, params=query_params)
            response.raise_for_status()
            documents = response.json().get("documents", [])

            if not documents:
                return {"error": f"No documents found matching: {filters}"}

            deleted_ids = []
            for doc in documents:
                doc_id = doc["$id"]
                delete_url = f"{url}/{doc_id}"
                await client.delete(delete_url, headers=HEADERS)
                deleted_ids.append(doc_id)

        return {"deleted_ids": deleted_ids}

    except Exception as e:
        loggers.db.error(
            f"Database deletion failed for collection: {collection_name} with filters: {filters}",
            extra={"Error": traceback.format_exc()}
        )
        return {"error": str(e)}
