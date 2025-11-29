"use client"

import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search } from "lucide-react"

interface JobFiltersProps {
  searchTerm: string
  onSearchChange: (value: string) => void
  area: string
  onAreaChange: (value: string) => void
  modality: string
  onModalityChange: (value: string) => void
  location: string
  onLocationChange: (value: string) => void
}

export function JobFilters({
  searchTerm,
  onSearchChange,
  area,
  onAreaChange,
  modality,
  onModalityChange,
  location,
  onLocationChange,
}: JobFiltersProps) {
  return (
    <div className="space-y-4">
      <div>
        <Label htmlFor="search" className="sr-only">
          Buscar
        </Label>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            id="search"
            placeholder="Buscar por título o empresa..."
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <Label htmlFor="area">Área</Label>
          <Select value={area} onValueChange={onAreaChange}>
            <SelectTrigger id="area">
              <SelectValue placeholder="Todas las áreas" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas las áreas</SelectItem>
              <SelectItem value="Tech">Tecnología</SelectItem>
              <SelectItem value="Marketing">Marketing</SelectItem>
              <SelectItem value="Sales">Ventas</SelectItem>
              <SelectItem value="Design">Diseño</SelectItem>
              <SelectItem value="HR">Recursos Humanos</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="modality">Modalidad</Label>
          <Select value={modality} onValueChange={onModalityChange}>
            <SelectTrigger id="modality">
              <SelectValue placeholder="Todas las modalidades" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas las modalidades</SelectItem>
              <SelectItem value="remote">Remoto</SelectItem>
              <SelectItem value="hybrid">Híbrido</SelectItem>
              <SelectItem value="onsite">Presencial</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="location">Ubicación</Label>
          <Input
            id="location"
            placeholder="Ciudad..."
            value={location}
            onChange={(e) => onLocationChange(e.target.value)}
          />
        </div>
      </div>
    </div>
  )
}
