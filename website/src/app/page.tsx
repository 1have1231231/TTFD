import Link from 'next/link'
import { getSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

async function getTopXP() {
  const topUsers = await prisma.xP.findMany({
    orderBy: { xp: 'desc' },
    take: 3,
    include: {
      user: {
        select: {
          discordId: true,
          username: true,
          globalName: true,
          avatarHash: true,
        },
      },
    },
  })

  return topUsers.map((entry, index) => ({
    rank: index + 1,
    username: entry.user.globalName || entry.user.username,
    avatarUrl: entry.user.avatarHash
      ? `https://cdn.discordapp.com/avatars/${entry.user.discordId}/${entry.user.avatarHash}.png?size=256`
      : null,
    xp: entry.xp.toString(),
    level: entry.level,
  }))
}

export default async function Home() {
  const session = await getSession()
  const topPlayers = await getTopXP()

  return (
    <main className="min-h-screen">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 glass border-b">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="text-2xl font-bold tracking-wider">
              TTFD
            </Link>
            
            <div className="flex items-center gap-4">
              {session ? (
                <>
                  <Link
                    href="/cabinet"
                    className="px-4 py-2 glass glass-hover rounded text-sm font-medium"
                  >
                    Cabinet
                  </Link>
                  <Link
                    href="/roulette"
                    className="px-4 py-2 glass glass-hover rounded text-sm font-medium"
                  >
                    Roulette
                  </Link>
                </>
              ) : (
                <Link
                  href="/api/auth/discord"
                  className="px-6 py-2 bg-accent-primary hover:bg-accent-secondary rounded text-sm font-bold transition-colors"
                >
                  Login with Discord
                </Link>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="pt-32 pb-20 px-6">
        <div className="container mx-auto text-center">
          <h1 className="text-6xl font-black tracking-wider mb-6">
            TTFD
          </h1>
          <p className="text-xl text-gray-400 mb-8 tracking-wide">
            ELITE MINECRAFT CLAN
          </p>
          {!session && (
            <Link
              href="/api/auth/discord"
              className="inline-block px-8 py-3 bg-accent-primary hover:bg-accent-secondary rounded text-base font-bold transition-colors"
            >
              JOIN NOW
            </Link>
          )}
        </div>
      </section>

      {/* Top XP */}
      <section className="py-20 px-6">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-4xl font-black tracking-wider text-center mb-12">
            TOP XP
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {topPlayers.map((player) => (
              <div
                key={player.rank}
                className={`glass glass-hover rounded-lg p-8 text-center ${
                  player.rank === 1 ? 'border-accent-primary' : ''
                }`}
              >
                <div className="text-sm font-bold text-gray-500 mb-4">
                  #{player.rank}
                </div>
                
                {player.avatarUrl && (
                  <img
                    src={player.avatarUrl}
                    alt={player.username}
                    className="w-24 h-24 rounded-full mx-auto mb-4 border-2 border-dark-border"
                  />
                )}
                
                <h3 className="text-xl font-bold mb-2">{player.username}</h3>
                <div className="text-3xl font-black font-mono text-accent-primary mb-1">
                  {parseInt(player.xp).toLocaleString()}
                </div>
                <div className="text-sm text-gray-500">XP</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-dark-border">
        <div className="container mx-auto text-center">
          <div className="text-2xl font-bold tracking-wider mb-4">TTFD</div>
          <div className="flex justify-center gap-6 mb-4">
            <a
              href="https://discord.gg/JPtaNvJJ"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-white transition-colors"
            >
              DISCORD
            </a>
          </div>
          <p className="text-sm text-gray-600">
            © 2026 TTFD. ALL RIGHTS RESERVED.
          </p>
        </div>
      </footer>
    </main>
  )
}
