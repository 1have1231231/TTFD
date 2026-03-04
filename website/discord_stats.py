"""
Модуль для получения статистики Discord сервера
"""
import discord
from discord.ext import commands, tasks
import os
import json
from datetime import datetime

# ID сервера TTFD
GUILD_ID = 997135062682320956

# Файл для хранения статистики
STATS_FILE = 'discord_stats.json'

class StatsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.presences = True
        super().__init__(command_prefix="!", intents=intents)
    
    async def on_ready(self):
        print(f'✅ Stats Bot запущен: {self.user.name}')
        self.update_stats.start()
    
    @tasks.loop(minutes=1)
    async def update_stats(self):
        """Обновляет статистику каждую минуту"""
        try:
            guild = self.get_guild(GUILD_ID)
            if not guild:
                print(f"❌ Сервер {GUILD_ID} не найден")
                return
            
            # Подсчитываем онлайн участников
            online_count = sum(1 for member in guild.members 
                             if not member.bot and member.status != discord.Status.offline)
            
            total_count = sum(1 for member in guild.members if not member.bot)
            
            stats = {
                'online_members': online_count,
                'total_members': total_count,
                'last_update': datetime.now().isoformat()
            }
            
            # Сохраняем в файл
            with open(STATS_FILE, 'w') as f:
                json.dump(stats, f)
            
            print(f"📊 Статистика обновлена: {online_count}/{total_count} онлайн")
        except Exception as e:
            print(f"❌ Ошибка обновления статистики: {e}")
    
    @update_stats.before_loop
    async def before_update_stats(self):
        await self.wait_until_ready()

def get_stats():
    """Получить статистику из файла"""
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    
    return {
        'online_members': 0,
        'total_members': 0,
        'last_update': None
    }

if __name__ == '__main__':
    # Запуск бота для обновления статистики
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot = StatsBot()
        bot.run(token)
    else:
        print("❌ DISCORD_TOKEN не найден")
