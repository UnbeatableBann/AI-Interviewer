import json
import os
import traceback
from dotenv import load_dotenv
import requests
from appwrite_client import appwrite

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

def evaluate_answer(question, answer):
    try:
        prompt = f"""
            You are an AI interviewer evaluating candidate responses.

            Question: "{question}"
            Answer: "{answer}"

            Your task:
            - Assign a score from 1 to 10 based solely on the quality and relevance of the answer.
            - Only return the numeric score (e.g., 7). Do not include any explanation, feedback, or extra text.
            - Output must be a single integer between 1 and 10.
            """
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mistral-small",  # or "mixtral-8x7b-32768"
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post("https://api.mistral.ai/v1/chat/completions", json=payload, headers=headers)
        response= response.json()['choices'][0]['message']['content']
        print(f"Score for question '{question}': {response}")
        return response
    
    except Exception as e:
        import traceback
        print('Exception in evaluate_answer:', traceback.format_exc())
        return {"error": str(e)}

def requirements(job_description):
    try:
        print(f"📺📺📺Job description received: {job_description}")
        prompt = f"""
        Do the following only if you are given a job description, if not, return None,
        You are an expert HR assistant. Extract the key requirements from the following job description:
        \n{job_description}\n 
        Return the result as a JSON array of objects. Each object should have:
          - "requirement": the name of the requirement
          - "description": a short description of the requirement
        Only output the JSON array. Do not include any explanation or extra text.
        """
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mistral-small",
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post("https://api.mistral.ai/v1/chat/completions", json=payload, headers=headers)
        print(f"✅✅✅✅Response from Mistral API: {response.text}")
        return response.json()
    except Exception as e:
        import traceback
        print('Exception in requirements:', traceback.format_exc())
        return {"error": str(e)}

def generate_questions_for_topic(profile, topic):
    try:
        print(f"📚📚📚Generating questions for profile: {profile} and topic: {topic}")
        prompt = f"""
            You are given the following topics for a 
            job profile:{profile} 
            and you have to ask 3 questions related to each topic.
            Topics: {topic}
            Each question should be clear, concise, and focused on assessing the candidate's skills and fit for the role.
            Format the output as a JSON array of objects, each with a "Topic name" with their respective topic's name field."""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mistral-small",
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post("https://api.mistral.ai/v1/chat/completions", json=payload, headers=headers)
        response_data=response.json()
        content = response_data['choices'][0]['message']['content']
        print(f"👉👉👉Response from Mistral API: {content}")
        # Parse the JSON string
        topic_list = json.loads(content)

        # Flatten into a list of question strings
        all_questions = []
        for topic in topic_list:
            for key, value in topic.items():
                if key.lower().startswith("question"):
                    all_questions.append(value)
        print(all_questions)
        return all_questions  #Now returns a list of strings
    
    except Exception as e:
        import traceback
        print('Exception in generate_questions_for_topic:', traceback.format_exc())
        return {"error": str(e)}

