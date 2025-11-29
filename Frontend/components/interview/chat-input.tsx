"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Send } from "lucide-react"
import { cn } from "@/lib/utils"

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

export function ChatInput({ onSend, disabled, placeholder = "Escribe tu respuesta..." }: ChatInputProps) {
  const [message, setMessage] = useState("")
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const maxChars = 500

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSend(message.trim())
      setMessage("")
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [message])

  const charsRemaining = maxChars - message.length
  const isOverLimit = message.length > maxChars

  return (
    <form onSubmit={handleSubmit} className="border-t bg-background p-4">
      <div className="space-y-2">
        <Textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          className="min-h-[60px] max-h-[200px] resize-none"
          rows={2}
        />

        <div className="flex items-center justify-between">
          <span className={cn("text-xs", isOverLimit ? "text-destructive font-medium" : "text-muted-foreground")}>
            {charsRemaining} caracteres restantes
          </span>

          <Button type="submit" size="sm" disabled={disabled || !message.trim() || isOverLimit}>
            <Send className="h-4 w-4 mr-2" />
            Enviar
          </Button>
        </div>
      </div>
    </form>
  )
}
