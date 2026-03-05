import { redirect } from 'next/navigation'
import { getSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import Link from 'next/link'

export default async function CabinetPage() {
  const session = await getSession()

  if (!session) {
    redirect('/')
  }

  const user = await prisma.user.findUnique({
    where: { id: session.userId },
    include: {
      wallet: true,
      xp: true,
    },
  })

  if (!user) {
    redirect('/')
  }

  const avatarUrl = user.avatarHash
    ? `https://cdn.discordapp.com/avatars/${user.discordId}/${user.avatarHash}.png?size=256`
    : null

  return (
    <main className="min-h-screen">
      <header className="fixed top-0 left-0 right-0 z-50 glass border-b">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="text-2xl font-bold tracking-wider">
              TTFD
            </Link>
            <div className="flex items-center gap-4">
              <Link href="/roulette" className="px-4 py-2 glass glass-hover rounded text-sm">
                Roulette
              </Link>
              <form action="/api/auth/logout" method="POST">
                <button className="px-4 py-2 glass glass-hover rounded text-sm">
                  Logout
                </button>
              </form>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 pt-32 pb-20">
        <h1 className="text-4xl font-black tracking-wider mb-12">CABINET</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl">
          <div className="glass rounded-lg p-8">
            <h2 className="text-xl font-bold mb-6">Profile</h2>
            <div className="flex items-center gap-4 mb-6">
              {avatarUrl && (
                <img src={avatarUrl} alt={user.username} className="w-20 h-20 rounded-full" />
              )}
              <div>
                <div className="text-2xl font-bold">{user.globalName || user.username}</div>
                <div className="text-sm text-gray-500">#{user.discriminator}</div>
              </div>
            </div>
          </div>

          <div className="glass rounded-lg p-8">
            <h2 className="text-xl font-bold mb-6">Balance</h2>
            <div className="text-4xl font-black font-mono text-accent-primary">
              {user.wallet?.balance.toString() || '0'}
            </div>
            <div className="text-sm text-gray-500 mt-2">COINS</div>
          </div>

          <div className="glass rounded-lg p-8">
            <h2 className="text-xl font-bold mb-6">Experience</h2>
            <div className="text-4xl font-black font-mono text-accent-primary">
              {user.xp?.xp.toString() || '0'}
            </div>
            <div className="text-sm text-gray-500 mt-2">XP · LEVEL {user.xp?.level || 1}</div>
          </div>

          <div className="glass rounded-lg p-8">
            <h2 className="text-xl font-bold mb-6">Quick Actions</h2>
            <Link
              href="/roulette"
              className="block w-full px-6 py-3 bg-accent-primary hover:bg-accent-secondary rounded text-center font-bold transition-colors"
            >
              Play Roulette
            </Link>
          </div>
        </div>
      </div>
    </main>
  )
}
