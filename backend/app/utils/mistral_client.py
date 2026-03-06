import asyncio
import json
import re
import traceback
from typing import Any, Dict, List, Union

import httpx
from core.config import settings
from core.logger import loggers


# --- Common helper ---
async def call_mistral(prompt: str, model: str = "mistral-small") -> Union[str, Dict[str, str]]:
    """Send a prompt to Mistral API and return the raw response content."""
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            loggers.external_api.error(
                f"Mistral API error: {response.status_code}",
                extra={"response": response.text}
            )
            return {"error": f"API returned status {response.status_code}"}

        response_data = response.json()
        return response_data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        loggers.external_api.error("Exception in call_mistral", extra={"error": traceback.format_exc()})
        return {"error": str(e)}

# --- Evaluate Answer ---
async def evaluate_answer(question: str, answer: str) -> Union[int, Dict[str, str]]:
    prompt = f"""
    You are an AI interviewer evaluating candidate responses.

    Question: "{question}"
    Answer: "{answer}"

    Your task:
    - Assign a score from 1 to 10 based solely on the quality and relevance of the answer.
    - Only return the numeric score (e.g., 7). Do not include any explanation, feedback, or extra text.
    - Output must be a single integer between 1 and 10.
    """
    try:
        result = await call_mistral(prompt)
        
        # If API returns error dict
        if isinstance(result, dict) and "error" in result:
            return result
        
        # Extract first integer from result
        result = re.sub(r"[`\s]", "", result) 
        match = re.search(r"\b([1-9]|10)\b", str(result))
        if match:
            return int(match.group(0))
        else:
            return {"error": f"Invalid response format: {result}"}
    
    except ValueError:
        return {"error": f"Invalid response format: {result}"}
    
    except Exception as e:
        return {"error": str(e)}

async def evaluate_answer_with_retry(question: str, answer: str, retries: int = settings.MAX_EVALUATION_RETRIES) -> int:
    for attempt in range(retries + 1):
        try:
            score = await evaluate_answer(question, answer)

            
            # Check if score is valid integer between 1 and 10
            if isinstance(score, int) and 0 <= score <= 10:
                return score

            # Log invalid response
            loggers.external_api.error(f"[Attempt {attempt+1}] Invalid score format: {score}")
        except Exception as e:
            loggers.external_api.error(f"[Attempt {attempt+1}] Error evaluating answer: {e}")

        # Wait before retrying (only if not last attempt)
        if attempt < retries:
            await asyncio.sleep(1)

    # If all retries fail, return -1 as fallback
    return -1



# --- Extract Requirements ---
async def extract_requirements(job_description: List[Dict[str, Any]]) -> Union[str, Dict[str, str]]:
    job = job_description[0]
    prompt = f"""
    You are an expert human interviewer preparing for a candidate interview.

    Job Title: {job['jobtitle']}
    Company Name: {job['companyname']}
    Experience Level: {job['experiencelevel']}
    Interview Type: {job['interviewtype']}
    Job Description: {job['description']}
    Requirements: {job['requirements']}

    Extract key interview topics as a JSON array of objects:
    - "topic": the skill/area
    - "why": why it is relevant

    Only return the JSON array.
    """
    return await call_mistral(prompt)


# --- Generate Questions for Topic ---
async def generate_questions_for_topic(
    job_profile: List[Dict[str, Any]], topic: List[Dict[str, Any]]
) -> Union[List[str], Dict[str, str]]:
    job = job_profile[0]
    prompt = f"""
    You are an expert {job['interviewtype']} interviewer preparing questions.

    Job Title: {job['jobtitle']}
    Company Name: {job['companyname']}
    Experience Level: {job['experiencelevel']}
    Interview Type: {job['interviewtype']}

    Topics:
    {json.dumps(topic, indent=2)}

    For each topic, generate concise interview questions. 
    Return a JSON array of objects:
    - "topic": the topic
    - "questions": an array of questions
    """

    try:
        result = await call_mistral(prompt)
        topic_list = json.loads(result)
        # Flatten all questions into a single list
        all_questions = [q for t in topic_list if "questions" in t for q in t["questions"]]
        return all_questions
    except Exception:
        return {"error": f"Invalid response: {result}"}





