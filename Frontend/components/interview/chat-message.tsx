import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import type { ChatMessage } from "@/types"
import { Bot, User } from "lucide-react"
import { cn } from "@/lib/utils"

interface ChatMessageProps {
  message: ChatMessage
}

export function ChatMessageComponent({ message }: ChatMessageProps) {
  const isAgent = message.sender === "agent"

  const categoryLabels = {
    knockout: "Pregunta Inicial",
    technical: "Técnica",
    soft_skills: "Habilidades Blandas",
  }

  const categoryColors = {
    knockout: "bg-gray-100 text-gray-800",
    technical: "bg-blue-100 text-blue-800",
    soft_skills: "bg-green-100 text-green-800",
  }

  return (
    <div
      className={cn(
        "flex gap-3 mb-4 animate-in fade-in slide-in-from-bottom-2 duration-300",
        !isAgent && "flex-row-reverse",
      )}
    >
      <Avatar className="h-8 w-8 flex-shrink-0">
        <AvatarFallback
          className={cn(isAgent ? "bg-muted text-muted-foreground" : "bg-primary text-primary-foreground")}
        >
          {isAgent ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
        </AvatarFallback>
      </Avatar>

      <div className={cn("flex flex-col gap-2 max-w-[75%]", !isAgent && "items-end")}>
        <div
          className={cn(
            "rounded-lg px-4 py-3 shadow-sm",
            isAgent ? "bg-muted text-foreground" : "bg-primary text-primary-foreground",
          )}
        >
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.message_text}</p>
        </div>

        <div className={cn("flex items-center gap-2 px-1", !isAgent && "flex-row-reverse")}>
          <span className="text-xs text-muted-foreground">
            {new Date(message.timestamp).toLocaleTimeString("es-ES", {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>

          {isAgent && message.question_category && (
            <Badge variant="secondary" className={cn("text-xs", categoryColors[message.question_category])}>
              {categoryLabels[message.question_category]}
            </Badge>
          )}

          {message.score !== undefined && (
            <Badge variant="outline" className="text-xs font-semibold">
              Puntuación: {message.score}/5
            </Badge>
          )}
        </div>

        {message.explanation && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg px-3 py-2 text-xs text-blue-900">
            <p className="font-medium mb-1">Evaluación:</p>
            <p>{message.explanation}</p>
          </div>
        )}
      </div>
    </div>
  )
}
