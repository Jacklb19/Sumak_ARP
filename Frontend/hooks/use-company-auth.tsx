// <CHANGE> Adding company authentication hook
"use client"

import { useEffect, useState } from "react"
import { useRouter } from 'next/navigation'

export function useCompanyAuth() {
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const storedToken = localStorage.getItem("company_token")
    setToken(storedToken)
    setIsLoading(false)

    if (!storedToken) {
      router.push("/auth/login-company")
    }
  }, [router])

  const login = (newToken: string) => {
    localStorage.setItem("company_token", newToken)
    setToken(newToken)
  }

  const logout = () => {
    localStorage.removeItem("company_token")
    setToken(null)
    router.push("/auth/login-company")
  }

  return { token, isLoading, isAuthenticated: !!token, login, logout }
}
