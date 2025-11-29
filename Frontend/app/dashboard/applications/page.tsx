"use client"

import { useState, useEffect } from "react"
import { DashboardHeader } from "@/components/dashboard/header"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { ScoreBadge } from "@/components/shared/score-badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { apiClient } from "@/lib/api"
import type { Application } from "@/types"
import { AlertCircle, ExternalLink, MessageSquare, FileText } from "lucide-react"
import Link from "next/link"

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    fetchApplications()
  }, [])

  const fetchApplications = async () => {
    setLoading(true)
    setError("")

    try {
      const response = await apiClient.get("/applications/my-applications")
      setApplications(response.data.applications || [])
    } catch (err: any) {
      console.error("Error fetching applications:", err)
      setError("Error al cargar las postulaciones.")
    } finally {
      setLoading(false)
    }
  }

  const statusConfig = {
    pending: { label: "Pendiente", color: "bg-gray-100 text-gray-800" },
    interview_in_progress: { label: "Entrevista en curso", color: "bg-yellow-100 text-yellow-800" },
    evaluation_completed: { label: "Evaluada", color: "bg-blue-100 text-blue-800" },
    hired: { label: "Contratado", color: "bg-green-100 text-green-800" },
    rejected: { label: "Rechazada", color: "bg-red-100 text-red-800" },
  }

  return (
    <div>
      <DashboardHeader title="Mis Postulaciones" description="Revisa el estado de tus aplicaciones" />

      <div className="p-6 space-y-6">
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {loading ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-20 w-full" />
            ))}
          </div>
        ) : applications.length === 0 ? (
          <Card>
            <CardContent className="pt-12 pb-12 text-center">
              <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">Aún no has aplicado a ningún empleo</h3>
              <p className="text-sm text-muted-foreground mb-6">
                Explora las oportunidades disponibles y comienza tu búsqueda
              </p>
              <Button asChild>
                <Link href="/dashboard/jobs">Ver empleos disponibles</Link>
              </Button>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Postulaciones ({applications.length})</CardTitle>
              <CardDescription>Historial completo de tus aplicaciones</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Empleo</TableHead>
                      <TableHead>Empresa</TableHead>
                      <TableHead>Estado</TableHead>
                      <TableHead>Puntuación</TableHead>
                      <TableHead>Fecha</TableHead>
                      <TableHead className="text-right">Acciones</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {applications.map((app) => (
                      <TableRow key={app.id}>
                        <TableCell className="font-medium">{app.job_title}</TableCell>
                        <TableCell>{app.company_name}</TableCell>
                        <TableCell>
                          <Badge className={statusConfig[app.status].color}>{statusConfig[app.status].label}</Badge>
                        </TableCell>
                        <TableCell>
                          {app.global_score !== undefined ? (
                            <ScoreBadge score={app.global_score} size="sm" />
                          ) : (
                            <span className="text-sm text-muted-foreground">-</span>
                          )}
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {new Date(app.created_at).toLocaleDateString("es-ES")}
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex gap-2 justify-end">
                            {app.status === "interview_in_progress" && (
                              <Button size="sm" asChild>
                                <Link href={`/dashboard/interview/${app.id}`}>
                                  <MessageSquare className="h-4 w-4 mr-1" />
                                  Continuar
                                </Link>
                              </Button>
                            )}
                            {(app.status === "evaluation_completed" ||
                              app.status === "hired" ||
                              app.status === "rejected") && (
                              <Button size="sm" variant="outline" asChild>
                                <Link href={`/dashboard/applications/${app.id}`}>
                                  <ExternalLink className="h-4 w-4 mr-1" />
                                  Ver detalle
                                </Link>
                              </Button>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
