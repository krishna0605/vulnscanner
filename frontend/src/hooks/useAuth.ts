import { useState, useEffect, useCallback } from 'react'
import { User, Session } from '@supabase/supabase-js'
import { auth, isSupabaseConfigured } from '../lib/supabase.ts'

interface AuthState {
  user: User | null
  session: Session | null
  loading: boolean
  error: string | null
}

interface AuthActions {
  signIn: (email: string, password: string) => Promise<{ error: any }>
  signUp: (email: string, password: string, userData?: any) => Promise<{ error: any }>
  signOut: () => Promise<{ error: any }>
  resetPassword: (email: string) => Promise<{ error: any }>
  updatePassword: (password: string) => Promise<{ error: any }>
  clearError: () => void
}

export const useAuth = (): AuthState & AuthActions => {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Check if Supabase should be skipped
  const skipSupabase = process.env.REACT_APP_SKIP_SUPABASE === 'true' || 
                      process.env.REACT_APP_ENVIRONMENT === 'development'

  // Initialize auth state
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        setLoading(true)
        
        // If Supabase is disabled, skip initialization
        if (skipSupabase || !isSupabaseConfigured) {
          console.log('Supabase authentication disabled - using backend API auth only')
          setSession(null)
          setUser(null)
          setLoading(false)
          return
        }
        
        const currentSession = await auth.getCurrentSession()
        const currentUser = await auth.getCurrentUser()
        
        setSession(currentSession)
        setUser(currentUser)
      } catch (err) {
        console.error('Error initializing auth:', err)
        setError('Failed to initialize authentication')
      } finally {
        setLoading(false)
      }
    }

    initializeAuth()

    // Only set up auth state listener if Supabase is enabled
    if (!skipSupabase && isSupabaseConfigured) {
      // Listen for auth state changes
      const { data: { subscription } } = auth.onAuthStateChange(
        async (event, session) => {
          console.log('Auth state changed:', event, session)
          setSession(session)
          setUser(session?.user ?? null)
          setLoading(false)
        }
      )

      return () => subscription.unsubscribe()
    }
  }, [skipSupabase])

  // Sign in function
  const signIn = useCallback(async (email: string, password: string) => {
    try {
      setLoading(true)
      setError(null)
      
      // If Supabase is disabled or not configured, return error to trigger fallback
      if (skipSupabase || !isSupabaseConfigured) {
        const msg = 'Supabase authentication disabled - using backend API fallback'
        setError(msg)
        return { error: { message: msg } }
      }
      
      const { error } = await auth.signIn(email, password)
      
      if (error) {
        setError(error.message)
        return { error }
      }
      
      return { error: null }
    } catch (err) {
      const errorMessage = 'An unexpected error occurred during sign in'
      setError(errorMessage)
      return { error: { message: errorMessage } }
    } finally {
      setLoading(false)
    }
  }, [skipSupabase])

  // Sign up function
  const signUp = useCallback(async (email: string, password: string, userData?: any) => {
    try {
      setLoading(true)
      setError(null)
      
      // If Supabase is disabled or not configured, return error to trigger fallback
      if (skipSupabase || !isSupabaseConfigured) {
        const msg = 'Supabase authentication disabled - using backend API fallback'
        setError(msg)
        return { error: { message: msg } }
      }
      
      const { error } = await auth.signUp(email, password, userData)
      
      if (error) {
        setError(error.message)
        return { error }
      }
      
      return { error: null }
    } catch (err) {
      const errorMessage = 'An unexpected error occurred during sign up'
      setError(errorMessage)
      return { error: { message: errorMessage } }
    } finally {
      setLoading(false)
    }
  }, [skipSupabase])

  // Sign out function
  const signOut = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      // If Supabase is disabled, just clear local state
      if (skipSupabase || !isSupabaseConfigured) {
        setUser(null)
        setSession(null)
        return { error: null }
      }
      
      const { error } = await auth.signOut()
      
      if (error) {
        setError(error.message)
        return { error }
      }
      
      return { error: null }
    } catch (err) {
      const errorMessage = 'An unexpected error occurred during sign out'
      setError(errorMessage)
      return { error: { message: errorMessage } }
    } finally {
      setLoading(false)
    }
  }, [skipSupabase])

  // Reset password function
  const resetPassword = useCallback(async (email: string) => {
    try {
      setLoading(true)
      setError(null)
      
      // If Supabase is disabled, return error to trigger fallback
      if (skipSupabase || !isSupabaseConfigured) {
        const msg = 'Supabase authentication disabled - using backend API fallback'
        setError(msg)
        return { error: { message: msg } }
      }
      
      const { error } = await auth.resetPassword(email)
      
      if (error) {
        setError(error.message)
        return { error }
      }
      
      return { error: null }
    } catch (err) {
      const errorMessage = 'An unexpected error occurred during password reset'
      setError(errorMessage)
      return { error: { message: errorMessage } }
    } finally {
      setLoading(false)
    }
  }, [skipSupabase])

  // Update password function
  const updatePassword = useCallback(async (password: string) => {
    try {
      setLoading(true)
      setError(null)
      
      // If Supabase is disabled, return error to trigger fallback
      if (skipSupabase || !isSupabaseConfigured) {
        const msg = 'Supabase authentication disabled - using backend API fallback'
        setError(msg)
        return { error: { message: msg } }
      }
      
      const { error } = await auth.updatePassword(password)
      
      if (error) {
        setError(error.message)
        return { error }
      }
      
      return { error: null }
    } catch (err) {
      const errorMessage = 'An unexpected error occurred during password update'
      setError(errorMessage)
      return { error: { message: errorMessage } }
    } finally {
      setLoading(false)
    }
  }, [skipSupabase])

  // Clear error function
  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return {
    // State
    user,
    session,
    loading,
    error,
    // Actions
    signIn,
    signUp,
    signOut,
    resetPassword,
    updatePassword,
    clearError,
  }
}

export default useAuth