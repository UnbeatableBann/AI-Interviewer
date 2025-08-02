# AI Interviewer

## Overview
AI Interviewer is an intelligent platform designed to simulate real-life interview scenarios using AI-driven bots. It provides a seamless experience for both candidates and HR professionals, featuring real-time feedback, face detection, and interactive Q&A sessions.

## Features
- AI-powered interview bot for realistic Q&A
- Face detection and analysis
- User authentication and role-based access (Candidate/HR)
- HR dashboard for managing interviews
- Real-time feedback and scoring
- Modern, interactive frontend (React + TypeScript)
- RESTful backend (Flask, FastAPI)

## Tech Stack
- **Frontend:** React, TypeScript, Vite
- **Backend:** Python, Flask, FastAPI
- **Face Detection:** Custom Python module
- **Authentication:** Appwrite/Supabase (configurable)

## Folder Structure
```
AI Interviewer/
├── backend/
│   ├── app.py                # Main FastAPI app
│   ├── appwrite_client.py    # Appwrite integration
│   ├── face_detection/       # Face detection module
│   ├── logger.py             # Logging
│   ├── redis_client.py       # Redis integration
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── pages/            # Page components
│   │   └── types/            # TypeScript types
│   ├── index.html            # Frontend entry point
│   └── ...
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn
- (Optional) Appwrite/Supabase account for authentication

### Backend Setup
1. Navigate to the backend directory:
   ```sh
   cd backend
   ```
2. (Optional) Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the Flask server:
   ```sh
   python app.py
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```sh
   cd frontend
   ```
2. Install dependencies:
   ```sh
   npm install
   # or
   yarn
   ```
3. Start the development server:
   ```sh
   npm run dev
   # or
   yarn dev
   ```

### Environment Variables
- Configure backend and frontend environment variables as needed (e.g., API endpoints, authentication keys).

## Usage
- Access the frontend at `http://localhost:3000` (default Vite port).
- The backend API runs at `http://localhost:5000` (default Flask port).
- Register/login as a candidate or HR to start/interview.
- HR can manage interviews and view analytics on the dashboard.

## Contribution Guidelines
1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License.

## Contact
For questions or support, please contact the maintainer: [Shadab Jamadar](mailto:shadabjamadar4@gmail.com) 
