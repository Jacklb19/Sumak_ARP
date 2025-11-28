"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Bot, User, Send, Mic, Video, Phone, Settings } from "lucide-react";
import { cn } from "@/lib/utils";

interface Message {
  role: "ai" | "candidate";
  content: string;
  timestamp: string;
}

const initialMessages: Message[] = [
  {
    role: "ai",
    content:
      "Hello! Welcome to your AI-powered interview for the Senior Frontend Engineer position at TechCorp. I'm your AI interviewer, and I'll be guiding you through this conversation to learn more about your experience and skills.",
    timestamp: new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    }),
  },
  {
    role: "ai",
    content:
      "This interview will take approximately 30-45 minutes. Feel free to ask for clarification on any question. Are you ready to begin?",
    timestamp: new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    }),
  },
];

export function InterviewInterface() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = () => {
    if (!input.trim()) return;

    const newMessage: Message = {
      role: "candidate",
      content: input,
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    setMessages((prev) => [...prev, newMessage]);
    setInput("");
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponses = [
        "That's a great point. Can you elaborate more on the technical approach you took?",
        "Interesting! How did you handle the challenges that came with that decision?",
        "I appreciate the detailed response. Let me ask you about your experience with team collaboration.",
        "Excellent. Your approach shows strong problem-solving skills. Moving on to the next topic...",
      ];

      const aiMessage: Message = {
        role: "ai",
        content: aiResponses[Math.floor(Math.random() * aiResponses.length)],
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };

      setMessages((prev) => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1500);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-4xl mx-auto">
      {/* Interview Header */}
      <div className="flex items-center justify-between p-4 border-b border-border bg-card">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center bg-primary text-primary-foreground">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h2 className="font-semibold text-foreground">
              AI Interview Session
            </h2>
            <p className="text-xs text-muted-foreground">
              Senior Frontend Engineer • TechCorp
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 px-2 py-1 bg-success/20 text-success text-xs font-medium">
            <span className="h-2 w-2 rounded-full bg-success animate-pulse" />
            In Progress
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="text-muted-foreground hover:text-foreground"
          >
            <Video className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="text-muted-foreground hover:text-foreground"
          >
            <Mic className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="text-muted-foreground hover:text-foreground"
          >
            <Settings className="h-4 w-4" />
          </Button>
          <Button variant="destructive" size="sm" className="gap-2">
            <Phone className="h-4 w-4" />
            End
          </Button>
        </div>
      </div>

      {/* Chat Messages */}
      <ScrollArea className="flex-1 p-6 bg-background">
        <div className="space-y-6 max-w-3xl mx-auto">
          {messages.map((message, index) => (
            <div
              key={index}
              className={cn(
                "flex gap-4",
                message.role === "candidate" && "flex-row-reverse"
              )}
            >
              <div
                className={cn(
                  "flex h-10 w-10 shrink-0 items-center justify-center",
                  message.role === "ai"
                    ? "bg-primary text-primary-foreground"
                    : "bg-secondary border border-border"
                )}
              >
                {message.role === "ai" ? (
                  <Bot className="h-5 w-5" />
                ) : (
                  <User className="h-5 w-5" />
                )}
              </div>
              <div
                className={cn(
                  "flex-1 max-w-[75%]",
                  message.role === "candidate" && "text-right"
                )}
              >
                <div
                  className={cn(
                    "inline-block p-4 text-sm leading-relaxed",
                    message.role === "ai"
                      ? "bg-card border border-border text-foreground"
                      : "bg-primary/10 border border-primary/30 text-foreground"
                  )}
                >
                  {message.content}
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  {message.role === "ai" ? "AI Interviewer" : "You"} •{" "}
                  {message.timestamp}
                </p>
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex gap-4">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center bg-primary text-primary-foreground">
                <Bot className="h-5 w-5" />
              </div>
              <div className="bg-card border border-border p-4">
                <div className="flex gap-1">
                  <span
                    className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce"
                    style={{ animationDelay: "0ms" }}
                  />
                  <span
                    className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce"
                    style={{ animationDelay: "150ms" }}
                  />
                  <span
                    className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce"
                    style={{ animationDelay: "300ms" }}
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="p-4 border-t border-border bg-card">
        <div className="flex gap-3 max-w-3xl mx-auto">
          <Input
            value={input}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setInput(e.target.value)
            }
            placeholder="Type your response..."
            className="flex-1 bg-input border-border focus:border-primary h-12"
            onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim()}
            className="bg-primary text-primary-foreground hover:bg-primary/90 h-12 px-6"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-xs text-muted-foreground text-center mt-3">
          Press Enter to send • Your responses are being analyzed in real-time
        </p>
      </div>
    </div>
  );
}
