"use client"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  LayoutDashboard,
  Users,
  MessageSquare,
  Settings,
  ChevronLeft,
  ChevronRight,
  Bot,
  Briefcase,
} from "lucide-react"

interface SidebarProps {
  currentView: "dashboard" | "candidate" | "interview"
  onViewChange: (view: "dashboard" | "candidate" | "interview") => void
  collapsed: boolean
  onCollapsedChange: (collapsed: boolean) => void
}

export function Sidebar({ currentView, onViewChange, collapsed, onCollapsedChange }: SidebarProps) {
  const navItems = [
    { id: "dashboard" as const, label: "Dashboard", icon: LayoutDashboard },
    { id: "candidate" as const, label: "Candidates", icon: Users },
    { id: "interview" as const, label: "Interview", icon: MessageSquare },
  ]

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 h-screen bg-sidebar border-r border-sidebar-border transition-all duration-300",
        collapsed ? "w-16" : "w-64",
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center justify-between border-b border-sidebar-border px-4">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center bg-primary">
              <Bot className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="font-mono text-sm font-bold tracking-tight text-sidebar-foreground">
              RECRUIT<span className="text-primary">AI</span>
            </span>
          </div>
        )}
        {collapsed && (
          <div className="flex h-8 w-8 items-center justify-center bg-primary mx-auto">
            <Bot className="h-5 w-5 text-primary-foreground" />
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-1 p-3">
        {navItems.map((item) => (
          <Button
            key={item.id}
            variant={currentView === item.id ? "secondary" : "ghost"}
            className={cn(
              "justify-start gap-3 h-11",
              currentView === item.id &&
                "bg-sidebar-accent text-sidebar-accent-foreground border-l-2 border-primary rounded-none",
              collapsed && "justify-center px-2",
            )}
            onClick={() => onViewChange(item.id)}
          >
            <item.icon className="h-5 w-5 shrink-0" />
            {!collapsed && <span className="font-medium">{item.label}</span>}
          </Button>
        ))}
      </nav>

      {/* Divider */}
      <div className="mx-3 my-2 border-t border-sidebar-border" />

      {/* Secondary Nav */}
      <nav className="flex flex-col gap-1 p-3">
        <Button
          variant="ghost"
          className={cn(
            "justify-start gap-3 h-11 text-muted-foreground hover:text-sidebar-foreground",
            collapsed && "justify-center px-2",
          )}
        >
          <Briefcase className="h-5 w-5 shrink-0" />
          {!collapsed && <span className="font-medium">Jobs</span>}
        </Button>
        <Button
          variant="ghost"
          className={cn(
            "justify-start gap-3 h-11 text-muted-foreground hover:text-sidebar-foreground",
            collapsed && "justify-center px-2",
          )}
        >
          <Settings className="h-5 w-5 shrink-0" />
          {!collapsed && <span className="font-medium">Settings</span>}
        </Button>
      </nav>

      {/* Collapse Toggle */}
      <div className="absolute bottom-4 left-0 right-0 px-3">
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-center text-muted-foreground hover:text-sidebar-foreground"
          onClick={() => onCollapsedChange(!collapsed)}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <>
              <ChevronLeft className="h-4 w-4 mr-2" />
              <span className="text-xs">Collapse</span>
            </>
          )}
        </Button>
      </div>
    </aside>
  )
}
