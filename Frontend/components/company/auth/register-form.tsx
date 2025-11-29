// <CHANGE> Adding company registration form
"use client"

import { useState } from "react"
import { useRouter } from 'next/navigation'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import { companyApi } from "@/lib/company-api"
import { Loader2 } from 'lucide-react'

const SECTORS = [
  "Tecnología",
  "Finanzas",
  "Salud",
  "Educación",
  "Retail",
  "Manufactura",
  "Servicios",
  "Construcción",
  "Alimentos y Bebidas",
  "Otro",
]

const SIZES = ["1-10", "11-50", "51-200", "201-500", "500+"]

export function RegisterCompanyForm() {
  const router = useRouter()
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    company_name: "",
    email: "",
    password: "",
    confirmPassword: "",
    country: "Colombia",
    city: "",
    sector: "",
    size: "",
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (formData.password !== formData.confirmPassword) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Las contraseñas no coinciden",
      })
      return
    }

    setIsLoading(true)
    try {
      const { confirmPassword, ...registerData } = formData
      await companyApi.registerCompany(registerData)
      toast({
        title: "Registro exitoso",
        description: "Tu cuenta ha sido creada. Ahora puedes iniciar sesión.",
      })
      router.push("/auth/login-company")
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error instanceof Error ? error.message : "Error al registrar empresa",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="w-full max-w-lg">
      <CardHeader>
        <CardTitle>Registrar Empresa</CardTitle>
        <CardDescription>Crea una cuenta para tu empresa y comienza a publicar vacantes</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="company_name">Nombre de la Empresa*</Label>
            <Input
              id="company_name"
              required
              value={formData.company_name}
              onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email Corporativo*</Label>
            <Input
              id="email"
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="password">Contraseña*</Label>
              <Input
                id="password"
                type="password"
                required
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirmar Contraseña*</Label>
              <Input
                id="confirmPassword"
                type="password"
                required
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="country">País</Label>
              <Input
                id="country"
                value={formData.country}
                onChange={(e) => setFormData({ ...formData, country: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="city">Ciudad</Label>
              <Input
                id="city"
                value={formData.city}
                onChange={(e) => setFormData({ ...formData, city: e.target.value })}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="sector">Sector</Label>
              <Select value={formData.sector} onValueChange={(value) => setFormData({ ...formData, sector: value })}>
                <SelectTrigger id="sector">
                  <SelectValue placeholder="Selecciona" />
                </SelectTrigger>
                <SelectContent>
                  {SECTORS.map((sector) => (
                    <SelectItem key={sector} value={sector}>
                      {sector}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="size">Tamaño de Empresa</Label>
              <Select value={formData.size} onValueChange={(value) => setFormData({ ...formData, size: value })}>
                <SelectTrigger id="size">
                  <SelectValue placeholder="Empleados" />
                </SelectTrigger>
                <SelectContent>
                  {SIZES.map((size) => (
                    <SelectItem key={size} value={size}>
                      {size}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Registrando...
              </>
            ) : (
              "Registrar Empresa"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
