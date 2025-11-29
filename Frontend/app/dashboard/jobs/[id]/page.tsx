"use client"

import { useState, useEffect } from "react"
import { useParams } from "next/navigation"
import { DashboardHeader } from "@/components/dashboard/header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { apiClient } from "@/lib/api"
import type { JobPosting } from "@/types"
import { MapPin, Briefcase, Calendar, Building2, AlertCircle } from "lucide-react"
import Image from "next/image"
import Link from "next/link"

export default function JobDetailPage() {
  const params = useParams()
  const jobId = params.id as string

  const [job, setJob] = useState<JobPosting | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    if (jobId) {
      fetchJobDetail()
    }
  }, [jobId])

  const fetchJobDetail = async () => {
    setLoading(true)
    setError("")

    try {
      const response = await apiClient.get(`/api/v1/job-postings/${jobId}`)
      setJob(response.data)
    } catch (err: any) {
      console.error("Error fetching job detail:", err)
      setError("Error al cargar el detalle del empleo.")
    } finally {
      setLoading(false)
    }
  }

  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return "Salario a convenir"
    if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`
    if (min) return `Desde $${min.toLocaleString()}`
    return "Salario a convenir"
  }

  const modalityLabels = {
    remote: "Remoto",
    hybrid: "Híbrido",
    onsite: "Presencial",
  }

  if (loading) {
    return (
      <div>
        <DashboardHeader title="Cargando..." />
        <div className="p-6 space-y-6">
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-96 w-full" />
        </div>
      </div>
    )
  }

  if (error || !job) {
    return (
      <div>
        <DashboardHeader title="Error" />
        <div className="p-6">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error || "No se encontró el empleo"}</AlertDescription>
          </Alert>
        </div>
      </div>
    )
  }

  return (
    <div>
      <DashboardHeader title={job.title} description={job.company_name} />

      <div className="p-6">
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Main Content - 2 columns */}
          <div className="lg:col-span-2 space-y-6">
            {/* Company Info */}
            <Card>
              <CardHeader>
                <div className="flex items-start gap-4">
                  {job.company_logo ? (
                    <Image
                      src={job.company_logo || "/placeholder.svg"}
                      alt={job.company_name}
                      width={64}
                      height={64}
                      className="rounded-lg object-contain"
                    />
                  ) : (
                    <div className="w-16 h-16 rounded-lg bg-muted flex items-center justify-center">
                      <Building2 className="h-8 w-8 text-muted-foreground" />
                    </div>
                  )}
                  <div className="flex-1">
                    <CardTitle className="text-2xl">{job.title}</CardTitle>
                    <CardDescription className="text-base mt-1">{job.company_name}</CardDescription>
                    <div className="flex flex-wrap gap-2 mt-3">
                      <Badge variant="secondary">{modalityLabels[job.modality]}</Badge>
                      <Badge variant="outline">
                        <MapPin className="h-3 w-3 mr-1" />
                        {job.location}
                      </Badge>
                      <Badge variant="outline">
                        <Briefcase className="h-3 w-3 mr-1" />
                        {job.contract_type}
                      </Badge>
                      <Badge variant="outline">
                        <Calendar className="h-3 w-3 mr-1" />
                        {new Date(job.published_at).toLocaleDateString("es-ES")}
                      </Badge>
                    </div>
                  </div>
                </div>
              </CardHeader>
            </Card>

            {/* Description */}
            <Card>
              <CardHeader>
                <CardTitle>Descripción del puesto</CardTitle>
              </CardHeader>
              <CardContent className="prose prose-sm max-w-none">
                <p className="whitespace-pre-wrap text-sm leading-relaxed text-foreground">{job.description}</p>
              </CardContent>
            </Card>

            {/* Skills Required */}
            {job.required_skills && (
              <Card>
                <CardHeader>
                  <CardTitle>Habilidades requeridas</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {job.required_skills.languages && job.required_skills.languages.length > 0 && (
                    <div>
                      <p className="text-sm font-medium mb-2">Lenguajes y tecnologías:</p>
                      <div className="flex flex-wrap gap-2">
                        {job.required_skills.languages.map((skill) => (
                          <Badge key={skill} variant="secondary">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  {job.required_skills.years_experience && (
                    <div>
                      <p className="text-sm font-medium mb-2">Experiencia requerida:</p>
                      <Badge variant="outline">{job.required_skills.years_experience} años</Badge>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar - 1 column */}
          <div className="space-y-6">
            {/* Apply Card */}
            <Card className="sticky top-6">
              <CardHeader>
                <CardTitle>Postularme a este empleo</CardTitle>
                <CardDescription>¿Listo para aplicar?</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Salario:</span>
                    <span className="font-medium text-primary">{formatSalary(job.salary_min, job.salary_max)}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Modalidad:</span>
                    <span className="font-medium">{modalityLabels[job.modality]}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Ubicación:</span>
                    <span className="font-medium">{job.location}</span>
                  </div>
                </div>

                <Button className="w-full" size="lg" asChild>
                  <Link href={`/dashboard/jobs/${job.id}/apply`}>Postularme ahora</Link>
                </Button>

                <p className="text-xs text-muted-foreground text-center">
                  Tu CV será procesado por nuestro sistema de IA
                </p>
              </CardContent>
            </Card>

            {/* Job Info */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Información adicional</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-start gap-3">
                  <Building2 className="h-4 w-4 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Área</p>
                    <p className="text-sm text-muted-foreground">{job.area}</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Briefcase className="h-4 w-4 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Tipo de contrato</p>
                    <p className="text-sm text-muted-foreground">{job.contract_type}</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Calendar className="h-4 w-4 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Publicado</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(job.published_at).toLocaleDateString("es-ES", {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
