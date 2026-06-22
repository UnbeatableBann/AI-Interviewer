import { create } from "zustand";

export type SessionStatus = "CREATED" | "RUNNING" | "PAUSED" | "COMPLETED" | "FAILED";

export interface Question {
  id: string;
  session_id: string;
  question_text: string;
  question_type: string;
  difficulty: string;
  skills_assessed: string[] | null;
  order: number;
  created_at: string;
}

export interface ResponseItem {
  id: string;
  session_id: string;
  question_id: string;
  response_text: string;
  audio_url?: string;
  feedback?: any;
  created_at: string;
}

interface InterviewState {
  activeSessionId: string | null;
  status: SessionStatus | null;
  questions: Question[];
  responses: ResponseItem[];
  currentQuestionIndex: number;
  remainingTime: number; // in seconds
  isRecording: boolean;
  recordingDuration: number; // in seconds
  audioChunksQueue: Blob[];
  activeTimer: NodeJS.Timeout | null;
  
  setSession: (session: {
    id: string;
    status: SessionStatus;
    questions: Question[];
    responses: ResponseItem[];
    remaining_time?: number;
  }) => void;
  
  startRecording: () => void;
  stopRecording: () => void;
  addAudioChunk: (chunk: Blob) => void;
  clearAudioQueue: () => void;
  incrementDuration: () => void;
  decrementRemainingTime: () => void;
  resetInterviewStore: () => void;
}

export const useInterviewStore = create<InterviewState>((set, get) => ({
  activeSessionId: null,
  status: null,
  questions: [],
  responses: [],
  currentQuestionIndex: 0,
  remainingTime: 1800, // 30 mins default
  isRecording: false,
  recordingDuration: 0,
  audioChunksQueue: [],
  activeTimer: null,

  setSession: (session) => {
    set({
      activeSessionId: session.id,
      status: session.status,
      questions: session.questions || [],
      responses: session.responses || [],
      currentQuestionIndex: session.questions ? session.questions.length : 0,
      remainingTime: session.remaining_time ?? get().remainingTime,
    });
  },

  startRecording: () => {
    set({ isRecording: true, recordingDuration: 0 });
  },

  stopRecording: () => {
    set({ isRecording: false });
  },

  addAudioChunk: (chunk) => {
    set((state) => ({
      audioChunksQueue: [...state.audioChunksQueue, chunk],
    }));
  },

  clearAudioQueue: () => {
    set({ audioChunksQueue: [] });
  },

  incrementDuration: () => {
    set((state) => ({ recordingDuration: state.recordingDuration + 1 }));
  },

  decrementRemainingTime: () => {
    set((state) => {
      const nextTime = state.remainingTime > 0 ? state.remainingTime - 1 : 0;
      if (nextTime === 0 && state.status === "RUNNING") {
        return { remainingTime: 0, status: "COMPLETED" };
      }
      return { remainingTime: nextTime };
    });
  },

  resetInterviewStore: () => {
    const { activeTimer } = get();
    if (activeTimer) {
      clearInterval(activeTimer);
    }
    set({
      activeSessionId: null,
      status: null,
      questions: [],
      responses: [],
      currentQuestionIndex: 0,
      remainingTime: 1800,
      isRecording: false,
      recordingDuration: 0,
      audioChunksQueue: [],
      activeTimer: null,
    });
  },
}));
