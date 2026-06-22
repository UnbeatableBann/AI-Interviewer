"use client";

import React, { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { useInterviewStore, Question, ResponseItem } from "@/stores/interview-store";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Mic,
  MicOff,
  Send,
  Pause,
  Play,
  CheckCircle2,
  Clock,
  ChevronRight,
  Sparkles,
  HelpCircle,
  Keyboard,
  CheckCircle,
  AlertCircle
} from "lucide-react";
import Link from "next/link";

export default function ActiveInterviewRoom() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.id as string;

  const {
    activeSessionId,
    status,
    questions,
    responses,
    remainingTime,
    isRecording,
    recordingDuration,
    setSession,
    startRecording,
    stopRecording,
    incrementDuration,
    decrementRemainingTime,
    resetInterviewStore
  } = useInterviewStore();

  const [inputMode, setInputMode] = useState<"voice" | "text">("voice");
  const [typedAnswer, setTypedAnswer] = useState("");
  const [transcribedText, setTranscribedText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // References for Web Speech API
  const recognitionRef = useRef<any>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const durationTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Scaffolding questions loop internally if API not configured
  const mockSessionSequence: Question[] = [
    {
      id: "q-1",
      session_id: sessionId,
      question_text: "Let's start with your background. How do you design tenant-isolated backend applications to comply with SOC2 data boundaries?",
      question_type: "PRIMARY",
      difficulty: "MEDIUM",
      skills_assessed: ["Multi-Tenancy", "Security & Compliance"],
      order: 1,
      created_at: new Date().toISOString(),
    },
    {
      id: "q-2",
      session_id: sessionId,
      question_text: "You mentioned RLS isolation. What performance overheads do you anticipate when scaling row-level filters to millions of concurrent reads, and how do you mitigate them?",
      question_type: "FOLLOW_UP",
      difficulty: "HARD",
      skills_assessed: ["PostgreSQL RLS", "Query Optimization"],
      order: 2,
      created_at: new Date().toISOString(),
    },
    {
      id: "q-3",
      session_id: sessionId,
      question_text: "Great. Now explain your approach to managing distributed locks using Redis. How do you handle network partitions (split-brain scenarios)?",
      question_type: "PRIMARY",
      difficulty: "HARD",
      skills_assessed: ["Distributed Locking", "Redis Infrastructure"],
      order: 3,
      created_at: new Date().toISOString(),
    }
  ];

  // Initialize session state on mount
  useEffect(() => {
    // Scaffold initial state
    setSession({
      id: sessionId,
      status: "RUNNING",
      questions: [mockSessionSequence[0]],
      responses: [],
      remaining_time: 1800,
    });

    // Start session ticker
    timerRef.current = setInterval(() => {
      decrementRemainingTime();
    }, 1000);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (durationTimerRef.current) clearInterval(durationTimerRef.current);
      resetInterviewStore();
    };
  }, [sessionId]);

  // Handle active speech recognition recording
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const rec = new SpeechRecognition();
        rec.continuous = true;
        rec.interimResults = true;
        rec.lang = "en-US";

        rec.onresult = (event: any) => {
          let interimTranscript = "";
          let finalTranscript = "";

          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              finalTranscript += event.results[i][0].transcript;
            } else {
              interimTranscript += event.results[i][0].transcript;
            }
          }
          setTranscribedText(finalTranscript || interimTranscript);
        };

        rec.onerror = (e: any) => {
          console.error("Speech Recognition Error:", e);
          if (e.error !== "no-speech") {
            setError(`Speech Recognition failed: ${e.error}. Type response instead.`);
            setInputMode("text");
          }
        };

        recognitionRef.current = rec;
      }
    }
  }, []);

  const handleToggleMic = () => {
    if (isRecording) {
      // Stop recording
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      stopRecording();
      if (durationTimerRef.current) {
        clearInterval(durationTimerRef.current);
      }
    } else {
      // Start recording
      setError(null);
      setTranscribedText("");
      if (recognitionRef.current) {
        try {
          recognitionRef.current.start();
          startRecording();
          durationTimerRef.current = setInterval(() => {
            incrementDuration();
          }, 1000);
        } catch (e) {
          setError("Microphone permission denied or initialization error.");
          setInputMode("text");
        }
      } else {
        setError("Browser Web Speech API not supported. Enter response manually.");
        setInputMode("text");
      }
    }
  };

  const handlePostResponse = async () => {
    const finalAnswer = inputMode === "voice" ? transcribedText : typedAnswer;
    if (!finalAnswer.trim()) return;

    setSubmitting(true);
    setError(null);

    try {
      // Simulate backend AI adapter processing STT transcription & next question adapting
      await new Promise((resolve) => setTimeout(resolve, 1500));

      const activeQuestion = questions[questions.length - 1];

      // Add user response item
      const newResponse: ResponseItem = {
        id: `resp-${Date.now()}`,
        session_id: sessionId,
        question_id: activeQuestion.id,
        response_text: finalAnswer,
        created_at: new Date().toISOString(),
        feedback: {
          score: 4.2,
          alignment: "High relevance to isolated logical boundaries",
        }
      };

      // Progress to next question in sequence if available, or complete session
      const nextOrder = questions.length + 1;
      const nextQuestion = mockSessionSequence.find((q) => q.order === nextOrder);

      if (nextQuestion) {
        setSession({
          id: sessionId,
          status: "RUNNING",
          questions: [...questions, nextQuestion],
          responses: [...responses, newResponse],
          remaining_time: remainingTime,
        });
      } else {
        setSession({
          id: sessionId,
          status: "COMPLETED",
          questions: questions,
          responses: [...responses, newResponse],
          remaining_time: remainingTime,
        });
        if (timerRef.current) clearInterval(timerRef.current);
        router.push(`/candidate/reports/${sessionId}`);
      }

      // Reset text inputs
      setTypedAnswer("");
      setTranscribedText("");
      if (isRecording) {
        handleToggleMic();
      }
    } catch (err: any) {
      setError("Failed to submit response. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const activeQuestion = questions[questions.length - 1];
  const formatTime = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const secs = sec % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="space-y-6 max-w-6xl font-sans selection:bg-primary selection:text-primary-foreground">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-border pb-4 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-muted-foreground">
              Core Session Loop
            </span>
            <span className="h-1.5 w-1.5 rounded-full bg-success animate-pulse" />
            <span className="text-[10px] font-mono text-success">Secure Channel Isolated</span>
          </div>
          <h1 className="text-lg font-semibold tracking-tight mt-1">Adaptive AI Technical Interview</h1>
        </div>

        {/* Timer slot */}
        <div className="flex items-center gap-3 bg-card border border-border px-4 py-2 rounded-md font-mono text-sm shadow-sm">
          <Clock className="h-4 w-4 text-muted-foreground" />
          <span className="font-semibold">{formatTime(remainingTime)}</span>
          <span className="text-[10px] text-muted-foreground">remaining</span>
        </div>
      </div>

      {error && (
        <div className="rounded-md bg-destructive/10 border border-destructive/20 p-3 text-xs text-destructive font-mono flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          {error}
        </div>
      )}

      {/* Main Grid layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Questions & Input */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active Question Display */}
          {activeQuestion && (
            <div className="rounded-lg border border-border bg-card p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase font-bold tracking-wider text-muted-foreground font-mono">
                  Question {activeQuestion.order} of 3
                </span>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-[10px]">
                    {activeQuestion.difficulty}
                  </Badge>
                  <Badge variant="secondary" className="text-[10px]">
                    {activeQuestion.question_type}
                  </Badge>
                </div>
              </div>
              <p className="text-base font-semibold leading-relaxed text-foreground">
                {activeQuestion.question_text}
              </p>
            </div>
          )}

          {/* Answer Input Panel */}
          <div className="rounded-lg border border-border bg-card p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <span className="text-xs font-semibold text-muted-foreground">Candidate Response Input</span>
              <div className="flex items-center gap-1">
                <Button
                  variant={inputMode === "voice" ? "secondary" : "ghost"}
                  size="sm"
                  className="text-xs h-7 px-2"
                  onClick={() => setInputMode("voice")}
                >
                  <Mic className="h-3 w-3 mr-1" />
                  Voice Mode
                </Button>
                <Button
                  variant={inputMode === "text" ? "secondary" : "ghost"}
                  size="sm"
                  className="text-xs h-7 px-2"
                  onClick={() => setInputMode("text")}
                >
                  <Keyboard className="h-3 w-3 mr-1" />
                  Text Mode
                </Button>
              </div>
            </div>

            {/* Input States */}
            {inputMode === "voice" ? (
              <div className="flex flex-col items-center py-6 space-y-4 bg-accent/10 rounded-lg border border-dashed border-border">
                {isRecording ? (
                  <div className="flex items-center gap-2">
                    {/* Pulsing Visual Waveform */}
                    <div className="flex items-end gap-1 h-8 px-4">
                      <span className="w-1 bg-primary rounded-full animate-bounce h-4" style={{ animationDelay: "0.1s" }} />
                      <span className="w-1 bg-primary rounded-full animate-bounce h-7" style={{ animationDelay: "0.2s" }} />
                      <span className="w-1 bg-primary rounded-full animate-bounce h-5" style={{ animationDelay: "0.3s" }} />
                      <span className="w-1 bg-primary rounded-full animate-bounce h-8" style={{ animationDelay: "0.4s" }} />
                      <span className="w-1 bg-primary rounded-full animate-bounce h-3" style={{ animationDelay: "0.5s" }} />
                    </div>
                    <span className="text-xs font-mono font-semibold">
                      Recording: {recordingDuration}s
                    </span>
                  </div>
                ) : (
                  <p className="text-xs text-muted-foreground">Click the microphone to begin speaking.</p>
                )}

                <Button
                  variant={isRecording ? "destructive" : "default"}
                  size="lg"
                  className="rounded-full h-14 w-14 p-0 animate-pulse"
                  onClick={handleToggleMic}
                >
                  {isRecording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
                </Button>

                {transcribedText && (
                  <div className="w-full px-6 pt-4 border-t border-border">
                    <label className="text-[10px] font-bold text-muted-foreground uppercase block mb-1">
                      Live Transcription Preview
                    </label>
                    <p className="text-xs text-foreground bg-card p-3 rounded border border-border leading-normal font-mono">
                      {transcribedText}
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-2">
                <textarea
                  className="w-full min-h-[140px] p-3 rounded-lg border border-input bg-background text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono"
                  placeholder="Type your structured engineering answer here..."
                  value={typedAnswer}
                  onChange={(e) => setTypedAnswer(e.target.value)}
                />
              </div>
            )}

            {/* Submit responses triggers */}
            <div className="flex justify-between items-center pt-2">
              <span className="text-[10px] text-muted-foreground font-mono">
                Pressing Submit triggers STT stitching & scoring.
              </span>
              <Button
                size="sm"
                className="gap-1.5 text-xs font-mono"
                loading={submitting}
                disabled={inputMode === "voice" ? !transcribedText.trim() : !typedAnswer.trim()}
                onClick={handlePostResponse}
              >
                SUBMIT ANSWER
                <Send className="h-3 w-3" />
              </Button>
            </div>
          </div>
        </div>

        {/* Right Column - Status Metrics */}
        <div className="space-y-6">
          {/* Target Assessment List */}
          <div className="rounded-lg border border-border bg-card p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-4 border-b border-border pb-3">
              <Sparkles className="h-4 w-4 text-muted-foreground" />
              <h2 className="text-sm font-semibold tracking-tight">Active Core Competencies</h2>
            </div>

            <div className="space-y-3">
              {activeQuestion?.skills_assessed?.map((skill, index) => (
                <div key={index} className="flex items-center gap-2.5 text-xs">
                  <CheckCircle className="h-4 w-4 text-success shrink-0" />
                  <span className="font-semibold text-foreground">{skill}</span>
                </div>
              ))}
              {activeQuestion?.skills_assessed && activeQuestion.skills_assessed.length === 0 && (
                <p className="text-xs text-muted-foreground">No specific skill target specified.</p>
              )}
            </div>
          </div>

          {/* Session Timeline Progression */}
          <div className="rounded-lg border border-border bg-card p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-4 border-b border-border pb-3">
              <HelpCircle className="h-4 w-4 text-muted-foreground" />
              <h2 className="text-sm font-semibold tracking-tight">Timeline Log</h2>
            </div>

            <div className="space-y-4">
              {responses.map((resp, idx) => (
                <div key={idx} className="flex gap-3 text-xs">
                  <div className="flex flex-col items-center">
                    <span className="h-2 w-2 rounded-full bg-success shrink-0" />
                    {idx < responses.length - 1 && <span className="w-[1px] h-full bg-border" />}
                  </div>
                  <div className="flex-1 space-y-1">
                    <p className="font-semibold text-muted-foreground font-mono">Q{idx + 1} Answered</p>
                    <p className="text-muted-foreground line-clamp-2 leading-relaxed">{resp.response_text}</p>
                  </div>
                </div>
              ))}
              
              <div className="flex gap-3 text-xs">
                <span className="h-2 w-2 rounded-full bg-primary shrink-0 animate-ping" />
                <div className="flex-1">
                  <p className="font-semibold text-foreground font-mono">Q{responses.length + 1} In Progress</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
