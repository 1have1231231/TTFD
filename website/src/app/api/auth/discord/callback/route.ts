import { NextRequest, NextResponse } from 'next/server'
import { exchangeCodeForToken, getDiscordUser } from '@/lib/discord'
import { prisma } from '@/lib/prisma'
import { createSession } from '@/lib/auth'
import { config } from '@/lib/config'

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const code = searchParams.get('code')

  if (!code) {
    return NextResponse.redirect(`${config.app.url}?error=no_code`)
  }

  try {
    // Exchange code for tokens
    const tokens = await exchangeCodeForToken(code)
    
    // Get user info
    const discordUser = await getDiscordUser(tokens.access_token)

    // Create or update user in database
    const user = await prisma.user.upsert({
      where: { discordId: discordUser.id },
      create: {
        discordId: discordUser.id,
        username: discordUser.username,
        discriminator: discordUser.discriminator,
        globalName: discordUser.global_name,
        avatarHash: discordUser.avatar,
        accessToken: tokens.access_token,
        refreshToken: tokens.refresh_token,
        wallet: {
          create: {
            balance: BigInt(1000), // Starting balance
          },
        },
        xp: {
          create: {
            xp: BigInt(0),
            level: 1,
          },
        },
      },
      update: {
        username: discordUser.username,
        discriminator: discordUser.discriminator,
        globalName: discordUser.global_name,
        avatarHash: discordUser.avatar,
        accessToken: tokens.access_token,
        refreshToken: tokens.refresh_token,
      },
    })

    // Create session
    await createSession({
      userId: user.id,
      discordId: user.discordId,
      username: user.username,
    })

    return NextResponse.redirect(`${config.app.url}/cabinet`)
  } catch (error) {
    console.error('Discord OAuth error:', error)
    return NextResponse.redirect(`${config.app.url}?error=auth_failed`)
  }
}
