import React, { createContext, useContext, useEffect, useState } from 'react'
import * as authService from '../services/authService.ts'

export interface AuthUser {
  id: string
  email: string
  username?: string | null
  full_name?: string | null
  role?: string | null
  is_active?: boolean
  email_verified?: boolean
}

interface AuthContextType {
  user: AuthUser | null
  loading: boolean
  signUp: (email: string, password: string, fullName?: string) => Promise<{ user: AuthUser | null; error: any }>
  signIn: (email: string, password: string) => Promise<{ user: AuthUser | null; error: any }>
  signOut: () => Promise<{ error: any }>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

const TOKEN_KEY = 'authToken'

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  // On app load, try to restore user from token
  useEffect(() => {
    const init = async () => {
      try {
        const token = localStorage.getItem(TOKEN_KEY)
        if (!token) {
          setLoading(false)
          return
        }
        const me = await authService.getCurrentUser()
        setUser(me)
      } catch (err) {
        // Token invalid or API not reachable
        localStorage.removeItem(TOKEN_KEY)
        setUser(null)
      } finally {
        setLoading(false)
      }
    }
    init()
  }, [])

  const signUp = async (email: string, password: string, fullName?: string) => {
    setLoading(true)
    try {
      const resp = await authService.register(email, password, fullName)
      const token = resp.access_token
      if (token) localStorage.setItem(TOKEN_KEY, token)
      setUser(resp.user)
      return { user: resp.user, error: null }
    } catch (error: any) {
      return { user: null, error }
    } finally {
      setLoading(false)
    }
  }

  const signIn = async (email: string, password: string) => {
    setLoading(true)
    try {
      const resp = await authService.login(email, password)
      const token = resp.access_token
      if (token) localStorage.setItem(TOKEN_KEY, token)
      setUser(resp.user)
      return { user: resp.user, error: null }
    } catch (error: any) {
      return { user: null, error }
    } finally {
      setLoading(false)
    }
  }

  const signOut = async () => {
    // Stateless JWT: just clear local storage and user state
    try {
      localStorage.removeItem(TOKEN_KEY)
      setUser(null)
      return { error: null }
    } catch (error: any) {
      return { error }
    }
  }

  const value: AuthContextType = {
    user,
    loading,
    signUp,
    signIn,
    signOut,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}