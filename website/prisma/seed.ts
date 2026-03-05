import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  console.log('🌱 Seeding database...')

  // Create test user
  const testUser = await prisma.user.upsert({
    where: { discordId: '123456789012345678' },
    update: {},
    create: {
      discordId: '123456789012345678',
      username: 'TestUser',
      globalName: 'Test User',
      avatarHash: null,
      wallet: {
        create: {
          balance: BigInt(10000),
        },
      },
      xp: {
        create: {
          xp: BigInt(1500),
          level: 5,
        },
      },
    },
  })

  console.log('✅ Created test user:', testUser.username)

  // Create more test users for leaderboard
  const users = [
    { discordId: '111111111111111111', username: 'TopPlayer1', xp: 5000, balance: 50000 },
    { discordId: '222222222222222222', username: 'TopPlayer2', xp: 3500, balance: 30000 },
    { discordId: '333333333333333333', username: 'TopPlayer3', xp: 2000, balance: 20000 },
  ]

  for (const userData of users) {
    await prisma.user.upsert({
      where: { discordId: userData.discordId },
      update: {},
      create: {
        discordId: userData.discordId,
        username: userData.username,
        globalName: userData.username,
        wallet: {
          create: {
            balance: BigInt(userData.balance),
          },
        },
        xp: {
          create: {
            xp: BigInt(userData.xp),
            level: Math.floor(userData.xp / 1000) + 1,
          },
        },
      },
    })
  }

  console.log('✅ Seeding completed!')
}

main()
  .catch((e) => {
    console.error('❌ Seeding failed:', e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
