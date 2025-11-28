"use client"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { KPICards } from "./kpi-cards"
import { CandidatesTable } from "./candidates-table"
import { Plus, Search, Filter } from "lucide-react"
import type { Candidate } from "@/lib/mock-data"

interface RecruiterDashboardProps {
  candidates: Candidate[]
  onViewCandidate: (candidate: Candidate) => void
}

export function RecruiterDashboard({ candidates, onViewCandidate }: RecruiterDashboardProps) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Recruitment Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-1">Monitor candidates and manage your hiring pipeline</p>
        </div>
        <Button className="bg-primary text-primary-foreground hover:bg-primary/90 gap-2 font-medium">
          <Plus className="h-4 w-4" />
          Create New Job
        </Button>
      </div>

      {/* KPI Cards */}
      <KPICards candidates={candidates} />

      {/* Candidates Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <h2 className="text-lg font-semibold text-foreground">All Candidates</h2>
          <div className="flex items-center gap-2">
            <div className="relative flex-1 sm:flex-initial">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search candidates..."
                className="pl-9 w-full sm:w-[280px] bg-input border-border focus:border-primary"
              />
            </div>
            <Button variant="outline" size="icon" className="border-border bg-transparent">
              <Filter className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <CandidatesTable candidates={candidates} onViewCandidate={onViewCandidate} />
      </div>
    </div>
  )
}
