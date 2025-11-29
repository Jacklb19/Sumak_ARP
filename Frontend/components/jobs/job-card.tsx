import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import type { JobPosting } from "@/types"
import { MapPin, Briefcase, DollarSign } from "lucide-react"
import Link from "next/link"
import Image from "next/image"

interface JobCardProps {
  job: JobPosting
}

export function JobCard({ job }: JobCardProps) {
  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return null
    if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`
    if (min) return `Desde $${min.toLocaleString()}`
    return null
  }

  const modalityColors = {
    remote: "bg-green-100 text-green-800",
    hybrid: "bg-blue-100 text-blue-800",
    onsite: "bg-gray-100 text-gray-800",
  }

  const modalityLabels = {
    remote: "Remoto",
    hybrid: "Híbrido",
    onsite: "Presencial",
  }

  return (
    <Card className="hover:shadow-lg transition-shadow duration-200 flex flex-col h-full">
      <CardHeader>
        <div className="flex items-start gap-4">
          {job.company_logo ? (
            <Image
              src={job.company_logo || "/placeholder.svg"}
              alt={job.company_name}
              width={48}
              height={48}
              className="rounded-lg object-contain"
            />
          ) : (
            <div className="w-12 h-12 rounded-lg bg-muted flex items-center justify-center">
              <Briefcase className="h-6 w-6 text-muted-foreground" />
            </div>
          )}
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-lg leading-tight line-clamp-2">{job.title}</h3>
            <p className="text-sm text-muted-foreground mt-1">{job.company_name}</p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 space-y-3">
        <div className="flex flex-wrap gap-2">
          <Badge variant="secondary" className={modalityColors[job.modality]}>
            {modalityLabels[job.modality]}
          </Badge>
          <Badge variant="outline">
            <MapPin className="h-3 w-3 mr-1" />
            {job.location}
          </Badge>
          <Badge variant="outline">{job.contract_type}</Badge>
        </div>

        {formatSalary(job.salary_min, job.salary_max) && (
          <div className="flex items-center gap-2 text-sm font-medium text-primary">
            <DollarSign className="h-4 w-4" />
            {formatSalary(job.salary_min, job.salary_max)}
          </div>
        )}

        {job.required_skills?.languages && job.required_skills.languages.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {job.required_skills.languages.slice(0, 3).map((skill) => (
              <Badge key={skill} variant="secondary" className="text-xs">
                {skill}
              </Badge>
            ))}
            {job.required_skills.languages.length > 3 && (
              <Badge variant="secondary" className="text-xs">
                +{job.required_skills.languages.length - 3}
              </Badge>
            )}
          </div>
        )}
      </CardContent>

      <CardFooter>
        <Button className="w-full" asChild>
          <Link href={`/dashboard/jobs/${job.id}`}>Ver detalles</Link>
        </Button>
      </CardFooter>
    </Card>
  )
}
