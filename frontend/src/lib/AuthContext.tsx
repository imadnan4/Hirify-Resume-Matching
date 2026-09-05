import { createContext, useCallback, useContext, useMemo } from 'react'
import { authClient, type AuthUser } from './auth'

type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated'

interface AuthContextValue {
  status: AuthStatus
  user: AuthUser | null
  token: string | null
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  // Reactive: better-auth's useSession subscribes to the session store, so a
  // successful signIn/signUp anywhere immediately updates status here.
  const { data: sessionData, isPending } = authClient.useSession()

  const status: AuthStatus = isPending
    ? 'loading'
    : sessionData?.user
      ? 'authenticated'
      : 'unauthenticated'

  const signOut = useCallback(async () => {
    try {
      await authClient.signOut()
    } catch {
      /* session already gone */
    }
  }, [])

  const value = useMemo(
    () => ({
      status,
      user: (sessionData?.user as AuthUser | undefined) ?? null,
      token: sessionData?.session?.token ?? null,
      signOut,
    }),
    [status, sessionData, signOut],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
