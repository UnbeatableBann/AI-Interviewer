import asyncio
from typing import Any, Dict

from core.logger import loggers
from core.config import settings
from db.crud import (
    delete_documents_by_fields,
    fetch_clean_documents,
    insert_to_collection,
    update_documents_by_field,
)
from fastapi import HTTPException
from models.user_model import JobDescriptionDB, UserInfoDB
from schemas.user_schemas import UpdateUserInfo
from utils.mistral_client import (
    evaluate_answer_with_retry,
    extract_requirements,
    generate_questions_for_topic,
)
from utils.redis_client import get_all_responses_from_redis, save_response_to_redis


# Duplicate logic in save_user_info and save_job_des_details
async def save_user_info(data: UserInfoDB):
    try:
        res = await insert_to_collection(
            collection_name="user_info", documents=[data.model_dump()]
        )
        users = res["documents"] if "documents" in res else []

        if users:
            return UserInfoDB(**users[0])
        return None
    except Exception as e:
        raise Exception(f"Failed to save user info: {str(e)}")


async def save_job_des_details(data: JobDescriptionDB):
    try:
        res = await insert_to_collection(
            collection_name="job_description", documents=[data.model_dump(mode="json")]
        )
        users = res["documents"] if "documents" in res else []

        if users:
            return JobDescriptionDB(**users[0])
        return None
    except Exception as e:
        raise Exception(f"Failed to save user info: {str(e)}")


async def generate_questions_with_llm(jobid: str, userid: str) -> list[str]:
    """
    Generates questions using LLM based on a user's job description.

    Args:
        jobid (str): Job identifier.
        userid (str): User identifier.

    Returns:
        list[str]: List of generated questions.

    Raises:
        HTTPException: If no questions are generated or an error occurs.
    """
    # Fetch job description documents
    jobdes = await fetch_clean_documents(
        collection_name="job_description",
        filters={"jobid": jobid, "userid": userid}
    )

    # Extract topic / requirements from job description
    topic = await extract_requirements(jobdes)

    # Generate questions
    generated_questions = await generate_questions_for_topic(jobdes, topic)

    # Handle errors returned by the question generation API
    if isinstance(generated_questions, dict) and "error" in generated_questions:
        loggers.external_api.error(f"Error generating questions: {generated_questions['error']}")
        raise HTTPException(status_code=500, detail=f"Error generating questions: {generated_questions['error']}")

    # If result is not a list or empty, raise exception
    if not isinstance(generated_questions, list) or not generated_questions:
        raise HTTPException(status_code=500, detail="No questions could be generated for this job description")

    # Return generated questions
    return generated_questions


async def process_response(
    jobid: str, data: Dict[str, Any], userid: str, islast: bool = False
) -> Dict[str, Any]:
    """
    Processes a user response: evaluates the answer, saves to Redis, and optionally
    finalizes all responses by saving them to the DB. Failed inserts are retried
    individually up to MAX_RETRIES.
    """
    # Validate input
    if not data.question:
        raise HTTPException(status_code=400, detail="Question is required")

    # Evaluate the answer
    try:
        score = await evaluate_answer_with_retry(data.question, data.answer)
        if score == -1:
            raise HTTPException(status_code=500, detail="Failed to evaluate answer after retries")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating answer: {str(e)}")

    # Prepare response document
    response_doc = {
        "jobid": jobid,
        "userid": userid,
        "question": data.question,
        "answer": data.answer,
        "score": score,
    }

    # Save to Redis
    try:
        await save_response_to_redis(jobid, response_doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving response: {str(e)}")

    # If last response, insert all responses into DB with per-document retries
    if islast:
        all_responses = await get_all_responses_from_redis(jobid)

        if not all_responses:
            raise HTTPException(status_code=404, detail="No responses found to finalize")

        failed_docs = all_responses.copy()
        successfully_inserted = []

        for attempt in range(1, settings.MAX_REDIS_RETRIES + 1):
            if not failed_docs:
                break

            insert_result = await insert_to_collection(
                collection_name="evaluation_table",
                documents=failed_docs
            )

            if isinstance(insert_result, dict) and "error" in insert_result:
                # Entire batch failed, retry after delay
                await asyncio.sleep(settings.REDIS_RETRY_DELAY)
                continue
            else:
                # Check if some documents failed individually
                failed_docs_next_round = []
                for doc, res in zip(failed_docs, insert_result):
                    if isinstance(res, dict) and "error" in res:
                        failed_docs_next_round.append(doc)
                    else:
                        successfully_inserted.append(res)

                failed_docs = failed_docs_next_round
                if failed_docs:
                    await asyncio.sleep(settings.REDIS_RETRY_DELAY)

        if failed_docs:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save {len(failed_docs)} documents after {settings.MAX_REDIS_RETRIES} attempts"
            )

        return {
            "status": "success",
            "message": "All responses submitted and saved to DB",
            "insert_result": successfully_inserted
        }

    # Return single response status
    return {
        "status": "success",
        "message": "Response saved successfully",
        "score": score
    }



async def user_exists(user_id: str) -> bool:
    """
    Check if a user with the given user_id exists in the 'users' collection.
    """
    try:
        results = await fetch_clean_documents(filters={"userid": user_id}, collection_name="registrations")

        if isinstance(results, dict) and "error" in results:
            loggers.db.error(f"Error checking user {user_id}: {results['error']}")
            return False
        
        return len(results) > 0

    except Exception as e:
        loggers.flask.error(f"Unexpected error in user_exists for {user_id}", extra={"Error": str(e)})
        return False
    
    
async def update_personal_info_service(userid: str, data: UpdateUserInfo) -> Dict[str, Any]:
    # Fetch existing user
    existing_user = await user_exists(userid)
    if not existing_user:
        return {"error": "User not found"}

    # Prepare update data
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return {"error": "No fields provided for update"}

    # Update in DB
    updated = await update_documents_by_field(collection_name="user_info", field="userid", value=userid, update_data= update_data)
    if not updated:
        return {"error": "Failed to update user info"}

    return {
        "status": "success",
        "updated_fields": len(update_data)
    }

async def delete_personal_info_service(userid: str) -> Dict[str, str]:
    # Check if user exists
    user = await user_exists(userid)
    if not user:
        return {"error": "User not found"}

    # Delete from DB
    for table_name in ["user_info", "registrations", "job_description", "evaluation_table"]:
        deleted = await delete_documents_by_fields(collection_name= table_name , filters={"userid":userid})
    if not deleted:
        return {"error": "Delete operation failed"}

    return {"status": "success", "message": "User personal info deleted successfully"}