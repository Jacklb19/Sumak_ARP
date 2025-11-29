import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Bot, Zap, Eye, Briefcase } from "lucide-react"
import Link from "next/link"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-teal-50">
      {/* Navbar */}
      <nav className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Briefcase className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">TalentHub</span>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="ghost" asChild>
              <Link href="/auth/login">Iniciar sesión</Link>
            </Button>
            <Button asChild>
              <Link href="/auth/register">Registrarse</Link>
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-4xl mx-auto space-y-8">
          <h1 className="text-5xl md:text-6xl font-bold text-balance leading-tight">
            Encuentra tu próximo empleo <span className="text-primary">con IA</span>
          </h1>
          <p className="text-xl text-muted-foreground text-balance max-w-2xl mx-auto">
            Entrevistas inteligentes, matching preciso y feedback instantáneo. El futuro del reclutamiento está aquí.
          </p>
          <div className="flex gap-4 justify-center">
            <Button size="lg" asChild>
              <Link href="/dashboard/jobs">Ver empleos disponibles</Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/auth/register">Crear cuenta gratis</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <Card className="border-2 hover:border-primary transition-colors">
            <CardContent className="pt-6 space-y-4">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <Bot className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold">Entrevistas con IA</h3>
              <p className="text-muted-foreground">
                Agentes inteligentes evalúan tus habilidades técnicas y blandas en tiempo real
              </p>
            </CardContent>
          </Card>

          <Card className="border-2 hover:border-primary transition-colors">
            <CardContent className="pt-6 space-y-4">
              <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center">
                <Zap className="h-6 w-6 text-accent" />
              </div>
              <h3 className="text-xl font-semibold">Feedback instantáneo</h3>
              <p className="text-muted-foreground">
                Recibe puntuaciones y comentarios después de cada respuesta en la entrevista
              </p>
            </CardContent>
          </Card>

          <Card className="border-2 hover:border-primary transition-colors">
            <CardContent className="pt-6 space-y-4">
              <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
                <Eye className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold">Proceso transparente</h3>
              <p className="text-muted-foreground">Conoce tu progreso en cada etapa y entiende cómo te evaluaron</p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-16">
        <Card className="max-w-3xl mx-auto bg-gradient-to-br from-primary to-blue-600 border-0">
          <CardContent className="pt-12 pb-12 text-center space-y-6">
            <h2 className="text-3xl font-bold text-white text-balance">Comienza tu búsqueda hoy</h2>
            <p className="text-lg text-white/90 text-balance max-w-xl mx-auto">
              Únete a miles de candidatos que ya están encontrando mejores oportunidades
            </p>
            <Button size="lg" variant="secondary" asChild>
              <Link href="/auth/register">Registrarse ahora</Link>
            </Button>
          </CardContent>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t bg-white mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <Briefcase className="h-5 w-5 text-primary" />
              <span className="font-semibold">TalentHub</span>
            </div>
            <p className="text-sm text-muted-foreground">© 2025 TalentHub. Todos los derechos reservados.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
