import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const limit = parseInt(searchParams.get('limit') || '3')

  const topUsers = await prisma.xP.findMany({
    orderBy: { xp: 'desc' },
    take: Math.min(limit, 100),
    include: {
      user: {
        select: {
          id: true,
          discordId: true,
          username: true,
          globalName: true,
          avatarHash: true,
        },
      },
    },
  })

  const result = topUsers.map((entry, index) => ({
    rank: index + 1,
    userId: entry.user.id,
    discordId: entry.user.discordId,
    username: entry.user.username,
    globalName: entry.user.globalName,
    avatarUrl: entry.user.avatarHash
      ? `https://cdn.discordapp.com/avatars/${entry.user.discordId}/${entry.user.avatarHash}.png?size=256`
      : null,
    xp: entry.xp.toString(),
    level: entry.level,
  }))

  return NextResponse.json({ items: result })
}
