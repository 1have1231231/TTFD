# Настройка интеграции статистики Discord → Сайт

## Проблема
Discord бот и сайт работают на разных Railway сервисах и не могут обмениваться файлами.

## Решение
Discord бот запускает HTTP API сервер на порту 8080, который отдаёт статистику.
Сайт получает данные с этого API.

## Настройка на Railway

### 1. Discord Bot (TTFD)

1. Перейди в настройки сервиса Discord бота
2. Settings → Networking → Public Networking
3. Включи "Generate Domain" если ещё не включено
4. Скопируй URL (например: `ttfd-production.up.railway.app`)
5. Variables → Add Variable:
   - Name: `STATS_API_PORT`
   - Value: `8080`

### 2. Website (TTFD-Website)

1. Перейди в настройки сервиса сайта
2. Variables → Add Variable:
   - Name: `DISCORD_BOT_API_URL`
   - Value: `https://ttfd-production.up.railway.app` (URL из шага 1)

### 3. Деплой

1. Закоммить изменения в Git
2. Push в GitHub
3. Railway автоматически задеплоит оба сервиса
4. Подожди 2-3 минуты пока боты запустятся

### 4. Проверка

1. Открой сайт
2. Открой консоль браузера (F12)
3. Должны появиться логи:
   ```
   🔄 Загрузка статистики...
   📡 Ответ получен: 200
   📊 Данные: {online_members: X, total_members: Y, ...}
   ✅ Статистика обновлена успешно
   ```

## Локальная разработка

### Discord Bot
```bash
cd TTFD/discord-bot
python py/bot.py
```
API будет доступен на `http://localhost:8080/api/stats`

### Website
```bash
cd TTFD/website
# Создай .env файл
echo "DISCORD_BOT_API_URL=http://localhost:8080" > .env
python app.py
```
Сайт будет доступен на `http://localhost:5000`

## Troubleshooting

### Сайт показывает 0 онлайн
- Проверь что Discord бот запущен
- Проверь что переменная `DISCORD_BOT_API_URL` правильная
- Открой `https://your-bot-url.railway.app/api/stats` в браузере - должен вернуть JSON

### Карточки игроков не загружаются
- Открой консоль браузера (F12)
- Проверь есть ли ошибки
- Проверь что API возвращает `top_players` массив

### API не отвечает
- Проверь логи Discord бота на Railway
- Должна быть строка: `✅ Stats API запущен на порту 8080`
- Проверь что порт 8080 открыт в настройках Railway
