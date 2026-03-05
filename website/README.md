# TTFD Elite — Production-Ready Web Application

Elite Minimal style web application with Discord OAuth2, PostgreSQL database, XP leaderboard, synchronized coin balance, and roulette game.

## Features

- ✅ Discord OAuth2 authentication
- ✅ PostgreSQL database with Prisma ORM
- ✅ User profiles with avatars
- ✅ TOP-3 XP leaderboard
- ✅ Synchronized coin balance (website ↔ Discord bot)
- ✅ Roulette game with provably fair RNG
- ✅ Transaction logging
- ✅ Rate limiting & idempotency
- ✅ Elite Minimal UI (dark theme, glass panels, smooth animations)

## Tech Stack

- **Frontend**: Next.js 14 (App Router) + TypeScript + TailwindCSS
- **Backend**: Next.js API Routes
- **Database**: PostgreSQL + Prisma
- **Auth**: Discord OAuth2 + JWT sessions
- **Discord Bot**: discord.js (separate process)

## Installation

### 1. Install dependencies

```bash
npm install
```

### 2. Setup environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `DISCORD_CLIENT_ID` - Discord OAuth2 client ID
- `DISCORD_CLIENT_SECRET` - Discord OAuth2 client secret
- `DISCORD_REDIRECT_URI` - OAuth2 callback URL
- `DISCORD_GUILD_ID` - Your Discord server ID
- `DISCORD_BOT_TOKEN` - Discord bot token
- `JWT_SECRET` - Secret for JWT signing
- `ADMIN_DISCORD_IDS` - Comma-separated admin Discord IDs

### 3. Setup database

```bash
# Push schema to database
npm run db:push

# Or run migrations
npm run db:migrate

# Seed database with test data (optional)
npm run db:seed
```

### 4. Run development server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Production Build

```bash
npm run build
npm start
```

## API Endpoints

### Authentication
- `GET /api/auth/discord` - Redirect to Discord OAuth
- `GET /api/auth/discord/callback` - OAuth callback
- `POST /api/auth/logout` - Logout

### User
- `GET /api/me` - Get current user profile

### Leaderboard
- `GET /api/top/xp?limit=3` - Get top XP players

### Wallet
- `GET /api/wallet` - Get user balance
- `GET /api/transactions?limit=50` - Get transaction history

### Roulette
- `POST /api/roulette/play` - Play roulette
  ```json
  {
    "bet": 100,
    "clientSeed": "optional",
    "idempotencyKey": "optional"
  }
  ```

## Database Schema

### Users
- Discord ID, username, avatar
- Access/refresh tokens

### Wallets
- User balance (BigInt)
- Atomic transactions

### XP
- User XP and level

### Transactions
- Type, amount, metadata
- Full audit log

### Roulette Rounds
- Bet, result, payout
- Provably fair seeds

## Discord Bot Integration

The bot shares the same database and can:
- Award XP to users
- Modify balances
- View leaderboards

Bot commands (example):
- `/balance` - Check balance
- `/addxp @user amount` - Add XP (admin)
- `/givemoney @user amount` - Adjust balance (admin)

## Security Features

- ✅ HttpOnly cookies for sessions
- ✅ Rate limiting (10 req/min per user)
- ✅ Idempotency keys for roulette
- ✅ Atomic database transactions
- ✅ Input validation with Zod
- ✅ CSRF protection
- ✅ Provably fair RNG

## Project Structure

```
src/
├── app/
│   ├── api/          # API routes
│   ├── cabinet/      # User cabinet page
│   ├── roulette/     # Roulette page
│   ├── layout.tsx    # Root layout
│   └── page.tsx      # Landing page
├── lib/
│   ├── auth.ts       # JWT & sessions
│   ├── discord.ts    # Discord OAuth
│   ├── prisma.ts     # Database client
│   ├── wallet.ts     # Balance operations
│   ├── roulette.ts   # Roulette logic
│   └── rate-limit.ts # Rate limiting
prisma/
├── schema.prisma     # Database schema
└── seed.ts           # Seed data
```

## License

MIT
