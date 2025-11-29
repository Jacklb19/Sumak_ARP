"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { useForm, Controller } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { DashboardHeader } from "@/components/dashboard/header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { FileUpload } from "@/components/shared/file-upload"
import { apiClient } from "@/lib/api"
import { applicationSchema, type ApplicationFormData } from "@/lib/validators"
import type { JobPosting } from "@/types"
import { Loader2, AlertCircle, ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function ApplyPage() {
  const params = useParams()
  const router = useRouter()
  const jobId = params.id as string

  const [job, setJob] = useState<JobPosting | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState("")
  const [cvFile, setCvFile] = useState<File | null>(null)

  const {
    register,
    handleSubmit,
    control,
    setValue,
    watch,
    formState: { errors },
  } = useForm<ApplicationFormData>({
    resolver: zodResolver(applicationSchema),
    defaultValues: {
      seniority_level: "mid",
      expected_salary: 0,
      linkedin_url: "",
      github_url: "",
      consent_ai: false,
      consent_data_storage: false,
    },
  })

  const consentAI = watch("consent_ai")
  const consentData = watch("consent_data_storage")

  useEffect(() => {
    if (jobId) {
      fetchJobDetail()
    }
  }, [jobId])

  const fetchJobDetail = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get(`/job-postings/${jobId}`)
      setJob(response.data)
    } catch (err) {
      console.error("Error fetching job:", err)
      setError("Error al cargar el empleo")
    } finally {
      setLoading(false)
    }
  }

  const onSubmit = async (data: ApplicationFormData) => {
    if (!cvFile) {
      setError("Debes subir tu CV")
      return
    }

    setSubmitting(true)
    setError("")

    try {
      const formData = new FormData()
      formData.append("job_posting_id", jobId)
      formData.append("seniority_level", data.seniority_level)
      formData.append("expected_salary", data.expected_salary.toString())
      formData.append("linkedin_url", data.linkedin_url || "")
      formData.append("github_url", data.github_url || "")
      formData.append("cv_file", cvFile)
      formData.append("consent_ai", "true")
      formData.append("consent_data_storage", "true")

      const response = await apiClient.post("/applications", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })

      if (response.data.success) {
        // Redirect to interview chat
        router.push(`/dashboard/interview/${response.data.application_id}`)
      }
    } catch (err: any) {
      console.error("Error submitting application:", err)
      setError(err.response?.data?.message || "Error al enviar la postulación. Intenta nuevamente.")
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div>
        <DashboardHeader title="Cargando..." />
        <div className="p-6">
          <Skeleton className="h-96 w-full" />
        </div>
      </div>
    )
  }

  if (error && !job) {
    return (
      <div>
        <DashboardHeader title="Error" />
        <div className="p-6">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </div>
      </div>
    )
  }

  return (
    <div>
      <DashboardHeader title="Postularme" description={job ? `${job.title} en ${job.company_name}` : ""} />

      <div className="p-6">
        <div className="max-w-3xl mx-auto space-y-6">
          <Button variant="ghost" asChild>
            <Link href={`/dashboard/jobs/${jobId}`}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Volver al empleo
            </Link>
          </Button>

          <Card>
            <CardHeader>
              <CardTitle>Información de postulación</CardTitle>
              <CardDescription>Completa los siguientes datos para aplicar a este empleo</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                {error && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                <div className="space-y-2">
                  <Label htmlFor="seniority_level">Nivel de experiencia</Label>
                  <Controller
                    name="seniority_level"
                    control={control}
                    render={({ field }) => (
                      <Select value={field.value} onValueChange={field.onChange}>
                        <SelectTrigger id="seniority_level">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="junior">Junior (0-2 años)</SelectItem>
                          <SelectItem value="mid">Mid (3-5 años)</SelectItem>
                          <SelectItem value="senior">Senior (5+ años)</SelectItem>
                        </SelectContent>
                      </Select>
                    )}
                  />
                  {errors.seniority_level && (
                    <p className="text-sm text-destructive">{errors.seniority_level.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="expected_salary">Expectativa salarial (anual USD)</Label>
                  <Input
                    id="expected_salary"
                    type="number"
                    {...register("expected_salary", { valueAsNumber: true })}
                    placeholder="70000"
                  />
                  {errors.expected_salary && (
                    <p className="text-sm text-destructive">{errors.expected_salary.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="linkedin_url">LinkedIn URL (opcional)</Label>
                  <Input
                    id="linkedin_url"
                    {...register("linkedin_url")}
                    placeholder="https://linkedin.com/in/tu-perfil"
                  />
                  {errors.linkedin_url && <p className="text-sm text-destructive">{errors.linkedin_url.message}</p>}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="github_url">GitHub URL (opcional)</Label>
                  <Input id="github_url" {...register("github_url")} placeholder="https://github.com/tu-usuario" />
                  {errors.github_url && <p className="text-sm text-destructive">{errors.github_url.message}</p>}
                </div>

                <div className="space-y-2">
                  <Label>CV (PDF, máximo 5MB) *</Label>
                  <FileUpload onFileSelect={setCvFile} />
                  {!cvFile && submitting && <p className="text-sm text-destructive">El CV es requerido</p>}
                </div>

                <div className="space-y-4 pt-4 border-t">
                  <div className="flex items-start space-x-3">
                    <Controller
                      name="consent_ai"
                      control={control}
                      render={({ field }) => (
                        <Checkbox id="consent_ai" checked={field.value} onCheckedChange={field.onChange} />
                      )}
                    />
                    <div className="space-y-1 leading-none">
                      <Label htmlFor="consent_ai" className="text-sm font-normal cursor-pointer">
                        Acepto que mi información sea procesada por inteligencia artificial para la evaluación de mi
                        candidatura
                      </Label>
                    </div>
                  </div>
                  {errors.consent_ai && <p className="text-sm text-destructive">{errors.consent_ai.message}</p>}

                  <div className="flex items-start space-x-3">
                    <Controller
                      name="consent_data_storage"
                      control={control}
                      render={({ field }) => (
                        <Checkbox id="consent_data_storage" checked={field.value} onCheckedChange={field.onChange} />
                      )}
                    />
                    <div className="space-y-1 leading-none">
                      <Label htmlFor="consent_data_storage" className="text-sm font-normal cursor-pointer">
                        Acepto el almacenamiento de mis datos personales de acuerdo con la política de privacidad
                      </Label>
                    </div>
                  </div>
                  {errors.consent_data_storage && (
                    <p className="text-sm text-destructive">{errors.consent_data_storage.message}</p>
                  )}
                </div>

                <div className="flex gap-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    className="flex-1 bg-transparent"
                    onClick={() => router.back()}
                    disabled={submitting}
                  >
                    Cancelar
                  </Button>
                  <Button
                    type="submit"
                    className="flex-1"
                    disabled={submitting || !cvFile || !consentAI || !consentData}
                  >
                    {submitting ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Enviando...
                      </>
                    ) : (
                      "Enviar postulación"
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
