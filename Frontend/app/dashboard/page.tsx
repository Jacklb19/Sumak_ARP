"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { DashboardHeader } from "@/components/dashboard/header"
import { useAuth } from "@/hooks/use-auth"
import { Briefcase, FileText, Clock, TrendingUp } from "lucide-react"
import Link from "next/link"

export default function DashboardPage() {
  const { user } = useAuth()

  return (
    <div>
      <DashboardHeader
        title="Dashboard"
        description={`Bienvenido de vuelta, ${user?.full_name?.split(" ")[0] || "Usuario"}`}
      />

      <div className="p-6 space-y-6">
        {/* Welcome Card */}
        <Card className="bg-gradient-to-br from-primary to-blue-600 border-0 text-white">
          <CardHeader>
            <CardTitle className="text-white">Comienza tu búsqueda</CardTitle>
            <CardDescription className="text-white/90">
              Explora oportunidades y aplica a empleos que coincidan con tu perfil
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="secondary" asChild>
              <Link href="/dashboard/jobs">Ver empleos disponibles</Link>
            </Button>
          </CardContent>
        </Card>

        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Empleos Disponibles</CardTitle>
              <Briefcase className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">150+</div>
              <p className="text-xs text-muted-foreground">Nuevas oportunidades</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Mis Postulaciones</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">0</div>
              <p className="text-xs text-muted-foreground">Aplicaciones enviadas</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">En Proceso</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">0</div>
              <p className="text-xs text-muted-foreground">Entrevistas activas</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Perfil Completado</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">85%</div>
              <p className="text-xs text-muted-foreground">Completa tu perfil</p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Acciones Rápidas</CardTitle>
              <CardDescription>Gestiona tu búsqueda de empleo</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button className="w-full justify-start bg-transparent" variant="outline" asChild>
                <Link href="/dashboard/jobs">
                  <Briefcase className="mr-2 h-4 w-4" />
                  Explorar empleos
                </Link>
              </Button>
              <Button className="w-full justify-start bg-transparent" variant="outline" asChild>
                <Link href="/dashboard/applications">
                  <FileText className="mr-2 h-4 w-4" />
                  Ver mis postulaciones
                </Link>
              </Button>
              <Button className="w-full justify-start bg-transparent" variant="outline" asChild>
                <Link href="/dashboard/profile">
                  <TrendingUp className="mr-2 h-4 w-4" />
                  Completar perfil
                </Link>
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Próximos pasos</CardTitle>
              <CardDescription>Recomendaciones para ti</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-primary mt-2" />
                <div>
                  <p className="font-medium text-sm">Completa tu perfil</p>
                  <p className="text-xs text-muted-foreground">Agrega tu experiencia y habilidades</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-primary mt-2" />
                <div>
                  <p className="font-medium text-sm">Sube tu CV actualizado</p>
                  <p className="text-xs text-muted-foreground">Asegúrate de tener tu mejor versión</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-muted mt-2" />
                <div>
                  <p className="font-medium text-sm">Aplica a tu primer empleo</p>
                  <p className="text-xs text-muted-foreground">Encuentra la oportunidad perfecta</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
