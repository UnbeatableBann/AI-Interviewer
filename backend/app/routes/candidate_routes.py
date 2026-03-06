from typing import Any, Dict
from uuid import uuid4

from db.crud import fetch_clean_documents
from dependencies.auth_guard import get_current_user, require_role
from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.params import Query
from schemas.interview_schemas import AnswerRequest, JobDescription, QuestionGenerateOut
from schemas.user_schemas import UpdateUserInfo, UserInfo
from services.candidate_service import (
    delete_personal_info_service,
    generate_questions_with_llm,
    process_response,
    save_job_des_details,
    save_user_info,
    update_personal_info_service,
)

router = APIRouter()


@router.post(
    "/save-personal-info",
    status_code=status.HTTP_201_CREATED,
    summary="Save user personal information",
    description="""
Save personal information for the authenticated user.

- Stores user's basic info such as name, contact details, and resume.
- Associates data with the current user's ID.
"""
)
async def save_personal_info(data: UserInfo, userid=Depends(require_role(["student"]))):
    data.userid = userid.userid
    result = await save_user_info(data)
    return result


@router.post(
    "/save-job-description",
    summary="Save job description",
    description="""
Save a job description for generating interview questions.

- Assigns a unique job ID.
- Stores the job description associated with the current user.
"""
)
async def save_job_description(data: JobDescription, userid=Depends(get_current_user)):
    data.userid = userid.userid
    data.jobid = str(uuid4())
    res = await save_job_des_details(data)
    return res


@router.get(
    "/generate-question/{jobid}",
    response_model=QuestionGenerateOut,
    summary="Generate interview questions for a job",
    description="""
Generate interview questions for a given job ID using LLM.

- Requires job ID to exist for the authenticated user.
- Returns a list of generated questions.

Raises:
- 404 Not Found: if the job ID does not exist for the user.
"""
)
async def generate_question(
    jobid: str = Path(
        ...,
        example="dd0a4ba2-92c4-48c7-9e66-cbe75ff905c1",
        description="The job ID for which questions should be generated",
    ),
    userid=Depends(get_current_user),
):
    response = await fetch_clean_documents(
        collection_name="job_description", 
        filters={"userid": userid.userid, "jobid": jobid}
    )

    if not response:
        raise HTTPException(
            status_code=404,
            detail=f"Job ID '{jobid}' not found for user {userid.userid}"
        )

    questions = await generate_questions_with_llm(jobid, userid.userid)
    return {"status": "success", "jobid": jobid, "questions": questions}


@router.post(
    "/submit-response/{jobid}",
    summary="Submit answer to interview questions",
    description="""
Submit candidate responses for a given job ID.

- `islast` query parameter indicates if this is the last response.
- Stores responses and processes them.

Raises:
- 404 Not Found: if the job ID does not exist for the user.
"""
)
async def submit_response(
    jobid: str = Path(
        ...,
        example="dd0a4ba2-92c4-48c7-9e66-cbe75ff905c1",
        description="The job ID for which questions should be generated",
    ),
    data: AnswerRequest = ...,
    islast: bool = Query(False, description="Whether this is the last response"),
    userid=Depends(get_current_user),
) -> Dict[str, Any]:
    response = await fetch_clean_documents(
        collection_name="job_description", 
        filters={"userid": userid.userid, "jobid": jobid}
    )

    if not response:
        raise HTTPException(
            status_code=404,
            detail=f"Job ID '{jobid}' not found for user {userid.userid}"
        )

    result = await process_response(jobid, data, userid.userid, islast)
    return result or []


@router.get(
    "/get-result/{jobid}",
    summary="Get evaluation result for a job",
    description="""
Fetch evaluation results for the given job ID.

- Returns candidate evaluation from the 'evaluation_table'.
- Requires the job ID to exist for the user.

Raises:
- 404 Not Found: if the job ID does not exist for the user.
- 400 Bad Request: if evaluation result is not found.
"""
)
async def get_result(
    jobid: str = Path(
        ...,
        example="dd0a4ba2-92c4-48c7-9e66-cbe75ff905c1",
        description="The job ID for which questions should be generated",
    ), 
    userid=Depends(get_current_user)
):
    response = await fetch_clean_documents(
        collection_name="job_description", 
        filters={"userid": userid.userid, "jobid": jobid}
    )

    if not response:
        raise HTTPException(
            status_code=404,
            detail=f"Job ID '{jobid}' not found for user {userid.userid}"
        )

    result = await fetch_clean_documents(
        collection_name="evaluation_table",
        filters={"userid": userid.userid, "jobid": jobid}
    )

    if not result:
        raise HTTPException(status_code=400, detail="Result not found")
    
    return result


@router.patch(
    "/update-personal-info",
    status_code=status.HTTP_200_OK,
    summary="Update personal information",
    description="""
Update personal information for the authenticated user.

- Only provided fields are updated.
- Handles user not found or missing fields errors.

Raises:
- 404 Not Found: if the user does not exist.
- 400 Bad Request: if no fields are provided.
- 500 Internal Server Error: if update fails.
"""
)
async def update_personal_info(
    data: UpdateUserInfo,
    userid=Depends(require_role(["student"]))
) -> Dict[str, Any]:
    result = await update_personal_info_service(userid.userid, data)

    if "error" in result:
        if result["error"] == "User not found":
            raise HTTPException(status_code=404, detail=result["error"])
        if result["error"] == "No fields provided for update":
            raise HTTPException(status_code=400, detail=result["error"])
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.delete(
    "/delete-personal-info",
    status_code=status.HTTP_200_OK,
    summary="Delete personal information",
    description="""
Delete personal information for the authenticated user.

- Calls the service layer to delete all saved personal info.

Raises:
- 404 Not Found: if the user does not exist.
- 500 Internal Server Error: if deletion fails.
"""
)
async def delete_personal_info(userid=Depends(require_role(["admin", "student"]))) -> Dict[str, str]:
    result = await delete_personal_info_service(userid.userid)

    if "error" in result:
        if result["error"] == "User not found":
            raise HTTPException(status_code=404, detail=result["error"])
        if result["error"] == "Delete operation failed":
            raise HTTPException(status_code=500, detail=result["error"])

    return result
