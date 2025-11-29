"use client"

import { useState, useEffect } from "react"
import { useForm } from "react-hook-form"
import { DashboardHeader } from "@/components/dashboard/header"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { apiClient } from "@/lib/api"
import { useAuth } from "@/hooks/use-auth"
import type { Candidate } from "@/types"
import { Loader2, CheckCircle2, AlertCircle } from "lucide-react"

export default function ProfilePage() {
  const { user, checkAuth } = useAuth()
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState("")
  const [error, setError] = useState("")

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<Candidate>()

  useEffect(() => {
    if (user) {
      setValue("full_name", user.full_name)
      setValue("email", user.email)
      setValue("phone_number", user.phone_number)
      setValue("country", user.country)
      setValue("city", user.city)
      setValue("seniority_level", user.seniority_level || "mid")
      setValue("linkedin_url", user.linkedin_url || "")
      setValue("github_url", user.github_url || "")
      setValue("portfolio_url", user.portfolio_url || "")
    }
  }, [user, setValue])

  const onSubmit = async (data: Candidate) => {
    setLoading(true)
    setSuccess("")
    setError("")

    try {
      await apiClient.put("/candidates/me", {
        full_name: data.full_name,
        phone_number: data.phone_number,
        country: data.country,
        city: data.city,
        seniority_level: data.seniority_level,
        linkedin_url: data.linkedin_url || null,
        github_url: data.github_url || null,
        portfolio_url: data.portfolio_url || null,
      })

      setSuccess("Perfil actualizado correctamente")
      await checkAuth()
    } catch (err: any) {
      console.error("Error updating profile:", err)
      setError(err.response?.data?.message || "Error al actualizar el perfil")
    } finally {
      setLoading(false)
    }
  }

  const initials =
    user?.full_name
      ?.split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2) || "U"

  if (!user) {
    return (
      <div>
        <DashboardHeader title="Mi Perfil" />
        <div className="p-6">
          <Skeleton className="h-96 w-full" />
        </div>
      </div>
    )
  }

  return (
    <div>
      <DashboardHeader title="Mi Perfil" description="Actualiza tu información personal" />

      <div className="p-6">
        <div className="max-w-3xl mx-auto space-y-6">
          {success && (
            <Alert className="bg-green-50 text-green-900 border-green-200">
              <CheckCircle2 className="h-4 w-4" />
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Card>
            <CardHeader>
              <div className="flex items-center gap-4">
                <Avatar className="h-20 w-20">
                  <AvatarFallback className="bg-primary text-primary-foreground text-2xl">{initials}</AvatarFallback>
                </Avatar>
                <div>
                  <CardTitle>{user.full_name}</CardTitle>
                  <CardDescription>{user.email}</CardDescription>
                </div>
              </div>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Información Personal</CardTitle>
              <CardDescription>Actualiza tus datos de contacto y ubicación</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="full_name">Nombre completo</Label>
                  <Input id="full_name" {...register("full_name", { required: "El nombre es requerido" })} />
                  {errors.full_name && <p className="text-sm text-destructive">{errors.full_name.message}</p>}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" {...register("email")} disabled className="bg-muted" />
                  <p className="text-xs text-muted-foreground">El email no puede ser modificado</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="phone_number">Teléfono</Label>
                    <Input id="phone_number" {...register("phone_number")} />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="seniority_level">Nivel de experiencia</Label>
                    <Select
                      defaultValue={user.seniority_level || "mid"}
                      onValueChange={(value) => setValue("seniority_level", value as any)}
                    >
                      <SelectTrigger id="seniority_level">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="junior">Junior (0-2 años)</SelectItem>
                        <SelectItem value="mid">Mid (3-5 años)</SelectItem>
                        <SelectItem value="senior">Senior (5+ años)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="country">País</Label>
                    <Input id="country" {...register("country")} />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="city">Ciudad</Label>
                    <Input id="city" {...register("city")} />
                  </div>
                </div>

                <div className="pt-4 border-t">
                  <h3 className="font-medium mb-4">Redes Profesionales</h3>

                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="linkedin_url">LinkedIn URL</Label>
                      <Input
                        id="linkedin_url"
                        {...register("linkedin_url")}
                        placeholder="https://linkedin.com/in/tu-perfil"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="github_url">GitHub URL</Label>
                      <Input id="github_url" {...register("github_url")} placeholder="https://github.com/tu-usuario" />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="portfolio_url">Portfolio URL</Label>
                      <Input id="portfolio_url" {...register("portfolio_url")} placeholder="https://tu-portfolio.com" />
                    </div>
                  </div>
                </div>

                <div className="flex gap-3 pt-4">
                  <Button type="submit" disabled={loading} className="flex-1">
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Guardando...
                      </>
                    ) : (
                      "Guardar cambios"
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
