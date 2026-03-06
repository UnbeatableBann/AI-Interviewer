import traceback
from datetime import date, datetime
from typing import List

from core.logger import loggers
from db.crud import fetch_all_documents


async def get_combined_data_paginated() -> List[dict]:
    """
    Fetches all rows from evaluation, user_info, and job_description collections,
    handles pagination, and merges them based on userid and jobid.

    Returns:
        A list of merged dictionaries with fields:
        userid, name, jobid, job_title, experience_level, score
    """
    try:
        # Fetch all documents from each collection with pagination
        evaluations = await fetch_all_documents("evaluation_table")  # userid, jobid, score
        users = await fetch_all_documents("user_info")         # userid, name
        jobs = await fetch_all_documents("job_description")    # jobid, job_title, experience_level
        
        # Build lookup maps for quick join
        user_map = {
            u.get("userid"): {
                "name": u.get("name", ""),
                "email": u.get("email", "")
            }
            for u in users
        }
        job_map = {
            j.get("jobid"): {
                "jobtitle": j.get("jobtitle", ""),
                "experiencelevel": j.get("experiencelevel", "")
            }
            for j in jobs
        }
        
        # Merge data
        combined_data = []
        for eval_doc in evaluations:
            userid = eval_doc.get("userid")
            jobid  = eval_doc.get("jobid")
            score  = eval_doc.get("score")
            dates  = eval_doc.get("$createdAt")

            combined_data.append({
                "userid": userid,
                "user": user_map.get(userid, None),
                "jobid": jobid,
                "jobtitle": job_map.get(jobid, {}).get("jobtitle"),
                "experiencelevel": job_map.get(jobid, {}).get("experiencelevel"),
                "score": score,
                "date" : dates
            })

        total_interviews = len(combined_data)

        today = date.today()
        todays_interviews = [
            i for i in combined_data
            if i.get("date") and datetime.fromisoformat(i["date"]).date() == today
        ]

        summary = {
            "total_interviews": total_interviews,
            "todays_interviews": len(todays_interviews),
        }

        loggers.db.info(f"Combined {len(combined_data)} records from all tables")
        return {
            "summary": summary,
            "data": combined_data
        }

    except Exception as e:
        loggers.db.error("Failed to combine data", extra={"Error": traceback.format_exc()})
        return {"error": str(e)}

