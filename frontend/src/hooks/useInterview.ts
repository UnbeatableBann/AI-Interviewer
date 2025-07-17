import { useState, useCallback, useRef } from 'react';
import { InterviewSession, Question, InterviewResponse, InterviewResult, StudentInfo, JobDescription, AIBotState } from '../types';

export const useInterview = () => {
  const [currentSession, setCurrentSession] = useState<InterviewSession | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [aiBot, setAiBot] = useState<AIBotState>({
    isListening: false,
    isSpeaking: false,
    currentEmotion: 'neutral',
    message: 'Hello! I\'m your AI interviewer. Ready to begin?',
    isWaitingForResponse: false
  });
  const [isRecording, setIsRecording] = useState(false);
  const [interviewStartTime, setInterviewStartTime] = useState<number>(0);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const speechRecognitionRef = useRef<any>(null);

  // Speech synthesis for AI bot
  const speak = useCallback((text: string) => {
    if ('speechSynthesis' in window) {
      // Stop any ongoing speech
      speechSynthesis.cancel();
      
      setAiBot(prev => ({ ...prev, isSpeaking: true, message: text, isWaitingForResponse: false }));
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1.1;
      utterance.volume = 0.8;
      
      utterance.onend = () => {
        setAiBot(prev => ({ ...prev, isSpeaking: false, isWaitingForResponse: true }));
      };
      
      speechSynthesis.speak(utterance);
    }
  }, []);

  // Speech recognition for user responses
  const startListening = useCallback(async () => {
    try {
      // Start audio recording
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.start();
      setIsRecording(true);
      setAiBot(prev => ({ ...prev, isListening: true, currentEmotion: 'thinking', isWaitingForResponse: false }));

      // Start speech recognition if available
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        
        recognition.onresult = (event: any) => {
          let finalTranscript = '';
          for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
              finalTranscript += event.results[i][0].transcript;
            }
          }
          
          if (finalTranscript) {
            setAiBot(prev => ({ 
              ...prev, 
              message: `I heard: "${finalTranscript}". Please continue or click stop when finished.`
            }));
          }
        };
        
        recognition.start();
        speechRecognitionRef.current = recognition;
      }
    } catch (error) {
      console.error('Error starting audio recording:', error);
      alert('Unable to access microphone. Please check permissions.');
    }
  }, []);

  const stopListening = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setAiBot(prev => ({ ...prev, isListening: false, currentEmotion: 'happy', isWaitingForResponse: false }));
      
      // Stop speech recognition
      if (speechRecognitionRef.current) {
        speechRecognitionRef.current.stop();
        speechRecognitionRef.current = null;
      }
      
      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        console.log('Audio recorded:', audioBlob);
        
        // Simulate AI processing
        setTimeout(() => {
          setAiBot(prev => ({ 
            ...prev, 
            message: "Great response! I'm analyzing your answer. Let's move to the next question.",
            currentEmotion: 'happy'
          }));
        }, 1000);
      };
    }
  }, [isRecording]);

  const generateQuestions = useCallback((jobDescription: JobDescription): Question[] => {
    const baseQuestions: Omit<Question, 'id'>[] = [
      {
        text: `Hello! Welcome to your interview for the ${jobDescription.title} position at ${jobDescription.company}. Let's start with a simple question - tell me about yourself and why you're interested in this role.`,
        type: 'behavioral',
        timeLimit: 120,
        difficulty: 'easy'
      },
      {
        text: `That's great! Now, what specifically attracts you to ${jobDescription.company}, and how do you see yourself contributing to our team?`,
        type: 'behavioral',
        timeLimit: 90,
        difficulty: 'easy'
      },
      {
        text: "Can you describe a challenging situation you faced in your previous experience and how you overcame it? I'm particularly interested in your problem-solving approach.",
        type: 'situational',
        timeLimit: 180,
        difficulty: 'medium'
      },
      {
        text: "What would you say are your greatest strengths, and can you provide a specific example of how these strengths helped you achieve a goal?",
        type: 'behavioral',
        timeLimit: 120,
        difficulty: 'medium'
      },
      {
        text: jobDescription.type === 'technical' 
          ? "Let's discuss a technical challenge. Walk me through your approach to solving a complex problem in your field. What tools and methodologies do you typically use?"
          : "How do you handle pressure and tight deadlines? Can you share an example where you had to deliver results under challenging circumstances?",
        type: jobDescription.type === 'technical' ? 'technical' : 'situational',
        timeLimit: 240,
        difficulty: 'hard'
      },
      {
        text: "Finally, where do you see yourself in the next 3-5 years, and how does this position align with your career goals?",
        type: 'behavioral',
        timeLimit: 120,
        difficulty: 'medium'
      }
    ];

    return baseQuestions.map((q, index) => ({
      ...q,
      id: `q-${index + 1}`
    }));
  }, []);

  const startInterview = useCallback((studentInfo: StudentInfo, jobDescription: JobDescription) => {
    const questions = generateQuestions(jobDescription);
    const session: InterviewSession = {
      id: Math.random().toString(36).substr(2, 9),
      userId: 'current-user',
      jobDescription,
      studentInfo,
      questions,
      responses: [],
      result: null,
      status: 'in-progress',
      createdAt: new Date().toISOString(),
      duration: 0,
      currentQuestionIndex: 0
    };

    setCurrentSession(session);
    setCurrentQuestionIndex(0);
    setInterviewStartTime(Date.now());
    
    // AI bot introduces itself and starts the interview
    setTimeout(() => {
      speak(`Hello ${studentInfo.name}! I'm your AI interviewer today. I'll be conducting a comprehensive interview for the ${jobDescription.title} position. We'll have about 6 questions, and you can take your time to answer each one. Let's begin!`);
    }, 1000);

    return session;
  }, [generateQuestions, speak]);

  const submitResponse = useCallback((questionId: string, answer: string, duration: number, audioBlob?: Blob) => {
    if (!currentSession) return;

    // Mock AI analysis - in production, this would use real AI services
    const confidence = Math.floor(Math.random() * 30) + 70; // 70-100
    const clarity = Math.floor(Math.random() * 25) + 75; // 75-100
    const emotionalTones = ['confident', 'nervous', 'enthusiastic', 'calm', 'passionate'];
    const emotionalTone = emotionalTones[Math.floor(Math.random() * emotionalTones.length)];

    const response: InterviewResponse = {
      questionId,
      answer,
      audioBlob,
      duration,
      confidence,
      clarity,
      emotionalTone
    };

    const updatedSession = {
      ...currentSession,
      responses: [...currentSession.responses, response]
    };

    setCurrentSession(updatedSession);
  }, [currentSession]);

  const nextQuestion = useCallback(() => {
    if (!currentSession) return false;
    
    if (currentQuestionIndex < currentSession.questions.length - 1) {
      const nextIndex = currentQuestionIndex + 1;
      setCurrentQuestionIndex(nextIndex);
      
      // AI bot asks the next question
      setTimeout(() => {
        const nextQuestion = currentSession.questions[nextIndex];
        speak(nextQuestion.text);
      }, 2000);
      
      return true;
    }
    return false;
  }, [currentSession, currentQuestionIndex, speak]);

  const stopInterview = useCallback(() => {
    if (!currentSession) return null;

    const stoppedSession = {
      ...currentSession,
      status: 'stopped' as const,
      duration: Math.floor((Date.now() - interviewStartTime) / 1000),
      completedAt: new Date().toISOString()
    };

    setCurrentSession(stoppedSession);
    
    // AI bot acknowledges the stop
    speak("Interview stopped. Thank you for your time. You can review your responses and continue later if needed.");
    
    return stoppedSession;
  }, [currentSession, interviewStartTime, speak]);

  const completeInterview = useCallback((): InterviewResult | null => {
    if (!currentSession || currentSession.responses.length === 0) return null;

    const responses = currentSession.responses;
    const avgConfidence = responses.reduce((sum, r) => sum + r.confidence, 0) / responses.length;
    const avgClarity = responses.reduce((sum, r) => sum + r.clarity, 0) / responses.length;
    const interviewDuration = Math.floor((Date.now() - interviewStartTime) / 1000);
    const completionRate = (responses.length / currentSession.questions.length) * 100;
    
    const result: InterviewResult = {
      overallScore: Math.floor((avgConfidence + avgClarity + completionRate) / 3),
      categoryScores: {
        communication: Math.floor(avgClarity),
        technical: Math.floor(Math.random() * 20) + 75,
        confidence: Math.floor(avgConfidence),
        clarity: Math.floor(avgClarity),
        emotionalIntelligence: Math.floor(Math.random() * 25) + 70
      },
      responses,
      feedback: [
        "Your responses demonstrated good structure and thoughtfulness.",
        "You maintained professional composure throughout the interview.",
        "Your examples were relevant and well-articulated.",
        "Consider providing more quantified achievements in future interviews."
      ],
      recommendations: [
        "Practice the STAR method for behavioral questions",
        "Research more about the company's recent developments",
        "Work on reducing filler words for clearer communication",
        "Prepare more specific examples of your achievements"
      ],
      strengths: [
        "Clear and articulate communication",
        "Professional demeanor and confidence",
        "Good use of relevant examples",
        "Strong technical knowledge demonstration"
      ],
      areasForImprovement: [
        "Could provide more quantified results",
        "Body language and eye contact",
        "Elaborating on leadership experiences",
        "Asking more insightful questions about the role"
      ],
      interviewDuration,
      completionRate
    };

    const completedSession = {
      ...currentSession,
      result,
      status: 'completed' as const,
      duration: interviewDuration,
      completedAt: new Date().toISOString()
    };

    setCurrentSession(completedSession);
    
    // Store interview in database for HR dashboard
    const interviews = JSON.parse(localStorage.getItem('interviews') || '[]');
    interviews.push(completedSession);
    localStorage.setItem('interviews', JSON.stringify(interviews));
    
    // AI bot concludes the interview
    speak(`Excellent! We've completed the interview. You scored ${result.overallScore} out of 100. I'll now prepare your detailed feedback report. Thank you for your time!`);
    
    return result;
  }, [currentSession, interviewStartTime, speak]);

  const getCurrentQuestion = useCallback(() => {
    if (!currentSession) return null;
    return currentSession.questions[currentQuestionIndex] || null;
  }, [currentSession, currentQuestionIndex]);

  return {
    currentSession,
    currentQuestionIndex,
    aiBot,
    isRecording,
    startInterview,
    submitResponse,
    nextQuestion,
    stopInterview,
    completeInterview,
    getCurrentQuestion,
    startListening,
    stopListening,
    speak,
    questionsRemaining: currentSession ? currentSession.questions.length - currentQuestionIndex - 1 : 0,
    progress: currentSession ? ((currentQuestionIndex + 1) / currentSession.questions.length) * 100 : 0
  };
};