import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface ScoreBadgeProps {
  score: number
  maxScore?: number
  size?: "sm" | "md" | "lg"
}

export function ScoreBadge({ score, maxScore = 100, size = "md" }: ScoreBadgeProps) {
  const percentage = (score / maxScore) * 100

  const getColor = () => {
    if (percentage >= 80) return "bg-green-100 text-green-800 border-green-200"
    if (percentage >= 60) return "bg-blue-100 text-blue-800 border-blue-200"
    if (percentage >= 40) return "bg-yellow-100 text-yellow-800 border-yellow-200"
    return "bg-red-100 text-red-800 border-red-200"
  }

  const sizeClasses = {
    sm: "text-xs px-2 py-0.5",
    md: "text-sm px-3 py-1",
    lg: "text-base px-4 py-1.5",
  }

  return (
    <Badge variant="outline" className={cn(getColor(), sizeClasses[size], "font-semibold")}>
      {score.toFixed(1)}/{maxScore}
    </Badge>
  )
}
