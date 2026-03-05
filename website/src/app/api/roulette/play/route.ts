import { NextRequest, NextResponse } from 'next/server'
import { getSession } from '@/lib/auth'
import { playRoulette } from '@/lib/roulette'
import { rateLimit } from '@/lib/rate-limit'
import { z } from 'zod'

const playSchema = z.object({
  bet: z.number().int().positive(),
  clientSeed: z.string().optional(),
  idempotencyKey: z.string().optional(),
})

// Store idempotency keys
const idempotencyCache = new Map<string, any>()

export async function POST(request: NextRequest) {
  const session = await getSession()

  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // Rate limiting
  if (!rateLimit(`roulette:${session.userId}`, 10, 60000)) {
    return NextResponse.json({ error: 'Too many requests' }, { status: 429 })
  }

  try {
    const body = await request.json()
    const { bet, clientSeed, idempotencyKey } = playSchema.parse(body)

    // Check idempotency
    if (idempotencyKey) {
      const cached = idempotencyCache.get(idempotencyKey)
      if (cached) {
        return NextResponse.json(cached)
      }
    }

    // Play roulette
    const result = await playRoulette(session.userId, BigInt(bet), clientSeed)

    const response = {
      result: result.result,
      payout: result.payout.toString(),
      newBalance: result.newBalance.toString(),
      roundId: result.roundId,
    }

    // Cache result for idempotency
    if (idempotencyKey) {
      idempotencyCache.set(idempotencyKey, response)
      setTimeout(() => idempotencyCache.delete(idempotencyKey), 60000)
    }

    return NextResponse.json(response)
  } catch (error: any) {
    console.error('Roulette error:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to play roulette' },
      { status: 400 }
    )
  }
}
