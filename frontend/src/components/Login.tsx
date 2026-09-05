import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { signInWithGoogle } from '../lib/auth'
import { useAuth } from '../lib/AuthContext'

export default function Login() {
  const { status } = useAuth()

  if (status === 'loading') {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <p className="text-sm text-muted-foreground">Loading…</p>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Welcome to Hirify</CardTitle>
          <CardDescription>Sign in with Google to match resumes with jobs.</CardDescription>
        </CardHeader>
        <CardContent>
          <Button variant="outline" className="w-full" onClick={() => void signInWithGoogle()} type="button">
            Continue with Google
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
