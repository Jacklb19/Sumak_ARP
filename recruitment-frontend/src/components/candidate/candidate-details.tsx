"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { ScoreCard } from "./score-card";
import {
  ArrowLeft,
  Mail,
  FileText,
  Linkedin,
  Code,
  Users,
  Heart,
  Check,
  X,
  Bot,
  User,
  Calendar,
} from "lucide-react";
import type { Candidate } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

interface CandidateDetailsProps {
  candidate: Candidate;
  onBack: () => void;
}

const seniorityStyles = {
  Junior: "bg-info/20 text-info border-info/30",
  Mid: "bg-warning/20 text-warning border-warning/30",
  Senior: "bg-primary/20 text-primary border-primary/30",
};

export function CandidateDetails({ candidate, onBack }: CandidateDetailsProps) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={onBack}
          className="text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            Candidate Profile
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            AI-powered assessment overview
          </p>
        </div>
      </div>

      {/* Profile Header Card */}
      <Card className="bg-card border-border">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
            <div className="flex items-start gap-4">
              <div className="flex h-16 w-16 items-center justify-center bg-secondary border border-border font-mono text-xl font-bold">
                {candidate.name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")}
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <h2 className="text-xl font-bold text-foreground">
                    {candidate.name}
                  </h2>
                  <Badge
                    variant="outline"
                    className={cn(
                      "font-mono text-xs",
                      seniorityStyles[candidate.seniority]
                    )}
                  >
                    {candidate.seniority}
                  </Badge>
                </div>
                <p className="text-muted-foreground">{candidate.appliedRole}</p>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Mail className="h-4 w-4" />
                    {candidate.email}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    Applied{" "}
                    {new Date(candidate.appliedDate).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button
                variant="outline"
                size="sm"
                className="gap-2 border-border bg-transparent"
              >
                <FileText className="h-4 w-4" />
                View CV
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="gap-2 border-border bg-transparent"
              >
                <Linkedin className="h-4 w-4" />
                LinkedIn
              </Button>
              <Button
                size="sm"
                className="gap-2 bg-primary text-primary-foreground"
              >
                Schedule Interview
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Score Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ScoreCard
          title="Technical Score"
          score={candidate.technicalScore}
          icon={<Code className="h-4 w-4" />}
        />
        <ScoreCard
          title="Behavioral Score"
          score={candidate.behavioralScore}
          icon={<Users className="h-4 w-4" />}
        />
        <ScoreCard
          title="Cultural Fit"
          score={candidate.culturalFitScore}
          icon={<Heart className="h-4 w-4" />}
        />
      </div>

      {/* AI Summary */}
      <Card className="bg-card border-border">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <Bot className="h-5 w-5 text-primary" />
            AI Assessment Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="p-4 bg-secondary/50 border border-border">
            <p className="text-sm text-foreground leading-relaxed">
              {candidate.aiSummary.recommendation}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Pros */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
                <div className="h-5 w-5 flex items-center justify-center bg-success/20 text-success">
                  <Check className="h-3 w-3" />
                </div>
                Strengths
              </h4>
              <ul className="space-y-2">
                {candidate.aiSummary.pros.map((pro, index) => (
                  <li
                    key={index}
                    className="flex items-start gap-2 text-sm text-muted-foreground"
                  >
                    <span className="text-success mt-0.5">•</span>
                    {pro}
                  </li>
                ))}
              </ul>
            </div>

            {/* Cons */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
                <div className="h-5 w-5 flex items-center justify-center bg-destructive/20 text-destructive">
                  <X className="h-3 w-3" />
                </div>
                Areas of Concern
              </h4>
              <ul className="space-y-2">
                {candidate.aiSummary.cons.map((con, index) => (
                  <li
                    key={index}
                    className="flex items-start gap-2 text-sm text-muted-foreground"
                  >
                    <span className="text-destructive mt-0.5">•</span>
                    {con}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Transcript Viewer */}
      <Card className="bg-card border-border">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg font-semibold">
            Interview Transcript
          </CardTitle>
        </CardHeader>
        <CardContent>
          {candidate.transcript.length > 0 ? (
            <Accordion type="single" collapsible defaultValue="transcript">
              <AccordionItem value="transcript" className="border-border">
                <AccordionTrigger className="text-sm font-medium hover:no-underline">
                  View Full Conversation ({candidate.transcript.length}{" "}
                  messages)
                </AccordionTrigger>
                <AccordionContent>
                  <ScrollArea className="h-[400px] pr-4">
                    <div className="space-y-4 pt-4">
                      {candidate.transcript.map((message, index) => (
                        <div
                          key={index}
                          className={cn(
                            "flex gap-3",
                            message.role === "candidate" && "flex-row-reverse"
                          )}
                        >
                          <div
                            className={cn(
                              "flex h-8 w-8 shrink-0 items-center justify-center border",
                              message.role === "ai"
                                ? "bg-primary text-primary-foreground border-primary"
                                : "bg-secondary border-border"
                            )}
                          >
                            {message.role === "ai" ? (
                              <Bot className="h-4 w-4" />
                            ) : (
                              <User className="h-4 w-4" />
                            )}
                          </div>
                          <div
                            className={cn(
                              "flex-1 max-w-[80%]",
                              message.role === "candidate" && "text-right"
                            )}
                          >
                            <div
                              className={cn(
                                "inline-block p-3 text-sm",
                                message.role === "ai"
                                  ? "bg-secondary border border-border text-foreground"
                                  : "bg-primary/10 border border-primary/30 text-foreground"
                              )}
                            >
                              {message.message}
                            </div>
                            <p className="text-xs text-muted-foreground mt-1">
                              {message.timestamp}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Bot className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p className="text-sm">No interview transcript available yet</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
