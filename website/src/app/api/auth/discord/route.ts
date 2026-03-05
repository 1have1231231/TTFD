import { NextResponse } from 'next/server'
import { getDiscordAuthUrl } from '@/lib/discord'

export async function GET() {
  const authUrl = getDiscordAuthUrl()
  return NextResponse.redirect(authUrl)
}
