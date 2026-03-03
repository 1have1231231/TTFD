# Конфигурация проекта
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла (для локальной разработки)
# На Render переменные берутся напрямую из Environment Variables
load_dotenv()

# Discord настройки
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID_STR = os.getenv('GUILD_ID', '0')

# Безопасное преобразование GUILD_ID
try:
    GUILD_ID = int(GUILD_ID_STR) if GUILD_ID_STR.isdigit() else 0
except (ValueError, AttributeError):
    GUILD_ID = 0

# Веб-сервер настройки
# На Railway/Render используется переменная PORT, на локалке - WEB_PORT
PORT = os.getenv('PORT')  # Railway/Render автоматически устанавливает PORT
WEB_PORT = int(PORT) if PORT else int(os.getenv('WEB_PORT', 5000))
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Discord OAuth настройки
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
# Автоматически определяем URL для Railway
RAILWAY_PUBLIC_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN')
RAILWAY_STATIC_URL = os.getenv('RAILWAY_STATIC_URL')
if RAILWAY_PUBLIC_DOMAIN:
    default_redirect = f'https://{RAILWAY_PUBLIC_DOMAIN}/auth/discord/callback'
elif RAILWAY_STATIC_URL:
    default_redirect = f'{RAILWAY_STATIC_URL}/auth/discord/callback'
else:
    default_redirect = 'http://localhost:5000/auth/discord/callback'
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', default_redirect)

# Проверка обязательных настроек
if not DISCORD_TOKEN:
    print("❌ DISCORD_TOKEN не установлен!")
    print("💡 Добавь переменные окружения в Render Dashboard:")
    print("   - DISCORD_TOKEN")
    print("   - GUILD_ID")
    print("   - SECRET_KEY")
    raise ValueError("DISCORD_TOKEN is required")

if GUILD_ID == 0:
    print("⚠️ GUILD_ID не установлен, некоторые функции могут не работать")

if not DISCORD_CLIENT_ID or not DISCORD_CLIENT_SECRET:
    print("⚠️ Discord OAuth не настроен (DISCORD_CLIENT_ID или DISCORD_CLIENT_SECRET отсутствуют)")
    print("💡 OAuth авторизация будет недоступна")
