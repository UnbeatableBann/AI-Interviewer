import uuid

from db.crud import (
    fetch_clean_documents,
    insert_to_collection,
    update_documents_by_field,
)
from fastapi import HTTPException
from models.user_model import UserDB
from utils.security import hash_password, verify_password


async def register_user(user):
    hashed_pw = await hash_password(user.password)
    userid = str(uuid.uuid4())

    user_data = UserDB(
        userid=userid,
        email=user.email,
        hashedpassword=hashed_pw,
        name=user.name,
        role=user.role,
    )

    res = await insert_to_collection(
        collection_name= "registrations", documents=[user_data.model_dump()]
    )

    users = res["documents"] if "documents" in res else []

    if users:
        return UserDB(**users[0])
    return None


async def get_user_by_email(email: str):
    res = await fetch_clean_documents(
        collection_name="registrations", filters={"email": email}
    )

    if res:
        return UserDB(**res[0])
    return None


async def reset_password_service(userid: str, email: str, old_password: str, new_password: str):
    db_user = await get_user_by_email(email) # can use own login schema for custom fields                                                                                                                                                  5-c069-4db6-aa3c-be505563ff5e'}]
    
    if not db_user or not await verify_password(old_password, db_user.hashedpassword):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    hashed_pw = await hash_password(new_password)
    update_data = {"hashedpassword": hashed_pw}

    # Update in DB
    updated = await update_documents_by_field(
        collection_name="registrations",
        field="userid",
        value=userid,
        update_data=update_data,
    )

    if not updated:
        return {"error": "Failed to update user info"}
    
    return {
        "status": "success",
        "updated_fields": len(update_data)
    }

async def new_password_service(email: str, new_password: str):

    hashed_password = await hash_password(new_password)

    # Update in DB
    updated = await update_documents_by_field(collection_name="registrations", field="email", value=email, update_data={"hashedpassword": hashed_password})
    if not updated:
        return {"error": "Failed to update password"}

    return {"message": "Password updated successfully"}
