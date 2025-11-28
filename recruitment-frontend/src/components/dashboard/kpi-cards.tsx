"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Users, Trophy, Calendar, TrendingUp } from "lucide-react"
import type { Candidate } from "@/lib/mock-data"

interface KPICardsProps {
  candidates: Candidate[]
}

export function KPICards({ candidates }: KPICardsProps) {
  const totalCandidates = candidates.length
  const highPerformers = candidates.filter((c) => c.overallScore > 80).length
  const pendingInterviews = candidates.filter((c) => c.status === "Pending" || c.status === "Interviewing").length
  const hired = candidates.filter((c) => c.status === "Hired").length

  const kpis = [
    {
      label: "Total Candidates",
      value: totalCandidates,
      icon: Users,
      change: "+12%",
      changeType: "positive" as const,
    },
    {
      label: "High Performers",
      value: highPerformers,
      icon: Trophy,
      sublabel: "> 80 score",
      change: "+8%",
      changeType: "positive" as const,
    },
    {
      label: "Pending Interviews",
      value: pendingInterviews,
      icon: Calendar,
      change: "-3",
      changeType: "neutral" as const,
    },
    {
      label: "Hired This Month",
      value: hired,
      icon: TrendingUp,
      change: "+2",
      changeType: "positive" as const,
    },
  ]

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {kpis.map((kpi) => (
        <Card key={kpi.label} className="bg-card border-border hover:border-primary/50 transition-colors">
          <CardContent className="p-5">
            <div className="flex items-start justify-between">
              <div className="space-y-2">
                <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">{kpi.label}</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold font-mono text-foreground">{kpi.value}</span>
                  {kpi.sublabel && <span className="text-xs text-muted-foreground">{kpi.sublabel}</span>}
                </div>
                <div
                  className={`text-xs font-medium ${
                    kpi.changeType === "positive" ? "text-green-400" : "text-muted-foreground"
                  }`}
                >
                  {kpi.change} from last month
                </div>
              </div>
              <div className="flex h-10 w-10 items-center justify-center bg-secondary border border-border">
                <kpi.icon className="h-5 w-5 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
