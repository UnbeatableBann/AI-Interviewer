from fastapi import APIRouter, Depends, HTTPException, status
from dependencies.auth_guard import require_role
from schemas.user_schemas import UserSignUp, UserOut
from services.auth_service import get_user_by_email, register_user
from db.crud import delete_documents_by_fields, fetch_clean_documents

router = APIRouter(dependencies=[Depends(require_role(["admin"]))])


@router.post(
    "/hr/register",
    summary="Create a new HR account",
    description="""
Register a new HR user in the system.

- Checks if the email is already registered.
- Saves the HR user to the database.
- Returns the created user details.

Raises:
- 409 Conflict: if the email is already registered.
- 500 Internal Server Error: if saving the user fails.
"""
)
async def create_hr_account(data: UserSignUp):
    existing_user = await get_user_by_email(data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered",
        )

    db_user = await register_user(data)
    if not db_user or (isinstance(db_user, dict) and 'error' in db_user):
        error_detail = db_user['error'] if isinstance(db_user, dict) else "Cannot save the details"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )

    return db_user


@router.get(
    "/hr/list",
    response_model=list[UserOut],
    summary="List all registered HR users",
    description="""
Fetches a list of all users with the 'HR' role.

- Returns an array of HR users.
- Handles database errors gracefully.

Raises:
- 500 Internal Server Error: if fetching HR users fails.
"""
)
async def list_hr_users():
    users = await fetch_clean_documents(collection_name="registrations", filters={"role": "hr"})
    if isinstance(users, dict) and 'error' in users:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch HR users: {users['error']}"
        )
    return users


@router.delete(
    "/hr/{hr_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an HR account by ID",
    description="""
Deletes an HR user by their unique ID.

- Deletes the user from the 'registrations' collection.
- Returns a success message if deletion succeeds.
- Returns 404 if the HR user does not exist.

Raises:
- 404 Not Found: if the HR user does not exist.
- 500 Internal Server Error: if deletion fails.
"""
)
async def delete_hr_account(hr_id: str):
    deleted = await delete_documents_by_fields(
        collection_name="registrations", 
        filters={"userid": hr_id}
    )

    if isinstance(deleted, dict) and 'error' in deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to delete HR details: {deleted['error']}"
        )

    deleted_ids = deleted.get("deleted_ids") if isinstance(deleted, dict) else None
    if not deleted_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="HR user not found"
        )

    return {"success": f"HR details for {hr_id} deleted successfully"}
