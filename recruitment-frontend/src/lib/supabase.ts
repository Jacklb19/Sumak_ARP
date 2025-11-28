import { createClient } from '@supabase/supabase-js'

// 1. Leemos las variables de entorno
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

// 2. Validación de seguridad para que no explote si faltan las keys
if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Faltan las variables de entorno de Supabase (.env.local)')
}

// 3. Creamos y exportamos el cliente
export const supabase = createClient(supabaseUrl, supabaseAnonKey)
