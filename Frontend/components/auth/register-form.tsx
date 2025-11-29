"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { useRouter } from "next/navigation"
import { registerSchema, type RegisterFormData } from "@/lib/validators"
import { apiClient } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2 } from "lucide-react"
import Link from "next/link"

export function RegisterForm() {
  const router = useRouter()
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      country: "Colombia",
    },
  })

  const onSubmit = async (data: RegisterFormData) => {
    setLoading(true)
    setError("")

    try {
      const response = await apiClient.post("/api/v1/candidates/register-candidate", {
        full_name: data.full_name,
        email: data.email,
        phone_number: data.phone_number,
        password: data.password,
        country: data.country,
        city: data.city,
      })

      if (response.data.success) {
        localStorage.setItem("auth_token", response.data.token)
        localStorage.setItem("candidate_id", response.data.candidate_id)
        localStorage.setItem("full_name", data.full_name)
        router.push("/dashboard")
      }
    } catch (err: any) {
      setError(err.response?.data?.message || "Error al registrarse. Intenta nuevamente.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Crear cuenta</CardTitle>
        <CardDescription>Regístrate para comenzar a buscar empleos</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <Label htmlFor="full_name">Nombre completo</Label>
            <Input id="full_name" {...register("full_name")} placeholder="Juan García" />
            {errors.full_name && <p className="text-sm text-destructive">{errors.full_name.message}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" {...register("email")} placeholder="juan@example.com" />
            {errors.email && <p className="text-sm text-destructive">{errors.email.message}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="phone_number">Teléfono</Label>
            <Input id="phone_number" {...register("phone_number")} placeholder="+573001234567" />
            {errors.phone_number && <p className="text-sm text-destructive">{errors.phone_number.message}</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="country">País</Label>
              <Select defaultValue="Colombia" onValueChange={(value) => setValue("country", value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Colombia">Colombia</SelectItem>
                  <SelectItem value="México">México</SelectItem>
                  <SelectItem value="Argentina">Argentina</SelectItem>
                  <SelectItem value="Chile">Chile</SelectItem>
                  <SelectItem value="Perú">Perú</SelectItem>
                </SelectContent>
              </Select>
              {errors.country && <p className="text-sm text-destructive">{errors.country.message}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="city">Ciudad</Label>
              <Input id="city" {...register("city")} placeholder="Bogotá" />
              {errors.city && <p className="text-sm text-destructive">{errors.city.message}</p>}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Contraseña</Label>
            <Input id="password" type="password" {...register("password")} placeholder="••••••••" />
            {errors.password && <p className="text-sm text-destructive">{errors.password.message}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirm_password">Confirmar contraseña</Label>
            <Input id="confirm_password" type="password" {...register("confirm_password")} placeholder="••••••••" />
            {errors.confirm_password && <p className="text-sm text-destructive">{errors.confirm_password.message}</p>}
          </div>

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Registrando...
              </>
            ) : (
              "Crear cuenta"
            )}
          </Button>

          <p className="text-center text-sm text-muted-foreground">
            ¿Ya tienes cuenta?{" "}
            <Link href="/auth/login" className="text-primary hover:underline">
              Inicia sesión
            </Link>
          </p>
        </form>
      </CardContent>
    </Card>
  )
}
