# 🚂 Railway Deployment Guide

## Prerequisites

- Railway account (https://railway.app)
- Discord Application configured
- GitHub repository

## Step 1: Create Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Select `website` folder as root directory

## Step 2: Add PostgreSQL Database

1. In your Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create `DATABASE_URL` variable

## Step 3: Configure Environment Variables

Add these variables in Railway dashboard:

### Required Variables

```
DATABASE_URL=<automatically set by Railway>
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret
DISCORD_REDIRECT_URI=https://your-app.railway.app/api/auth/discord/callback
DISCORD_GUILD_ID=your_discord_guild_id
DISCORD_BOT_TOKEN=your_discord_bot_token
JWT_SECRET=generate_random_secret_here
SESSION_SECRET=generate_random_secret_here
NEXT_PUBLIC_APP_URL=https://your-app.railway.app
NODE_ENV=production
```

### Optional Variables

```
ADMIN_DISCORD_IDS=123456789012345678,987654321098765432
ROULETTE_MIN_BET=10
ROULETTE_MAX_BET=100000
ROULETTE_WIN_CHANCE=0.47
ROULETTE_WIN_MULTIPLIER=2
```

## Step 4: Configure Discord OAuth

1. Go to https://discord.com/developers/applications
2. Select your application
3. Go to OAuth2 → Redirects
4. Add: `https://your-app.railway.app/api/auth/discord/callback`
5. Save changes

## Step 5: Deploy

Railway will automatically:
1. Install dependencies
2. Generate Prisma Client
3. Build Next.js
4. Push database schema
5. Start the application

## Step 6: Verify Deployment

1. Check Railway logs for errors
2. Visit your app URL
3. Test Discord OAuth login
4. Check database in Railway dashboard

## Troubleshooting

### Build fails

- Check Railway logs
- Verify all environment variables are set
- Ensure `DATABASE_URL` is present

### Database connection error

- Verify PostgreSQL service is running
- Check `DATABASE_URL` format
- Ensure Prisma schema is correct

### OAuth redirect error

- Verify `DISCORD_REDIRECT_URI` matches exactly
- Check Discord application settings
- Ensure URL uses HTTPS in production

### App crashes on start

- Check for missing environment variables
- Verify `PORT` is not hardcoded
- Check Railway logs for specific errors

## Monitoring

- Railway provides automatic logs
- Monitor database usage in dashboard
- Set up alerts for errors

## Scaling

Railway automatically scales based on usage. For high traffic:
1. Upgrade to Pro plan
2. Enable autoscaling
3. Monitor performance metrics

## Database Migrations

To run migrations in production:

```bash
# In Railway dashboard, run command:
npx prisma migrate deploy
```

Or use Railway CLI:

```bash
railway run npx prisma migrate deploy
```

## Backup

Railway automatically backs up PostgreSQL databases. To create manual backup:

1. Go to PostgreSQL service
2. Click "Backups"
3. Create snapshot

## Support

- Railway Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- GitHub Issues: Your repository
