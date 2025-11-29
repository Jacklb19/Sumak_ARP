"use client"

import { useState, useEffect, useRef } from "react"
import { useParams, useRouter } from "next/navigation"
import { InterviewHeader } from "@/components/interview/interview-header"
import { ChatMessageComponent } from "@/components/interview/chat-message"
import { ChatInput } from "@/components/interview/chat-input"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { InterviewWebSocket, type WebSocketMessage } from "@/lib/websocket"
import type { ChatMessage, Application } from "@/types"
import { Loader2, WifiOff } from "lucide-react"
import { apiClient } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

type ConnectionStatus = "connecting" | "connected" | "disconnected" | "completed"

export default function InterviewPage() {
  const params = useParams()
  const router = useRouter()
  const applicationId = params.application_id as string
  const { toast } = useToast()

  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [status, setStatus] = useState<ConnectionStatus>("connecting")
  const [isTyping, setIsTyping] = useState(false)
  const [application, setApplication] = useState<Application | null>(null)
  const [showCompletionDialog, setShowCompletionDialog] = useState(false)
  const [finalScore, setFinalScore] = useState<number | null>(null)

  const wsRef = useRef<InterviewWebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const startTimeRef = useRef(new Date())

  useEffect(() => {
    fetchApplicationDetails()
  }, [applicationId])

  useEffect(() => {
    const token = localStorage.getItem("auth_token")
    if (!token) {
      router.push("/auth/login")
      return
    }

    console.log("[v0] Initializing WebSocket connection")
    const ws = new InterviewWebSocket(applicationId, token)
    wsRef.current = ws

    ws.connect(handleWebSocketMessage, handleWebSocketError, handleWebSocketOpen, handleWebSocketClose)

    return () => {
      console.log("[v0] Cleaning up WebSocket connection")
      ws.disconnect()
    }
  }, [applicationId])

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  const fetchApplicationDetails = async () => {
    try {
      const response = await apiClient.get(`/applications/${applicationId}`)
      setApplication(response.data)
    } catch (error) {
      console.error("[v0] Error fetching application:", error)
    }
  }

  const handleWebSocketOpen = () => {
    console.log("[v0] WebSocket connected successfully")
    setStatus("connected")
    toast({
      title: "Conectado",
      description: "La entrevista ha comenzado",
    })
  }

  const handleWebSocketClose = () => {
    console.log("[v0] WebSocket connection closed")
    if (status !== "completed") {
      setStatus("disconnected")
    }
  }

  const handleWebSocketError = (error: Event) => {
    console.error("[v0] WebSocket error:", error)
    setStatus("disconnected")
    toast({
      title: "Error de conexión",
      description: "Intentando reconectar...",
      variant: "destructive",
    })
  }

  const handleWebSocketMessage = (data: WebSocketMessage) => {
    console.log("[v0] Received WebSocket message:", data)

    switch (data.type) {
      case "connected":
        setStatus("connected")
        break

      case "question":
        setIsTyping(false)
        const questionMessage: ChatMessage = {
          id: `msg-${Date.now()}`,
          sender: "agent",
          message_text: data.message_text || "",
          timestamp: data.timestamp || new Date().toISOString(),
          question_category: data.question_category,
        }
        setMessages((prev) => [...prev, questionMessage])
        break

      case "score_update":
        if (messages.length > 0) {
          setMessages((prev) => {
            const updated = [...prev]
            const lastUserMessageIndex = [...updated].reverse().findIndex((m) => m.sender === "candidate")
            if (lastUserMessageIndex !== -1) {
              const actualIndex = updated.length - 1 - lastUserMessageIndex
              updated[actualIndex] = {
                ...updated[actualIndex],
                score: data.score,
                explanation: data.explanation,
              }
            }
            return updated
          })

          toast({
            title: "Respuesta evaluada",
            description: `Puntuación: ${data.score}/5`,
          })
        }
        break

      case "interview_completed":
        setIsTyping(false)
        setStatus("completed")
        setFinalScore(data.global_score || null)
        setShowCompletionDialog(true)
        break

      case "error":
        toast({
          title: "Error",
          description: data.message || "Ocurrió un error durante la entrevista",
          variant: "destructive",
        })
        break
    }
  }

  const handleSendMessage = (messageText: string) => {
    if (!wsRef.current || status !== "connected") {
      toast({
        title: "No conectado",
        description: "Esperando conexión...",
        variant: "destructive",
      })
      return
    }

    const candidateMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      sender: "candidate",
      message_text: messageText,
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, candidateMessage])
    setIsTyping(true)

    wsRef.current.send({
      type: "candidate_message",
      application_id: applicationId,
      message_text: messageText,
    })

    console.log("[v0] Sent candidate message")
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const handleCompletionDialogClose = () => {
    setShowCompletionDialog(false)
    router.push(`/dashboard/applications`)
  }

  if (!application) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen">
      <InterviewHeader
        jobTitle={application.job_title}
        companyName={application.company_name}
        startTime={startTimeRef.current}
        status={status}
      />

      {/* Connection Status Banner */}
      {status === "disconnected" && (
        <Alert variant="destructive" className="rounded-none border-x-0">
          <WifiOff className="h-4 w-4" />
          <AlertDescription>Conexión perdida. Reconectando automáticamente...</AlertDescription>
        </Alert>
      )}

      {status === "connecting" && (
        <Alert className="rounded-none border-x-0 bg-yellow-50 text-yellow-900 border-yellow-200">
          <Loader2 className="h-4 w-4 animate-spin" />
          <AlertDescription>Conectando con el agente de entrevista...</AlertDescription>
        </Alert>
      )}

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto bg-gradient-to-b from-background to-muted/20 p-6">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 && status === "connected" && (
            <div className="text-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
              <p className="text-muted-foreground">El agente está preparando la primera pregunta...</p>
            </div>
          )}

          {messages.map((message) => (
            <ChatMessageComponent key={message.id} message={message} />
          ))}

          {isTyping && (
            <div className="flex gap-3 mb-4">
              <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                <div className="flex gap-1">
                  <div
                    className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce"
                    style={{ animationDelay: "0ms" }}
                  />
                  <div
                    className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce"
                    style={{ animationDelay: "150ms" }}
                  />
                  <div
                    className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce"
                    style={{ animationDelay: "300ms" }}
                  />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <ChatInput
        onSend={handleSendMessage}
        disabled={status !== "connected" || isTyping || status === "completed"}
        placeholder={
          status === "completed"
            ? "La entrevista ha finalizado"
            : isTyping
              ? "Esperando respuesta del agente..."
              : "Escribe tu respuesta..."
        }
      />

      {/* Completion Dialog */}
      <Dialog open={showCompletionDialog} onOpenChange={setShowCompletionDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Entrevista completada</DialogTitle>
            <DialogDescription>Has completado todas las preguntas de la entrevista</DialogDescription>
          </DialogHeader>
          <div className="py-6 space-y-4">
            {finalScore !== null && (
              <div className="text-center">
                <p className="text-sm text-muted-foreground mb-2">Puntuación global</p>
                <p className="text-4xl font-bold text-primary">{finalScore.toFixed(1)}/100</p>
              </div>
            )}
            <p className="text-sm text-center text-muted-foreground">
              El reclutador revisará tu evaluación y se pondrá en contacto contigo pronto.
            </p>
          </div>
          <div className="flex gap-3">
            <Button onClick={handleCompletionDialogClose} className="flex-1">
              Ver mis postulaciones
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
