"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Briefcase, Home, Search, FileText, User, LogOut } from "lucide-react"
import { useAuth } from "@/hooks/use-auth"

const navItems = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: Home,
  },
  {
    title: "Empleos Disponibles",
    href: "/dashboard/jobs",
    icon: Search,
  },
  {
    title: "Mis Postulaciones",
    href: "/dashboard/applications",
    icon: FileText,
  },
  {
    title: "Mi Perfil",
    href: "/dashboard/profile",
    icon: User,
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const { logout } = useAuth()

  return (
    <div className="flex h-screen w-64 flex-col border-r bg-sidebar">
      {/* Logo */}
      <div className="border-b px-6 py-4">
        <Link href="/dashboard" className="flex items-center gap-2">
          <Briefcase className="h-6 w-6 text-sidebar-primary" />
          <span className="text-lg font-bold">TalentHub</span>
        </Link>
      </div>

      {/* Navigation */}
      <ScrollArea className="flex-1 px-3 py-4">
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`)

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                )}
              >
                <Icon className="h-5 w-5" />
                {item.title}
              </Link>
            )
          })}
        </nav>
      </ScrollArea>

      {/* Logout Button */}
      <div className="border-t p-4">
        <Button variant="ghost" className="w-full justify-start gap-3" onClick={logout}>
          <LogOut className="h-5 w-5" />
          Cerrar sesión
        </Button>
      </div>
    </div>
  )
}
