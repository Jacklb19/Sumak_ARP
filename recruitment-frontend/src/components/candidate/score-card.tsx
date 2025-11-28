"use client"

import type React from "react"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface ScoreCardProps {
  title: string
  score: number
  icon: React.ReactNode
}

export function ScoreCard({ title, score, icon }: ScoreCardProps) {
  const circumference = 2 * Math.PI * 40
  const strokeDashoffset = circumference - (score / 100) * circumference

  const getScoreColor = (score: number) => {
    if (score >= 80) return "stroke-primary"
    if (score >= 60) return "stroke-warning"
    return "stroke-muted-foreground"
  }

  const getTextColor = (score: number) => {
    if (score >= 80) return "text-primary"
    if (score >= 60) return "text-warning"
    return "text-muted-foreground"
  }

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
          {icon}
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex items-center justify-center pt-2 pb-4">
        <div className="relative h-28 w-28">
          <svg className="h-28 w-28 -rotate-90 transform">
            {/* Background circle */}
            <circle
              cx="56"
              cy="56"
              r="40"
              fill="none"
              stroke="currentColor"
              strokeWidth="8"
              className="text-secondary"
            />
            {/* Progress circle */}
            <circle
              cx="56"
              cy="56"
              r="40"
              fill="none"
              strokeWidth="8"
              strokeLinecap="square"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              className={cn("transition-all duration-500", getScoreColor(score))}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={cn("text-3xl font-bold font-mono", getTextColor(score))}>{score}</span>
            <span className="text-xs text-muted-foreground">/100</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
