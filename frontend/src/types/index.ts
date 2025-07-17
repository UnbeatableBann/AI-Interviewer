export interface User {
  id: string;
  email: string;
  name: string;
  phone?: string;
  role: 'candidate' | 'hr';
  createdAt: string;
  avatar?: string;
  isVerified: boolean;
  company?: string;
}

export interface StudentInfo {
  name: string;
  email: string;
  phone: string;
  education: string;
  major: string;
  graduationYear: string;
  experience: string;
  skills: string[];
  profilePhoto?: string;
}

export interface JobDescription {
  title: string;
  company: string;
  description: string;
  requirements: string;
  level: 'entry' | 'mid' | 'senior';
  type: 'hr' | 'technical' | 'behavioral';
}

export interface Question {
  id: string;
  text: string;
  type: 'behavioral' | 'technical' | 'situational';
  timeLimit: number;
  difficulty: 'easy' | 'medium' | 'hard';
  audioUrl?: string;
}

export interface InterviewResponse {
  questionId: string;
  answer: string;
  audioBlob?: Blob;
  duration: number;
  confidence: number;
  clarity: number;
  emotionalTone: string;
}

export interface InterviewResult {
  overallScore: number;
  categoryScores: {
    communication: number;
    technical: number;
    confidence: number;
    clarity: number;
    emotionalIntelligence: number;
  };
  responses: InterviewResponse[];
  feedback: string[];
  recommendations: string[];
  strengths: string[];
  areasForImprovement: string[];
  interviewDuration: number;
  completionRate: number;
}

export interface InterviewSession {
  id: string;
  userId: string;
  jobDescription: JobDescription;
  studentInfo: StudentInfo;
  questions: Question[];
  responses: InterviewResponse[];
  result: InterviewResult | null;
  status: 'setup' | 'in-progress' | 'paused' | 'completed' | 'stopped';
  createdAt: string;
  completedAt?: string;
  duration: number;
  currentQuestionIndex: number;
}

export interface AIBotState {
  isListening: boolean;
  isSpeaking: boolean;
  currentEmotion: 'neutral' | 'happy' | 'thinking' | 'concerned';
  message: string;
  isWaitingForResponse: boolean;
}

export interface HRDashboardStats {
  totalInterviews: number;
  todayInterviews: number;
  averageScore: number;
  completionRate: number;
  topSkills: string[];
  recentInterviews: InterviewSession[];
}