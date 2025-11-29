"use client"

import { useState, useEffect } from "react"
import { useParams } from "next/navigation"
import { DashboardHeader } from "@/components/dashboard/header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScoreBadge } from "@/components/shared/score-badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { apiClient } from "@/lib/api"
import type { Application } from "@/types"
import { AlertCircle, ArrowLeft, CheckCircle2, TrendingUp, MessageSquare, Lightbulb } from "lucide-react"
import Link from "next/link"

export default function ApplicationDetailPage() {
  const params = useParams()
  const applicationId = params.id as string

  const [application, setApplication] = useState<Application | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    if (applicationId) {
      fetchApplicationDetail()
    }
  }, [applicationId])

  const fetchApplicationDetail = async () => {
    setLoading(true)
    setError("")

    try {
      const response = await apiClient.get(`/api/v1/applications/${applicationId}`)
      setApplication(response.data)
    } catch (err: any) {
      console.error("Error fetching application detail:", err)
      setError("Error al cargar el detalle de la postulación.")
    } finally {
      setLoading(false)
    }
  }

  const statusConfig = {
    pending: { label: "Pendiente", color: "bg-gray-100 text-gray-800" },
    interview_in_progress: { label: "Entrevista en curso", color: "bg-yellow-100 text-yellow-800" },
    evaluation_completed: { label: "Evaluación completada", color: "bg-blue-100 text-blue-800" },
    hired: { label: "Contratado", color: "bg-green-100 text-green-800" },
    rejected: { label: "Rechazada", color: "bg-red-100 text-red-800" },
  }

  if (loading) {
    return (
      <div>
        <DashboardHeader title="Cargando..." />
        <div className="p-6 space-y-6">
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    )
  }

  if (error || !application) {
    return (
      <div>
        <DashboardHeader title="Error" />
        <div className="p-6">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error || "No se encontró la postulación"}</AlertDescription>
          </Alert>
        </div>
      </div>
    )
  }

  return (
    <div>
      <DashboardHeader
        title="Detalle de Postulación"
        description={`${application.job_title} en ${application.company_name}`}
      />

      <div className="p-6 space-y-6">
        <Button variant="ghost" asChild>
          <Link href="/dashboard/applications">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Volver a postulaciones
          </Link>
        </Button>

        {/* Status Card */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>{application.job_title}</CardTitle>
                <CardDescription>{application.company_name}</CardDescription>
              </div>
              <Badge className={statusConfig[application.status].color}>{statusConfig[application.status].label}</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Fecha de aplicación</p>
                <p className="font-medium">{new Date(application.created_at).toLocaleDateString("es-ES")}</p>
              </div>
              {application.interview_started_at && (
                <div>
                  <p className="text-sm text-muted-foreground">Entrevista iniciada</p>
                  <p className="font-medium">
                    {new Date(application.interview_started_at).toLocaleDateString("es-ES")}
                  </p>
                </div>
              )}
              {application.interview_completed_at && (
                <div>
                  <p className="text-sm text-muted-foreground">Entrevista completada</p>
                  <p className="font-medium">
                    {new Date(application.interview_completed_at).toLocaleDateString("es-ES")}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Scores */}
        {application.global_score !== undefined && (
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-primary" />
                  Puntuación Global
                </CardTitle>
                <CardDescription>Tu evaluación general</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-6">
                  <div className="text-5xl font-bold text-primary mb-2">{application.global_score.toFixed(1)}</div>
                  <p className="text-muted-foreground">de 100 puntos</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5 text-primary" />
                  Desglose de Puntuaciones
                </CardTitle>
                <CardDescription>Evaluación por categorías</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {application.cv_score !== undefined && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">CV</span>
                    <ScoreBadge score={application.cv_score} size="sm" />
                  </div>
                )}
                {application.technical_score !== undefined && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Habilidades Técnicas</span>
                    <ScoreBadge score={application.technical_score} size="sm" />
                  </div>
                )}
                {application.soft_skills_score !== undefined && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Habilidades Blandas</span>
                    <ScoreBadge score={application.soft_skills_score} size="sm" />
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* Explanation */}
        {application.global_score_explanation && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-primary" />
                Evaluación Detallada
              </CardTitle>
              <CardDescription>Feedback del sistema de IA</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed">{application.global_score_explanation}</p>
            </CardContent>
          </Card>
        )}

        {/* Next Steps */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-primary" />
              Próximos Pasos
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {application.status === "evaluation_completed" && (
              <>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-primary mt-2" />
                  <div>
                    <p className="font-medium text-sm">El reclutador revisará tu perfil</p>
                    <p className="text-xs text-muted-foreground">Recibirás una notificación por email si hay interés</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-muted mt-2" />
                  <div>
                    <p className="font-medium text-sm">Mantén tu perfil actualizado</p>
                    <p className="text-xs text-muted-foreground">
                      Mejora tus posibilidades manteniendo tu información al día
                    </p>
                  </div>
                </div>
              </>
            )}
            {application.status === "hired" && (
              <div className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium text-sm">¡Felicitaciones!</p>
                  <p className="text-xs text-muted-foreground">
                    El reclutador se pondrá en contacto contigo pronto para coordinar los siguientes pasos
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
