import traceback

from core.logger import loggers
from fastapi import APIRouter, Depends, HTTPException
from services.hr_service import get_combined_data_paginated
from db.crud import fetch_clean_documents
from dependencies.auth_guard import require_role

router = APIRouter()


@router.get(
    "/get-all-interviews",
    summary="Fetch all interview data",
    description="""
Retrieve all interview records in a paginated format.

- Combines relevant data from multiple collections/services.
- Handles service-level errors and logs unexpected exceptions.

Raises:
- 500 Internal Server Error: if fetching interview data fails or an unexpected error occurs.
"""
)
async def get_all_interviews():
    try:
        result = await get_combined_data_paginated()

        if isinstance(result, dict) and "error" in result:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Failed to fetch interview data",
                    "error": result["error"],
                },
            )

        return result

    except HTTPException as http_err:
        raise http_err

    except Exception as e:
        loggers.api.error(
            "Unhandled error in /get-all-interviews",
            extra={"Error": traceback.format_exc()},
        )
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)},
        )


@router.get(
    "/get-student-info",
    summary="Fetch student information by ID",
    description="""
Retrieve personal information of a student using their user ID.

- Requires admin role.
- Returns user details from the 'user_info' collection.

Raises:
- 500 Internal Server Error: if fetching student info fails.
"""
)
async def get_student_info(userid: str, user=Depends(require_role(["admin"]))):
    result = await fetch_clean_documents(collection_name="user_info", filters={"userid": userid})
    if isinstance(result, dict) and 'error' in result:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve student details: {result['error']}"
        )
    return result
