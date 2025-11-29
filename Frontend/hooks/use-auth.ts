"use client"

import { useState, useEffect } from "react"
import { apiClient } from "@/lib/api"
import type { Candidate } from "@/types"

export function useAuth() {
  const [user, setUser] = useState<Candidate | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const token = localStorage.getItem("auth_token")

    if (!token) {
      setLoading(false)
      return
    }

    try {
      const response = await apiClient.get("/api/v1/candidates/me")
      setUser(response.data)
    } catch (error) {
      console.error("Auth check failed:", error)
      localStorage.removeItem("auth_token")
      localStorage.removeItem("candidate_id")
      localStorage.removeItem("full_name")
    } finally {
      setLoading(false)
    }
  }

  const login = (token: string, candidateId: string, fullName: string) => {
    localStorage.setItem("auth_token", token)
    localStorage.setItem("candidate_id", candidateId)
    localStorage.setItem("full_name", fullName)
    checkAuth()
  }

  const logout = () => {
    localStorage.removeItem("auth_token")
    localStorage.removeItem("candidate_id")
    localStorage.removeItem("full_name")
    setUser(null)
    window.location.href = "/auth/login"
  }

  return { user, loading, login, logout, checkAuth }
}
