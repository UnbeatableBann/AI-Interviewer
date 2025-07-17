from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
import io
from PIL import Image

"""
When the user opens the web page, the camera starts automatically, and the video feed is displayed in the <video> element.
The JavaScript periodically captures frames from the video feed and sends them to the Flask server, which uses OpenCV for face detection.
The Flask server processes the image, detects faces, and returns their coordinates.
The JavaScript uses these coordinates to draw face detection boxes over the video feed in real-time.
"""

app = Flask(__name__)

# Load OpenCV face detector
# This loads a pre-trained Haar Cascade model for frontal face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

@app.route('/')
def index():
    # Render the front-end HTML page
    return render_template('index.html')

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

if __name__ == '__main__':
    # Run the Flask app on localhost with debugging enabled
    app.run(debug=True, host='0.0.0.0', port=5000)