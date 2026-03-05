import { NextResponse } from 'next/server'
import { getSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { getDiscordAvatarUrl } from '@/lib/discord'

export async function GET() {
  const session = await getSession()

  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const user = await prisma.user.findUnique({
    where: { id: session.userId },
    include: {
      wallet: true,
      xp: true,
    },
  })

  if (!user) {
    return NextResponse.json({ error: 'User not found' }, { status: 404 })
  }

  const avatarUrl = user.avatarHash
    ? `https://cdn.discordapp.com/avatars/${user.discordId}/${user.avatarHash}.png?size=256`
    : null

  return NextResponse.json({
    id: user.id,
    discordId: user.discordId,
    username: user.username,
    globalName: user.globalName,
    avatarUrl,
    balance: user.wallet?.balance.toString() || '0',
    xp: user.xp?.xp.toString() || '0',
    level: user.xp?.level || 1,
  })
}
