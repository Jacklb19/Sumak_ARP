import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

// --- DEBUGGING BLOCK ---
// Esto imprimirá en la consola del navegador si las keys están cargando
if (typeof window !== 'undefined') {
  console.log("Supabase Config Check:")
  console.log("- URL Loaded:", !!supabaseUrl) // Debería decir true
  console.log("- Key Loaded:", !!supabaseAnonKey) // Debería decir true
}
// ----------------------

if (!supabaseUrl || !supabaseAnonKey) {
  // Este error es más descriptivo
  console.error("CRITICAL: Environment variables missing. Check .env.local file location.")
  throw new Error('Faltan las variables de entorno de Supabase (.env.local)')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
