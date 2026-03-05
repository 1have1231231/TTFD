import { NextResponse } from 'next/server'
import { deleteSession } from '@/lib/auth'
import { config } from '@/lib/config'

export async function POST() {
  await deleteSession()
  return NextResponse.redirect(config.app.url)
}
