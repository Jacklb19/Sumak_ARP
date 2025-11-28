"use client";

import { useEffect, useState } from "react";
import { createClient } from "@supabase/supabase-js";
import {
  LayoutDashboard,
  Users,
  Briefcase,
  Settings,
  Search,
  Bell,
  ChevronRight,
  MoreHorizontal,
  BarChart3,
  CheckCircle2,
  Clock,
  XCircle,
} from "lucide-react";

// --- 1. CONFIGURACIÓN SUPABASE (Si ya tienes lib/supabase.ts, impórtalo y borra esto) ---
const supabaseUrl =
  process.env.NEXT_PUBLIC_SUPABASE_URL || "https://example.supabase.co";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "anon-key";
const supabase = createClient(supabaseUrl, supabaseAnonKey);

// --- 2. TIPOS DE DATOS ---
export type Seniority = "Junior" | "Mid" | "Senior";
export type CandidateStatus = "Pending" | "Interviewing" | "Hired" | "Rejected";

export interface Candidate {
  id: string;
  name: string;
  email: string;
  appliedRole: string;
  seniority: Seniority;
  technicalScore: number;
  behavioralScore: number;
  culturalFitScore: number;
  overallScore: number;
  status: CandidateStatus;
  cvUrl: string;
  linkedinUrl: string;
  appliedDate: string;
  aiSummary: {
    recommendation: string;
    pros: string[];
    cons: string[];
  };
  transcript: {
    role: "ai" | "candidate";
    message: string;
    timestamp: string;
  }[];
}

