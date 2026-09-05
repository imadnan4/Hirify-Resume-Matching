import { createInternalNeonAuth, type ReactBetterAuthClient } from '@neondatabase/auth'
import { BetterAuthReactAdapter } from '@neondatabase/auth/react'

const FALLBACK_AUTH_URL = 'https://ep-square-cell-b3jhlrm9.neonauth.c-4.ap-southeast-1.aws.neon.tech/neondb/auth'

export const NEON_AUTH_URL = import.meta.env.VITE_NEON_AUTH_URL || FALLBACK_AUTH_URL

export const neonAuth = createInternalNeonAuth(NEON_AUTH_URL, {
  adapter: BetterAuthReactAdapter({ fetchOptions: { credentials: 'include' } }),
})

/** Better Auth react client (signIn.email, signUp.email, signIn.social, signOut, useSession ...) */
export const authClient = neonAuth.adapter as unknown as ReactBetterAuthClient

/** Fetches a fresh JWT for the current session (null when signed out). */
export const getAuthToken = async (): Promise<string | null> => {
  const jwt = await neonAuth.getJWTToken()
  if (jwt) return jwt
  // Fallback: explicit token endpoint (uses the session cookie)
  try {
    const res = await fetch(`${NEON_AUTH_URL}/token`, { credentials: 'include' })
    if (res.ok) {
      const data = (await res.json()) as { token?: string }
      return data.token ?? null
    }
  } catch {
    /* not signed in */
  }
  return null
}

export interface AuthUser {
  id: string
  email: string
  name?: string | null
  image?: string | null
}

/** Initiates Google shared OAuth; browser lands on callbackURL after consent. */
export const signInWithGoogle = (): Promise<unknown> =>
  authClient.signIn.social({
    provider: 'google',
    callbackURL: window.location.origin,
  })
