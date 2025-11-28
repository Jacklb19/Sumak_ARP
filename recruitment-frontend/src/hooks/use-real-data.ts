// Archivo: src/hooks/use-real-data.ts

import { useEffect, useState } from 'react'
// Asegúrate de que esta ruta sea correcta según dónde creaste el cliente
import { supabase } from '@/lib/supabase' 
// Importamos los tipos que te dio v0 (asumiendo que están en mock-data.ts)
// Si te da error de importación, borra esta línea y define la interfaz 'Candidate' aquí mismo (ver abajo)
import type { Candidate } from '@/lib/mock-data' 

export function useRealDashboardData() {
  // Estado para guardar la lista de candidatos
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        console.log("Fetching data from Supabase...")

        // 1. Consulta a Supabase
        // Hacemos JOIN con 'jobs' para sacar el título del puesto
        // Hacemos JOIN con 'evaluations' para sacar los scores
        const { data, error } = await supabase
          .from('candidates')
          .select(`
            *,
            jobs ( title, seniority ),
            evaluations ( 
              technical_score, 
              behavioral_score, 
              cultural_fit_score, 
              overall_score,
              interview_transcript,
              recommendations
            )
          `)
          .order('created_at', { ascending: false })

        if (error) {
          console.error("Supabase Error:", error)
          throw error
        }

        // 2. Mapeo (Transformación) de Datos
        // Convertimos lo que llega de la DB al formato que espera tu UI (Candidate)
        const adaptedData: Candidate[] = (data || []).map((row: any) => {
          // Tomamos la primera evaluación (o un objeto vacío si no existe)
          const ev = row.evaluations?.[0] || {}
          
          // Intentamos parsear el transcript si viene como string JSON
          let transcript = []
          try {
             transcript = typeof ev.interview_transcript === 'string' 
               ? JSON.parse(ev.interview_transcript) 
               : (ev.interview_transcript || [])
          } catch (e) {
            console.log("Transcript parsing error", e)
          }

          return {
            id: row.id,
            name: row.name,
            email: row.email,
            // Si no hay job, ponemos 'Unknown'
            appliedRole: row.jobs?.title || 'Unknown Role',
            // Default a 'Mid' si no viene nada
            seniority: (row.jobs?.seniority || 'Mid') as any,
            
            // Scores (default a 0)
            technicalScore: ev.technical_score || 0,
            behavioralScore: ev.behavioral_score || 0,
            culturalFitScore: ev.cultural_fit_score || 0,
            overallScore: ev.overall_score || 0,
            
            // Capitalizamos el status (pending -> Pending)
            status: (row.status ? row.status.charAt(0).toUpperCase() + row.status.slice(1) : 'Pending') as any,
            
            cvUrl: row.cv_url || '#',
            linkedinUrl: row.linkedin_url || '#',
            appliedDate: new Date(row.created_at).toLocaleDateString(),
            
            aiSummary: {
               recommendation: ev.recommendations || "Pending analysis...",
               pros: [], // Placeholder
               cons: []  // Placeholder
            },
            
            transcript: transcript
          }
        })
        
        setCandidates(adaptedData)
      } catch (err) {
        console.error("Error fetching candidates:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  return { candidates, loading }
}
