# 🚀 Quick Start Guide

## Prerequisites

- Node.js 18+ 
- PostgreSQL database
- Discord Application (for OAuth2)

## Setup Steps

### 1. Install Dependencies

```bash
cd website
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and fill in:
- Database URL
- Discord credentials
- JWT secret

### 3. Setup Database

```bash
npm run db:push
npm run db:seed
```

### 4. Run Development Server

```bash
npm run dev
```

Visit: http://localhost:3000

## Discord OAuth Setup

1. Go to https://discord.com/developers/applications
2. Create New Application
3. OAuth2 → Add Redirect: `http://localhost:3000/api/auth/discord/callback`
4. Copy Client ID and Secret to `.env`

## Test Accounts

After seeding, you can test with:
- Discord ID: `123456789012345678`
- Balance: 10,000 coins
- XP: 1,500

## Production Deployment

```bash
npm run build
npm start
```

## Troubleshooting

**Database connection failed**
- Check DATABASE_URL in .env
- Ensure PostgreSQL is running

**Discord OAuth error**
- Verify DISCORD_CLIENT_ID and SECRET
- Check redirect URI matches exactly

**Rate limit errors**
- Wait 60 seconds
- Check rate-limit.ts configuration

## Next Steps

1. Configure Discord bot (see bot/ folder)
2. Customize roulette settings in .env
3. Add admin Discord IDs
4. Deploy to production (Vercel/Railway)

## Support

Check README.md for full documentation.