// --- 3. COMPONENTE PRINCIPAL ---
export default function DashboardPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(
    null
  );

  // --- HOOK DE CARGA DE DATOS ---
  useEffect(() => {
    async function fetchData() {
      try {
        console.log("Cargando datos de Supabase...");

        // Consulta real a tu DB
        const { data, error } = await supabase
          .from("candidates")
          .select(
            `
            id, name, email, status, cv_url, created_at, linkedin_url,
            jobs ( title, seniority ),
            evaluations ( 
              technical_score, 
              behavioral_score, 
              cultural_fit_score, 
              overall_score,
              interview_transcript,
              recommendations
            )
          `
          )
          .order("created_at", { ascending: false });

        if (error) throw error;

        // Mapeo de DB -> UI
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const mappedData: Candidate[] = (data || []).map((row: any) => {
          const ev = row.evaluations?.[0] || {};

          // Parsear transcript seguro
          let transcript = [];
          try {
            transcript =
              typeof ev.interview_transcript === "string"
                ? JSON.parse(ev.interview_transcript)
                : ev.interview_transcript || [];
          } catch (e) {
            console.error("Error parsing transcript", e);
          }

          return {
            id: row.id,
            name: row.name,
            email: row.email,
            appliedRole: row.jobs?.title || "Unknown Role",
            seniority: (row.jobs?.seniority || "Mid") as Seniority, // Fallback

            technicalScore: ev.technical_score || 0,
            behavioralScore: ev.behavioral_score || 0,
            culturalFitScore: ev.cultural_fit_score || 0,
            overallScore: ev.overall_score || 0,

            // Normalizar Status: "pending" -> "Pending"
            status: (row.status
              ? row.status.charAt(0).toUpperCase() + row.status.slice(1)
              : "Pending") as CandidateStatus,

            cvUrl: row.cv_url || "#",
            linkedinUrl: row.linkedin_url || "#",
            appliedDate: new Date(row.created_at).toLocaleDateString(),

            aiSummary: {
              recommendation: ev.recommendations || "Pending analysis...",
              pros: [], // Placeholder
              cons: [], // Placeholder
            },

            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            transcript: transcript.map((t: any) => ({
              role: t.role || "ai",
              message: t.message || "",
              timestamp: t.timestamp || "Now",
            })),
          };
        });

        setCandidates(mappedData);
      } catch (err) {
        console.error("Error fetching candidates:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  // --- RENDERIZADO ---
  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 font-sans">
      {/* SIDEBAR */}
      <aside className="w-64 border-r border-slate-800 bg-slate-950 p-6 hidden md:flex flex-col">
        <div className="flex items-center gap-2 mb-10">
          <div className="h-8 w-8 bg-indigo-600 rounded-lg flex items-center justify-center font-bold">
            AI
          </div>
          <span className="text-xl font-bold tracking-tight">Recruit.OS</span>
        </div>

        <nav className="space-y-2 flex-1">
          <NavItem
            icon={<LayoutDashboard size={20} />}
            label="Dashboard"
            active
          />
          <NavItem icon={<Users size={20} />} label="Candidates" />
          <NavItem icon={<Briefcase size={20} />} label="Jobs" />
          <NavItem icon={<BarChart3 size={20} />} label="Analytics" />
        </nav>

        <div className="pt-6 border-t border-slate-800">
          <NavItem icon={<Settings size={20} />} label="Settings" />
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 overflow-y-auto">
        <header className="h-16 border-b border-slate-800 flex items-center justify-between px-8 bg-slate-950 sticky top-0 z-10">
          <h1 className="text-lg font-semibold">Overview</h1>
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search
                className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                size={16}
              />
              <input
                type="text"
                placeholder="Search candidates..."
                className="bg-slate-900 border border-slate-800 rounded-full pl-10 pr-4 py-1.5 text-sm focus:outline-none focus:border-indigo-500 w-64"
              />
            </div>
            <button className="p-2 hover:bg-slate-800 rounded-full relative">
              <Bell size={20} className="text-slate-400" />
              <span className="absolute top-2 right-2 w-2 h-2 bg-indigo-500 rounded-full"></span>
            </button>
            <div className="h-8 w-8 bg-slate-800 rounded-full border border-slate-700"></div>
          </div>
        </header>

        <div className="p-8 space-y-8">
          {/* KPI CARDS */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <KpiCard
              title="Total Candidates"
              value={candidates.length.toString()}
              change="+12%"
            />
            <KpiCard
              title="Interviews Active"
              value={candidates
                .filter((c) => c.status === "Interviewing")
                .length.toString()}
              change="+4"
            />
            <KpiCard
              title="High Performers"
              value={candidates
                .filter((c) => c.overallScore > 80)
                .length.toString()}
              change="Top 10%"
            />
          </div>

          {/* TABLE SECTION */}
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden">
            <div className="p-6 flex items-center justify-between border-b border-slate-800">
              <h2 className="text-lg font-semibold">Recent Candidates</h2>
              <button className="text-sm text-indigo-400 hover:text-indigo-300 font-medium">
                View All
              </button>
            </div>

            {loading ? (
              <div className="p-10 text-center text-slate-500">
                Syncing with Supabase...
              </div>
            ) : candidates.length === 0 ? (
              <div className="p-10 text-center text-slate-500">
                No candidates found. Insert data in DB.
              </div>
            ) : (
              <table className="w-full text-left">
                <thead className="bg-slate-900 text-slate-400 text-xs uppercase tracking-wider">
                  <tr>
                    <th className="px-6 py-4 font-medium">Name</th>
                    <th className="px-6 py-4 font-medium">Role applied</th>
                    <th className="px-6 py-4 font-medium">Score</th>
                    <th className="px-6 py-4 font-medium">Status</th>
                    <th className="px-6 py-4 font-medium">Date</th>
                    <th className="px-6 py-4 font-medium text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {candidates.map((candidate) => (
                    <tr
                      key={candidate.id}
                      className="hover:bg-slate-800/50 transition-colors cursor-pointer group"
                      onClick={() => setSelectedCandidate(candidate)}
                    >
                      <td className="px-6 py-4">
                        <div className="font-medium text-slate-200">
                          {candidate.name}
                        </div>
                        <div className="text-xs text-slate-500">
                          {candidate.email}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-slate-400">
                        {candidate.appliedRole}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div className="w-full bg-slate-800 rounded-full h-1.5 w-24 overflow-hidden">
                            <div
                              className={`h-full rounded-full ${getScoreColor(
                                candidate.overallScore
                              )}`}
                              style={{ width: `${candidate.overallScore}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium">
                            {candidate.overallScore}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <StatusBadge status={candidate.status} />
                      </td>
                      <td className="px-6 py-4 text-slate-500 text-sm">
                        {candidate.appliedDate}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button className="p-2 hover:bg-slate-700 rounded opacity-0 group-hover:opacity-100 transition-opacity">
                          <MoreHorizontal
                            size={16}
                            className="text-slate-400"
                          />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </main>

      {/* DETAIL PANEL (MODAL SIMPLE) */}
      {selectedCandidate && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex justify-end">
          <div className="w-full max-w-2xl bg-slate-950 border-l border-slate-800 h-full overflow-y-auto p-8 animate-in slide-in-from-right duration-300">
            <div className="flex justify-between items-start mb-8">
              <div>
                <h2 className="text-2xl font-bold">{selectedCandidate.name}</h2>
                <p className="text-slate-400">
                  {selectedCandidate.appliedRole}
                </p>
              </div>
              <button
                onClick={() => setSelectedCandidate(null)}
                className="p-2 hover:bg-slate-800 rounded-full"
              >
                <XCircle className="text-slate-400" />
              </button>
            </div>

            <div className="space-y-6">
              <div className="p-4 bg-slate-900 rounded-lg border border-slate-800">
                <h3 className="text-sm font-semibold text-slate-400 uppercase mb-3">
                  AI Summary
                </h3>
                <p className="text-slate-300 leading-relaxed">
                  {selectedCandidate.aiSummary.recommendation}
                </p>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-slate-400 uppercase mb-3">
                  Interview Transcript
                </h3>
                <div className="space-y-4 bg-slate-900/50 p-4 rounded-lg border border-slate-800 max-h-96 overflow-y-auto">
                  {selectedCandidate.transcript.length > 0 ? (
                    selectedCandidate.transcript.map((msg, i) => (
                      <div
                        key={i}
                        className={`flex flex-col ${
                          msg.role === "ai" ? "items-start" : "items-end"
                        }`}
                      >
                        <div
                          className={`max-w-[85%] p-3 rounded-lg text-sm ${
                            msg.role === "ai"
                              ? "bg-slate-800 text-slate-200"
                              : "bg-indigo-900/50 text-indigo-100 border border-indigo-800"
                          }`}
                        >
                          {msg.message}
                        </div>
                        <span className="text-[10px] text-slate-600 mt-1">
                          {msg.timestamp}
                        </span>
                      </div>
                    ))
                  ) : (
                    <p className="text-slate-500 italic text-center">
                      No transcript available yet.
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// --- COMPONENTES AUXILIARES ---

function NavItem({
  icon,
  label,
  active = false,
}: {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
}) {
  return (
    <button
      className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
        active
          ? "bg-indigo-600/10 text-indigo-400 border border-indigo-600/20"
          : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

function KpiCard({
  title,
  value,
  change,
}: {
  title: string;
  value: string;
  change: string;
}) {
  return (
    <div className="bg-slate-900 p-6 rounded-xl border border-slate-800">
      <h3 className="text-slate-500 text-sm font-medium mb-2">{title}</h3>
      <div className="flex items-end justify-between">
        <span className="text-3xl font-bold text-slate-100">{value}</span>
        <span className="text-emerald-400 text-sm font-medium bg-emerald-400/10 px-2 py-0.5 rounded">
          {change}
        </span>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: CandidateStatus }) {
  const styles = {
    Pending: "bg-slate-800 text-slate-400 border-slate-700",
    Interviewing: "bg-indigo-900/30 text-indigo-400 border-indigo-800",
    Hired: "bg-emerald-900/30 text-emerald-400 border-emerald-800",
    Rejected: "bg-red-900/30 text-red-400 border-red-800",
  };

  const icons = {
    Pending: <Clock size={12} />,
    Interviewing: <Clock size={12} />,
    Hired: <CheckCircle2 size={12} />,
    Rejected: <XCircle size={12} />,
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
        styles[status] || styles.Pending
      }`}
    >
      {icons[status] || icons.Pending}
      {status}
    </span>
  );
}

function getScoreColor(score: number) {
  if (score >= 80) return "bg-emerald-500";
  if (score >= 60) return "bg-yellow-500";
  return "bg-red-500";
}
