"use client"

import { useEffect, useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Clock, Building2 } from "lucide-react"
import Image from "next/image"

interface InterviewHeaderProps {
  jobTitle: string
  companyName: string
  companyLogo?: string
  startTime: Date
  status: "connecting" | "connected" | "disconnected" | "completed"
}

export function InterviewHeader({ jobTitle, companyName, companyLogo, startTime, status }: InterviewHeaderProps) {
  const [elapsed, setElapsed] = useState("00:00")

  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date()
      const diff = Math.floor((now.getTime() - startTime.getTime()) / 1000)
      const minutes = Math.floor(diff / 60)
      const seconds = diff % 60
      setElapsed(`${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`)
    }, 1000)

    return () => clearInterval(interval)
  }, [startTime])

  const statusConfig = {
    connecting: { label: "Conectando...", color: "bg-yellow-100 text-yellow-800" },
    connected: { label: "En progreso", color: "bg-green-100 text-green-800" },
    disconnected: { label: "Desconectado", color: "bg-red-100 text-red-800" },
    completed: { label: "Completada", color: "bg-blue-100 text-blue-800" },
  }

  const currentStatus = statusConfig[status]

  return (
    <div className="border-b bg-background p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          {companyLogo ? (
            <Image
              src={companyLogo || "/placeholder.svg"}
              alt={companyName}
              width={40}
              height={40}
              className="rounded-lg object-contain"
            />
          ) : (
            <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
              <Building2 className="h-5 w-5 text-muted-foreground" />
            </div>
          )}

          <div>
            <h2 className="font-semibold text-lg leading-tight">Entrevista para: {jobTitle}</h2>
            <p className="text-sm text-muted-foreground">{companyName}</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            <span className="font-mono">{elapsed}</span>
          </div>

          <Badge className={currentStatus.color}>{currentStatus.label}</Badge>
        </div>
      </div>
    </div>
  )
}
