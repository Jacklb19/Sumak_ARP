"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Eye, MoreHorizontal } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { Candidate, Seniority, CandidateStatus } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

interface CandidatesTableProps {
  candidates: Candidate[];
  onViewCandidate: (candidate: Candidate) => void;
}

const seniorityStyles: Record<Seniority, string> = {
  Junior: "bg-info/20 text-info border-info/30",
  Mid: "bg-warning/20 text-warning border-warning/30",
  Senior: "bg-primary/20 text-primary border-primary/30",
};

const statusStyles: Record<CandidateStatus, string> = {
  Pending: "bg-muted text-muted-foreground border-muted-foreground/30",
  Interviewing: "bg-warning/20 text-warning border-warning/30",
  Hired: "bg-success/20 text-success border-success/30",
  Rejected: "bg-destructive/20 text-destructive border-destructive/30",
};

export function CandidatesTable({
  candidates,
  onViewCandidate,
}: CandidatesTableProps) {
  return (
    <div className="border border-border bg-card">
      <Table>
        <TableHeader>
          <TableRow className="border-border hover:bg-transparent">
            <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Candidate
            </TableHead>
            <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Applied Role
            </TableHead>
            <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Seniority
            </TableHead>
            <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Overall Score
            </TableHead>
            <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Status
            </TableHead>
            <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground text-right">
              Actions
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {candidates.map((candidate) => (
            <TableRow
              key={candidate.id}
              className="border-border hover:bg-secondary/50 cursor-pointer transition-colors"
              onClick={() => onViewCandidate(candidate)}
            >
              <TableCell>
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center bg-secondary border border-border font-mono text-sm font-medium">
                    {candidate.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </div>
                  <div>
                    <p className="font-medium text-foreground">
                      {candidate.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {candidate.email}
                    </p>
                  </div>
                </div>
              </TableCell>
              <TableCell>
                <span className="text-sm text-foreground">
                  {candidate.appliedRole}
                </span>
              </TableCell>
              <TableCell>
                <Badge
                  variant="outline"
                  className={cn(
                    "font-mono text-xs",
                    seniorityStyles[candidate.seniority]
                  )}
                >
                  {candidate.seniority}
                </Badge>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-3 min-w-[140px]">
                  <Progress
                    value={candidate.overallScore}
                    className="h-2 flex-1 bg-secondary"
                  />
                  <span
                    className={cn(
                      "font-mono text-sm font-medium w-8",
                      candidate.overallScore >= 80
                        ? "text-primary"
                        : candidate.overallScore >= 60
                        ? "text-warning"
                        : "text-muted-foreground"
                    )}
                  >
                    {candidate.overallScore}
                  </span>
                </div>
              </TableCell>
              <TableCell>
                <Badge
                  variant="outline"
                  className={cn(
                    "font-mono text-xs",
                    statusStyles[candidate.status]
                  )}
                >
                  {candidate.status}
                </Badge>
              </TableCell>
              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-muted-foreground hover:text-foreground"
                    onClick={(e: React.MouseEvent) => {
                      e.stopPropagation();
                      onViewCandidate(candidate);
                    }}
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-muted-foreground hover:text-foreground"
                        onClick={(e: React.MouseEvent) => e.stopPropagation()}
                      >
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent
                      align="end"
                      className="bg-popover border-border"
                    >
                      <DropdownMenuItem>Schedule Interview</DropdownMenuItem>
                      <DropdownMenuItem>Send Message</DropdownMenuItem>
                      <DropdownMenuItem>Download CV</DropdownMenuItem>
                      <DropdownMenuItem className="text-destructive">
                        Reject
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
