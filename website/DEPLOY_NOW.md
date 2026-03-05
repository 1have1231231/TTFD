# 🚀 Deploy to Railway NOW

## ✅ Code is on GitHub!

Repository: https://github.com/1have1231231/TTFD

## Step-by-Step Railway Deployment

### 1. Create Railway Project

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select: `1have1231231/TTFD`
4. **IMPORTANT**: Set root directory to `website`

### 2. Add PostgreSQL Database

1. In Railway project, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Wait for database to provision
4. `DATABASE_URL` will be automatically set

### 3. Configure Environment Variables

Click on your service → "Variables" → Add these:

```env
# Discord OAuth (GET FROM https://discord.com/developers/applications)
DISCORD_CLIENT_ID=your_client_id_here
DISCORD_CLIENT_SECRET=your_client_secret_here
DISCORD_REDIRECT_URI=https://your-app.up.railway.app/api/auth/discord/callback
DISCORD_GUILD_ID=your_discord_server_id
DISCORD_BOT_TOKEN=your_bot_token

# Security (GENERATE RANDOM STRINGS)
JWT_SECRET=random_string_32_chars_minimum
SESSION_SECRET=another_random_string_32_chars

# App URL (WILL BE PROVIDED BY RAILWAY)
NEXT_PUBLIC_APP_URL=https://your-app.up.railway.app

# Environment
NODE_ENV=production

# Optional - Admin Discord IDs (comma-separated)
ADMIN_DISCORD_IDS=your_discord_id,another_admin_id

# Optional - Roulette Settings
ROULETTE_MIN_BET=10
ROULETTE_MAX_BET=100000
ROULETTE_WIN_CHANCE=0.47
ROULETTE_WIN_MULTIPLIER=2
```

### 4. Update Discord OAuth Redirect

1. Go to https://discord.com/developers/applications
2. Select your application
3. OAuth2 → Redirects
4. Add: `https://your-app.up.railway.app/api/auth/discord/callback`
5. **Replace `your-app` with your actual Railway domain**
6. Save

### 5. Deploy!

Railway will automatically:
- ✅ Install dependencies
- ✅ Generate Prisma Client
- ✅ Build Next.js
- ✅ Create database tables
- ✅ Start application

### 6. Get Your URL

1. In Railway, click on your service
2. Go to "Settings" → "Networking"
3. Click "Generate Domain"
4. Copy your URL (e.g., `your-app.up.railway.app`)

### 7. Update Environment Variables

Go back to Variables and update:
- `DISCORD_REDIRECT_URI` with your Railway URL
- `NEXT_PUBLIC_APP_URL` with your Railway URL

### 8. Redeploy

Railway will automatically redeploy after variable changes.

## ✅ Verification Checklist

- [ ] Railway build succeeded
- [ ] PostgreSQL database is running
- [ ] All environment variables are set
- [ ] Discord OAuth redirect is configured
- [ ] App URL is accessible
- [ ] Can login with Discord
- [ ] TOP-3 XP shows on homepage
- [ ] Cabinet page loads after login

## 🐛 Troubleshooting

### Build Failed

Check Railway logs:
- Missing environment variables?
- Database connection issue?
- Syntax errors?

### Can't Login

- Verify `DISCORD_CLIENT_ID` and `DISCORD_CLIENT_SECRET`
- Check redirect URI matches exactly (including https://)
- Ensure Discord app has correct redirect configured

### Database Error

- Verify PostgreSQL service is running
- Check `DATABASE_URL` is set
- Try redeploying

### 500 Error

- Check Railway logs for specific error
- Verify all required env variables are set
- Check JWT_SECRET is set

## 📊 What's Deployed

- ✅ Next.js 14 with App Router
- ✅ PostgreSQL database with Prisma
- ✅ Discord OAuth2 authentication
- ✅ TOP-3 XP leaderboard
- ✅ User profiles with balance
- ✅ Roulette game (API ready)
- ✅ Transaction logging
- ✅ Rate limiting
- ✅ Elite Minimal UI

## 🎮 Next Steps After Deployment

1. Test Discord login
2. Check TOP-3 XP display
3. Create roulette UI page
4. Setup Discord bot (separate deployment)
5. Add more features

## 📝 Important Notes

- Railway provides free tier with limits
- Database is automatically backed up
- Logs are available in Railway dashboard
- Can scale up anytime

## 🆘 Need Help?

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Check logs in Railway dashboard
