"use client"

import { useState, useEffect } from "react"
import { DashboardHeader } from "@/components/dashboard/header"
import { JobCard } from "@/components/jobs/job-card"
import { JobFilters } from "@/components/jobs/job-filters"
import { apiClient } from "@/lib/api"
import type { JobPosting } from "@/types"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle } from "lucide-react"

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobPosting[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  const [searchTerm, setSearchTerm] = useState("")
  const [area, setArea] = useState("all")
  const [modality, setModality] = useState("all")
  const [location, setLocation] = useState("")

  useEffect(() => {
    fetchJobs()
  }, [])

  const fetchJobs = async () => {
    setLoading(true)
    setError("")

    try {
      const response = await apiClient.get("/job-postings", {
        params: {
          status: "published",
          limit: 50,
          offset: 0,
        },
      })
      setJobs(response.data.postings || [])
    } catch (err: any) {
      console.error("Error fetching jobs:", err)
      setError("Error al cargar los empleos. Por favor intenta nuevamente.")
    } finally {
      setLoading(false)
    }
  }

  const filteredJobs = jobs.filter((job) => {
    const matchesSearch =
      job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.company_name.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesArea = area === "all" || job.area === area
    const matchesModality = modality === "all" || job.modality === modality
    const matchesLocation = !location || job.location.toLowerCase().includes(location.toLowerCase())

    return matchesSearch && matchesArea && matchesModality && matchesLocation
  })

  return (
    <div>
      <DashboardHeader title="Empleos Disponibles" description="Encuentra tu próxima oportunidad laboral" />

      <div className="p-6 space-y-6">
        <JobFilters
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          area={area}
          onAreaChange={setArea}
          modality={modality}
          onModalityChange={setModality}
          location={location}
          onLocationChange={setLocation}
        />

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {loading ? (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="space-y-3">
                <Skeleton className="h-48 w-full" />
              </div>
            ))}
          </div>
        ) : filteredJobs.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No se encontraron empleos que coincidan con tu búsqueda</p>
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                {filteredJobs.length} empleo{filteredJobs.length !== 1 ? "s" : ""} encontrado
                {filteredJobs.length !== 1 ? "s" : ""}
              </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {filteredJobs.map((job) => (
                <JobCard key={job.id} job={job} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
