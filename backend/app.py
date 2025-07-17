import traceback
import io
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import requests
import os
import uuid
from gtts import gTTS
from appwrite.input_file import InputFile
from appwrite_client import supabase, insert_to_collection, fetch_clean_documents, storage, APPWRITE_BUCKET_ID, APPWRITE_PROJECT_ID
from utility import evaluate_answer, requirements, generate_questions_for_topic
import speech_recognition as sr
from pydub import AudioSegment
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import base64
from PIL import Image

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS)


# @app.route("/", methods=['GET'])
# def index():
#     return render_template("index.html")


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify the server is running."""
    return jsonify({"status": "ok"}), 200

@app.route("/save-personal-info", methods=["POST"])
def save_personal_info():
    """Save user personal info and avatar to the database and storage."""
    try:
        # Parse and validate the incoming JSON data
        data = request.json
        if not data or 'full_name' not in data or 'email' not in data:
            return jsonify({'error': 'Missing full_name or email in request'}), 400
        
        # Extract user information from the request
        full_name = data.get("full_name", "")
        email = data.get("email", "")
        phone_number = data.get("phone_number", "")
        education_level = data.get("education_level", "")
        field_of_study = data.get("field_of_study", "")
        graduation_year = data.get("graduation_year", "")
        work_experience = data.get("work_experience", "")
        skills = data.get("skills", "")
        user_id = data.get("userId") # Generate a unique user ID

        # Handle avatar image upload (optional)
        avatar_url = None
        image_file = request.files.get("profilePhoto")
        if image_file:
            file_id = f"{user_id}_avatar"
            file_input = InputFile.from_wsgi(image_file)
            # Upload the file to Appwrite Storage
            uploaded_file = storage.create_file(
                bucket_id= APPWRITE_BUCKET_ID,
                file_id=file_id,
                file=file_input
            )

            # Create public URL to access image
            avatar_url = f"https://cloud.appwrite.io/v1/storage/buckets/avatars/files/{file_id}/view?project={APPWRITE_PROJECT_ID}"

        # Prepare the data for insertion into the database
        value = {
            "user_id": user_id,
            "full_name": full_name,
            "email": email,
            "phone_number": phone_number,
            "education_level": education_level,
            "field_of_study": field_of_study,
            "graduation_year": graduation_year,
            "work_experience": work_experience,
            "skils": skills,
            "avatar_url": avatar_url if avatar_url else None
        }
        # Insert the data into the "user_info" table
        insert_result = insert_to_collection(table_name="user_info", value=[value])
        
        # Check for insertion errors
        if insert_result and isinstance(insert_result, dict) and insert_result.get("error"):
            return jsonify({"error": "Failed to save personal info"}), 500
        
        return jsonify({"message": "Personal info saved successfully", "user_id": user_id})
    
    except Exception as e:
        print('Exception in /save-personal-info:', traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# Route to handle for each question submission (do not save each que one by one, do it for altogether)
@app.route("/question-submission", methods=["POST"])
def question_submission():
    """Save a user's answer and evaluation for a question."""
    try:
        data = request.json
        interview_id = data["interview_id"]
        userid = data["userid"]
        question = data["question"]
        user_answer = data["user_answer"]
        created_at = data["created_at"]
        duration = data["duration"]
        # Validate required fields
        if not userid or not question or not user_answer:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Evaluate the user's answer using the LLM
        eval_result = evaluate_answer(question, user_answer)

        # Prepare the value for insertion
        value={
            "interview_id": interview_id,
            "userid": userid,
            "question": question,
            "user_answer": user_answer,
            "score": eval_result,
            "created_at": created_at,
            "duration": duration
        }
        # Insert the response into the evaluation_table
        insert_result = insert_to_collection(table_name="evaluation_table", value=[value])
        if insert_result and isinstance(insert_result, dict) and insert_result.get("error"):
            return jsonify({
                "error": "Failed to save response. Please try submitting again.",
                "details": insert_result["error"]
            }), 500

        return jsonify({"message": "Response submitted successfully"})
    
    except Exception as e:
        print('Exception in /submit-response:', traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route('/generate_question', methods=['POST'])
def generate_question():
    """Generate interview questions based on job description."""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Missing userid in request'}), 400
        user_id = data.get('user_id')
        timestamp= data.get('timestamp', '')
        print(f"🔍🔍🔍🔍Generating questions for user_id: {user_id} at {timestamp}")

        # Fetch job description from the database
        job_description = fetch_clean_documents(table_name="job_description", query={"created_at": timestamp,"user_id": user_id})
        print(f"🎯🎯🎯🎯Fetched job description: {job_description}")

        if not job_description or job_description.get("error"):
            return jsonify({"error": "Failed to fetch job description"}), 500
        
        # Extract requirements and generate questions using LLM
        requirements_list = requirements(job_description)
        gen_questions = generate_questions_for_topic(job_description, requirements_list)
        return jsonify({"questions": gen_questions})
    except Exception as e:
        print('Exception in /generate_question:', traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route("/tts", methods=["POST"])
def text_to_speech():
    """Convert text to speech and return as audio file."""
    data = request.get_json()
    text = data.get("text")
    lang = data.get("lang", "en")

    if not text:
        return jsonify({"error": "Text is required"}), 400

    try:
        # Convert text to speech using gTTS
        buf = io.BytesIO()
        tts = gTTS(text, lang=lang)
        tts.write_to_fp(buf)
        buf.seek(0)
        return send_file(buf, mimetype="audio/mpeg", as_attachment=False)
    except Exception as e:
        print('Exception in /tts:', traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route("/stt", methods=["POST"])
def speech_to_text():
    """Convert uploaded audio to text using speech recognition."""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        audio_file = request.files['audio']
        # Convert to wav if needed
        audio = AudioSegment.from_file(audio_file)
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        return jsonify({'text': text})
    except Exception as e:
        print('Exception in /stt:', traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route("/save-job-description", methods=["POST"])
def save_job_description():
    """Save job description details to the database."""
    try:
        print("saving job description")
        data = request.json
        if not data or 'description' not in data:
            return jsonify({'error': 'Missing job_description in request'}), 400
        # Extract job description details
        job_title = data.get("title", "")
        company_name = data.get("company", "")
        experience_level = data.get("level", "")
        interview_type = data.get("type", "")
        description = data.get("description", "")
        requirements= data.get("requirements", "")
        user_id= data.get("userId")
        timestamp = data.get("timestamp", "")
        print(timestamp)
        value = {
            "user_id" : user_id,
            "job_title": job_title,
            "company_name": company_name,
            "experience_level": experience_level,
            "interview_type": interview_type,
            "description": description,
            "requirements": requirements,
            "created_at": timestamp
        }
        # Insert job description into the database
        insert_result = insert_to_collection(table_name="job_description", value=[value])
        if insert_result and isinstance(insert_result, dict) and insert_result.get("error"):
            return jsonify({"error": "Failed to save job description"}), 500

        return jsonify({"message": "Job description saved successfully"})

    except Exception as e:
        print('Exception in /job_description:', traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# Route for evaluating all answers
@app.route('/evaluate_all_answer', methods=['POST'])
def evaluate_all_answer():
    """Compute and return the average score for all responses in an interview."""
    
    try:
        data = request.get_json()
        interview_id = data.get('interview_id')

        if not interview_id:
            return jsonify({'error': 'interview_id is required'}), 400

        # Fetch all responses from Supabase
        response = fetch_clean_documents(table_name="evaluation_table",query={"interview_id": interview_id})

        if hasattr(response, "error") and response.error:
            return jsonify({"error": f"Supabase error: {response.error}"}), 500

        scores = [item['Score'] for item in response.data if 'Score' in item]

        if not scores:
            return jsonify({"message": "No scores found for this interview"}), 404

        avg_score = sum(scores) / len(scores)

        return jsonify({
            "interview_id": interview_id,
            "average_score": round(avg_score, 2)
        })

    except Exception as e:
        print('Exception in /evaluate_all_answer:', traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/user_details', methods=['POST'])
def user_details():
    """Fetch user details based on user ID."""
    try:
        data = request.json
        if not data or 'userid' not in data:
            return jsonify({'error': 'Missing userid in request'}), 400
        
        userid = data['userid']
        # Fetch user details from the database
        user_info = fetch_clean_documents(table_name="user_info", query={"user_id": userid})
        
        if hasattr(user_info, "error") and user_info.error:
            return jsonify({"error": f"Supabase error: {user_info.error}"}), 500
        
        return jsonify(user_info)
    
    except Exception as e:
        print('Exception in /user_details:', traceback.format_exc())
        return jsonify({'error': str(e)}), 500


face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

@app.route('/detect', methods=['POST'])
def detect_faces():
    try:
        # Get image data from the request
        image_data = request.json['image']
        
        # Remove the data URL prefix (e.g., "data:image/jpeg;base64,")
        image_data = image_data.split(',')[1]
        
        # Decode the base64 image into bytes
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert the image to OpenCV format (BGR)
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        # Convert the image to grayscale for face detection
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the image
        # The detectMultiScale method returns a list of rectangles where faces are detected
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Prepare the list of detected faces for the JSON response
        faces_list = []
        for (x, y, w, h) in faces:
            faces_list.append({
                'x': int(x),
                'y': int(y),
                'width': int(w),
                'height': int(h)
            })
        
        # Return the detected faces and their count as a JSON response
        return jsonify({
            'success': True,
            'faces': faces_list,
            'count': len(faces_list)
        })
        
    except Exception as e:
        # Handle any errors and return an error response
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == "__main__":
    app.run(debug=True)

