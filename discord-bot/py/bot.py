# Discord Bot - Основной файл

import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import aiohttp
from datetime import datetime, timedelta
import random
import config
import os

# Автоматический выбор базы данных
database_url = os.getenv('DATABASE_URL')
print("═══════════════════════════════════════════════════════════════")
print("🔍 ПРОВЕРКА ПОДКЛЮЧЕНИЯ К БАЗЕ ДАННЫХ")
print("═══════════════════════════════════════════════════════════════")

if database_url:
    print(f"✅ DATABASE_URL найден")
    print(f"   Длина URL: {len(database_url)} символов")
    print(f"   Начинается с: {database_url[:20]}...")
    print("🔄 Попытка подключения к PostgreSQL...")
    try:
        from database_postgres import db
        print("✅ PostgreSQL подключен успешно!")
        print("✅ Данные будут сохраняться в PostgreSQL")
        print("═══════════════════════════════════════════════════════════════")
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL:")
        print(f"   {type(e).__name__}: {e}")
        print("⚠️ Переключение на JSON файл (данные будут теряться при деплое)")
        print("═══════════════════════════════════════════════════════════════")
        from database import db
else:
    print("❌ DATABASE_URL не найден в переменных окружения")
    print("⚠️ Используется JSON файл (данные будут теряться при деплое)")
    print("")
    print("💡 Чтобы подключить PostgreSQL:")
    print("   1. Railway → Postgres → Variables → DATABASE_URL (скопируй)")
    print("   2. Railway → TTFD (бот) → Variables → + New Variable")
    print("   3. Name: DATABASE_URL, Value: вставь скопированный URL")
    print("   4. Settings → Restart")
    print("═══════════════════════════════════════════════════════════════")
    from database import db
import tickets_system
import verification_system
from commands_manager import get_commands_text
from theme import BotTheme, game_embed, profile_embed, success_embed, error_embed, warning_embed
# import shop_system  # Магазин отключен
import commands_channel
import updates_system
import voice_tracking
import rank_roles
import game_integration
import slash_commands
import views
import chatgpt_system
import private_channels_system

print("✅ Используется JSON база данных")

# Настройка intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.presences = True

# Создание бота
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Статистика бота
bot.stats = {
    'start_time': None,
    'commands_used': 0,
    'messages_seen': 0,
}

# ID канала для списка команд
COMMANDS_CHANNEL_ID = 1466295322002067607

# Файл для хранения ID сообщения со списком команд
COMMANDS_MESSAGE_FILE = 'json/commands_message.json'

# ID сообщения со списком команд (будет загружено из файла)
COMMANDS_MESSAGE_ID = None

def load_commands_message_id():
    """Загрузить ID сообщения со списком команд из файла"""
    global COMMANDS_MESSAGE_ID
    try:
        import json
        import os
        if os.path.exists(COMMANDS_MESSAGE_FILE):
            with open(COMMANDS_MESSAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                COMMANDS_MESSAGE_ID = data.get('message_id')
                if COMMANDS_MESSAGE_ID:
                    print(f"📋 Загружен ID сообщения команд: {COMMANDS_MESSAGE_ID}")
    except Exception as e:
        print(f"⚠️ Не удалось загрузить ID сообщения: {e}")

def save_commands_message_id(message_id):
    """Сохранить ID сообщения со списком команд в файл"""
    global COMMANDS_MESSAGE_ID
    try:
        import json
        from datetime import datetime
        COMMANDS_MESSAGE_ID = message_id
        data = {
            'message_id': message_id,
            'channel_id': COMMANDS_CHANNEL_ID,
            'last_updated': datetime.now().isoformat()
        }
        with open(COMMANDS_MESSAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"💾 Сохранён ID сообщения команд: {message_id}")
    except Exception as e:
        print(f"⚠️ Не удалось сохранить ID сообщения: {e}")

# ID канала для уведомлений об обновлениях (ОТКЛЮЧЕНО)
# UPDATES_CHANNEL_ID = 1466923990936326294
UPDATES_CHANNEL_ID = None  # Отключено

# ID роли администратора
ADMIN_ROLE_ID = 1466282400219922536


# ==================== Вспомогательные функции ====================

def is_admin(ctx):
    """Проверить является ли пользователь администратором"""
    admin_role = ctx.guild.get_role(ADMIN_ROLE_ID)
    return admin_role in ctx.author.roles if admin_role else False

def create_progress_bar(current, total, length=10):
    """Создать прогресс-бар"""
    filled = int((current / total) * length) if total > 0 else 0
    bar = "█" * filled + "░" * (length - filled)
    percentage = int((current / total) * 100) if total > 0 else 0
    return f"{bar} {percentage}%"

def get_next_rank_info(user):
    """Получить информацию о следующем ранге"""
    current_rank = db.get_rank_info(user['rank_id'])
    all_ranks = db.get_all_ranks()
    
    if user['rank_id'] < len(all_ranks):
        next_rank = all_ranks[user['rank_id']]
        xp_needed = next_rank['required_xp'] - user['xp']
        progress = user['xp'] - current_rank['required_xp']
        total_needed = next_rank['required_xp'] - current_rank['required_xp']
        return {
            'next_rank': next_rank,
            'xp_needed': xp_needed,
            'progress_bar': create_progress_bar(progress, total_needed)
        }
    return None

def get_daily_streak(user):
    """Получить серию ежедневных входов"""
    if 'daily_streak' not in user:
        user['daily_streak'] = 0
        user['last_daily_date'] = None
    return user['daily_streak']

def update_daily_streak(user):
    """Обновить серию ежедневных входов"""
    if 'last_daily_date' not in user or user['last_daily_date'] is None:
        user['daily_streak'] = 1
        user['last_daily_date'] = datetime.now().date().isoformat()
        return 1
    
    last_date = datetime.fromisoformat(user['last_daily_date']).date()
    today = datetime.now().date()
    days_diff = (today - last_date).days
    
    if days_diff == 1:
        # Продолжаем серию
        user['daily_streak'] = user.get('daily_streak', 0) + 1
    elif days_diff > 1:
        # Серия прервана
        user['daily_streak'] = 1
    else:
        # Уже получено сегодня
        return user.get('daily_streak', 1)
    
    user['last_daily_date'] = today.isoformat()
    return user['daily_streak']

async def handle_rank_up(ctx, user, old_xp):
    """
    Обработать повышение ранга с выдачей роли
    
    Args:
        ctx: Discord Context
        user: Данные пользователя
        old_xp: Старое количество XP
    
    Returns:
        bool: True если была выдана новая роль
    """
    new_xp = user.get('xp', 0)
    
    # Определяем старую и новую роль по XP
    old_tier = rank_roles.get_role_for_xp(old_xp)
    new_tier = rank_roles.get_role_for_xp(new_xp)
    
    # Проверяем, изменилась ли роль
    if old_tier != new_tier and new_tier:
        # Выдаём новую роль
        try:
            result = await rank_roles.update_user_rank_role(ctx.author, new_xp)
            
            if result['success'] and result['action'] == 'added':
                # Отправляем уведомление с информацией о роли
                await rank_roles.send_rank_up_notification(
                    ctx,
                    ctx.author,
                    old_xp,
                    new_xp,
                    old_tier,
                    new_tier,
                    result.get('role')
                )
                return True
        except Exception as e:
            print(f"❌ Ошибка выдачи роли: {e}")
    
    return False


# ==================== События бота ====================

@bot.event
async def on_ready():
    """Событие запуска бота"""
    bot.stats['start_time'] = datetime.now()
    
    # Загружаем ID сообщения со списком команд
    load_commands_message_id()
    
    print("=" * 50)
    print(f"✅ Бот успешно запущен!")
    print(f"📛 Имя: {bot.user.name}#{bot.user.discriminator}")
    print(f"🆔 ID: {bot.user.id}")
    print(f"🌐 Серверов: {len(bot.guilds)}")
    print(f"👥 Пользователей: {len(bot.users)}")
    print("=" * 50)
    
    # Регистрация slash команд
    print("🔄 Регистрация slash команд...")
    try:
        await slash_commands.setup_slash_commands(bot, db)
        print("✅ Slash команды зарегистрированы")
    except Exception as e:
        print(f"❌ Ошибка регистрации slash команд: {e}")
        import traceback
        traceback.print_exc()
    
    # Настройка интеграции с игрой
    print("🎮 Настройка интеграции с TTFD Game...")
    try:
        global game_int
        game_int = game_integration.GameIntegration(db)
        game_integration.setup_game_commands(bot, db, game_int)
        print("✅ Интеграция с игрой настроена")
    except Exception as e:
        print(f"❌ Ошибка настройки интеграции с игрой: {e}")
        import traceback
        traceback.print_exc()
    
    # Инициализация системы отслеживания войса
    print("🎤 Инициализация системы отслеживания войса...")
    try:
        voice_tracking.init_voice_tracking(bot, db)
        print("✅ Система отслеживания войса инициализирована")
    except Exception as e:
        print(f"❌ Ошибка инициализации войса: {e}")
        import traceback
        traceback.print_exc()
    
    # Настройка ChatGPT (ПЕРЕД синхронизацией команд!)
    print("🤖 Настройка ChatGPT...")
    try:
        await chatgpt_system.setup_chatgpt_commands(bot)
        print(f"✅ ChatGPT настроен (канал: {chatgpt_system.CHATGPT_CHANNEL_ID})")
    except Exception as e:
        print(f"❌ Ошибка настройки ChatGPT: {e}")
        import traceback
        traceback.print_exc()
    
    # Настройка приватных каналов
    try:
        await private_channels_system.setup_private_channels(bot)
        print("✅ Система приватных каналов настроена")
    except Exception as e:
        print(f"❌ Ошибка настройки приватных каналов: {e}")
        import traceback
        traceback.print_exc()
    
    # Синхронизация ВСЕХ slash команд с Discord (ВАЖНО: в самом конце после всех регистраций!)
    print("🔄 Синхронизация slash команд с Discord...")
    try:
        # Используем GLOBAL sync для всех команд (работает везде, но обновляется до 1 часа)
        synced = await bot.tree.sync()
        print(f"✅ Синхронизировано {len(synced)} slash команд с Discord (global sync)")
        print("⏰ Команды появятся в течение 1 часа")
        
        # Также синхронизируем с guild для мгновенного появления на сервере
        try:
            guild = discord.Object(id=config.GUILD_ID)
            synced_guild = await bot.tree.sync(guild=guild)
            print(f"✅ Синхронизировано {len(synced_guild)} slash команд с guild (мгновенно)")
        except Exception as guild_error:
            print(f"⚠️ Guild sync не удался (команды всё равно появятся через global sync): {guild_error}")
    except Exception as e:
        print(f"❌ Ошибка синхронизации команд: {e}")
        import traceback
        traceback.print_exc()
    
    # Настройка системы верификации
    print("🔄 Настройка системы верификации...")
    try:
        await verification_system.setup_verification(bot)
    except Exception as e:
        print(f"❌ Ошибка настройки верификации: {e}")
        import traceback
        traceback.print_exc()
    
    # Настройка кнопки тикетов
    print("🔄 Настройка кнопки тикетов...")
    try:
        await tickets_system.setup_ticket_button(bot)
    except Exception as e:
        print(f"❌ Ошибка настройки кнопки тикетов: {e}")
        import traceback
        traceback.print_exc()
    
    # Проверка автообновления
    print("🔄 Проверка автообновления...")
    try:
        await updates_system.check_auto_update(bot)
    except Exception as e:
        print(f"❌ Ошибка проверки автообновления: {e}")
        import traceback
        traceback.print_exc()
    
    # Запуск фоновых задач
    if not update_bot_status.is_running():
        update_bot_status.start()

@bot.event
async def on_command(ctx):
    """Событие использования команды"""
    bot.stats['commands_used'] += 1
    
    # Если команда выполнена в канале команд, удаляем ответ бота через 5 минут
    if commands_channel.is_commands_channel(ctx.channel.id):
        # Ждём ответа бота и удаляем его через 5 минут
        async def delete_bot_response():
            await asyncio.sleep(1)  # Ждём пока бот ответит
            async for msg in ctx.channel.history(limit=10):
                if msg.author == bot.user and msg.created_at > ctx.message.created_at:
                    asyncio.create_task(delete_message_after(msg, 300))
                    break
        
        asyncio.create_task(delete_bot_response())

async def delete_message_after(message, delay):
    """Удалить сообщение через указанное время"""
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except:
        pass

@bot.event
async def on_raw_reaction_add(payload):
    """Обработка добавления реакции"""
    await verification_system.handle_verification_reaction(bot, payload)

@bot.event
async def on_raw_reaction_remove(payload):
    """Обработка удаления реакции"""
    await verification_system.handle_verification_reaction_remove(bot, payload)

@bot.event
async def on_voice_state_update(member, before, after):
    """Обработка изменения голосового состояния"""
    await voice_tracking.on_voice_state_update(member, before, after)

@bot.event
async def on_member_update(before, after):
    """Обработка изменения данных участника (роли, ник и т.д.)"""
    # Проверяем изменение ролей для системы приватных каналов
    if before.roles != after.roles:
        await private_channels_system.on_member_update_role(before, after, bot)


# ==================== Фоновые задачи ====================

@tasks.loop(minutes=5)
async def update_bot_status():
    """Обновление статуса бота"""
    statuses = [
        discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} серверов"),
        discord.Activity(type=discord.ActivityType.playing, name="/help для помощи"),
        discord.Activity(type=discord.ActivityType.listening, name="ваши команды"),
    ]
    await bot.change_presence(activity=random.choice(statuses))


# ==================== Обновление списка команд ====================

def get_all_commands_list():
    """Получить список всех команд бота с описаниями"""
    from commands_manager import get_all_commands
    return get_all_commands()

async def update_commands_list():
    """Обновить список команд в канале"""
    global COMMANDS_MESSAGE_ID
    
    print(f"📝 Начало обновления списка команд (канал ID: {COMMANDS_CHANNEL_ID})...")
    
    try:
        channel = bot.get_channel(COMMANDS_CHANNEL_ID)
        if not channel:
            print(f"⚠️ Канал команд не найден (ID: {COMMANDS_CHANNEL_ID})")
            return
        
        print(f"✅ Канал найден: {channel.name}")
        
        # Получаем отформатированный текст команд
        print("📄 Генерация текста команд...")
        text = get_commands_text()
        print(f"✅ Текст сгенерирован ({len(text)} символов)")
        
        # Если сообщение уже существует - обновляем его
        if COMMANDS_MESSAGE_ID:
            try:
                message = await channel.fetch_message(COMMANDS_MESSAGE_ID)
                await message.edit(content=text)
                print(f"✅ Список команд обновлён (Message ID: {COMMANDS_MESSAGE_ID})")
                return
            except discord.NotFound:
                print("⚠️ Старое сообщение не найдено, создаю новое")
                COMMANDS_MESSAGE_ID = None
            except Exception as e:
                print(f"❌ Ошибка редактирования сообщения: {e}")
        
        # Если сообщения нет - создаём новое
        # Удаляем старые сообщения бота в канале
        try:
            async for message in channel.history(limit=100):
                if message.author == bot.user:
                    await message.delete()
                    await asyncio.sleep(0.5)
        except Exception as e:
            print(f"⚠️ Не удалось очистить старые сообщения: {e}")
        
        # Создаём новое сообщение
        message = await channel.send(text)
        save_commands_message_id(message.id)
        print(f"✅ Список команд создан (Message ID: {message.id})")
        
    except Exception as e:
        print(f"❌ Ошибка обновления списка команд: {e}")
        import traceback
        traceback.print_exc()


# ==================== Команды ====================

# ==================== Команды для администраторов ====================

@bot.command(name='updatecommands')
async def update_commands_manual(ctx):
    """
    Обновить список команд в канале вручную
    """
    if not is_admin(ctx):
        await ctx.send(convert_to_font("❌ у тебя нет прав для использования этой команды!"))
        return
    
    try:
        await update_commands_list()
        await ctx.send(convert_to_font("✅ список команд обновлён!"))
    except Exception as e:
        await ctx.send(convert_to_font(f"❌ ошибка: {e}"))

@bot.command(name='setupverification')
async def setup_verification_manual(ctx):
    """
    Настроить систему верификации вручную
    """
    if not is_admin(ctx):
        await ctx.send(convert_to_font("❌ у тебя нет прав для использования этой команды!"))
        return
    
    try:
        success = await verification_system.setup_verification(bot)
        if success:
            await ctx.send(convert_to_font("✅ система верификации настроена!"))
        else:
            await ctx.send(convert_to_font("❌ не удалось настроить верификацию"))
    except Exception as e:
        await ctx.send(convert_to_font(f"❌ ошибка: {e}"))

@bot.command(name='setuptickets')
async def setup_tickets_manual(ctx):
    """
    Настроить кнопку тикетов вручную
    """
    if not is_admin(ctx):
        await ctx.send(convert_to_font("❌ у тебя нет прав для использования этой команды!"))
        return
    
    try:
        success = await tickets_system.setup_ticket_button(bot)
        if success:
            await ctx.send(convert_to_font("✅ кнопка тикетов настроена!"))
        else:
            await ctx.send(convert_to_font("❌ не удалось настроить кнопку"))
    except Exception as e:
        await ctx.send(convert_to_font(f"❌ ошибка: {e}"))

@bot.command(name='setuprankroles')
async def setup_rank_roles(ctx, tier: str = None, role: discord.Role = None):
    """
    Настроить роли для рангов
    Использование: !setuprankroles [F/E/D/C/B/A/S] [@роль]
    Без параметров - показать текущие настройки
    """
    if not is_admin(ctx):
        await ctx.send(convert_to_font("❌ у тебя нет прав для использования этой команды!"))
        return
    
    if not tier and not role:
        # Показать текущие настройки
        config = rank_roles.get_rank_roles_config()
        
        embed = BotTheme.create_embed(
            title=convert_to_font("⚙️ настройка ролей рангов"),
            description=convert_to_font("текущие настройки ролей для каждого ранга"),
            embed_type='info'
        )
        
        for rank_tier in ['F', 'E', 'D', 'C', 'B', 'A', 'S']:
            role_data = config.get(rank_tier, {})
            role_id = role_data.get('role_id') if isinstance(role_data, dict) else role_data
            
            if role_id:
                role_obj = ctx.guild.get_role(role_id)
                if role_obj:
                    required_xp = role_data.get('required_xp', 0) if isinstance(role_data, dict) else 0
                    embed.add_field(
                        name=convert_to_font(f"ранг {rank_tier}"),
                        value=f"{role_obj.mention} ({required_xp} xp)",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name=convert_to_font(f"ранг {rank_tier}"),
                        value=convert_to_font(f"роль не найдена (id: {role_id})"),
                        inline=True
                    )
            else:
                embed.add_field(
                    name=convert_to_font(f"ранг {rank_tier}"),
                    value=convert_to_font("не настроено"),
                    inline=True
                )
        
        embed.add_field(
            name=convert_to_font("📝 как настроить"),
            value=convert_to_font("!setuprankroles [F/E/D/C/B/A/S] [@роль]"),
            inline=False
        )
        
        await ctx.send(embed=embed)
        return
    
    if not tier or not role:
        await ctx.send(convert_to_font("❌ использование: !setuprankroles [F/E/D/C/B/A/S] [@роль]"))
        return
    
    tier = tier.upper()
    
    if tier not in ['F', 'E', 'D', 'C', 'B', 'A', 'S']:
        await ctx.send(convert_to_font("❌ ранг должен быть F, E, D, C, B, A или S"))
        return
    
    # Устанавливаем роль
    success = rank_roles.set_rank_role(tier, role.id)
    
    if success:
        embed = BotTheme.create_embed(
            title=convert_to_font("✅ роль настроена!"),
            embed_type='success'
        )
        embed.add_field(
            name=convert_to_font(f"ранг {tier}"),
            value=role.mention,
            inline=True
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send(convert_to_font("❌ ошибка настройки роли"))

@bot.command(name='syncrankroles')
async def sync_rank_roles(ctx):
    """
    Синхронизировать роли всех пользователей с их рангами
    Полезно при первом запуске или после изменения настроек
    """
    if not is_admin(ctx):
        await ctx.send(convert_to_font("❌ у тебя нет прав для использования этой команды!"))
        return
    
    await ctx.send(convert_to_font("🔄 начинаю синхронизацию ролей..."))
    
    try:
        stats = await rank_roles.sync_all_user_roles(bot, db)
        
        embed = BotTheme.create_embed(
            title=convert_to_font("✅ синхронизация завершена!"),
            embed_type='success'
        )
        embed.add_field(
            name=convert_to_font("всего пользователей"),
            value=convert_to_font(str(stats['total'])),
            inline=True
        )
        embed.add_field(
            name=convert_to_font("обновлено"),
            value=convert_to_font(str(stats['updated'])),
            inline=True
        )
        embed.add_field(
            name=convert_to_font("пропущено"),
            value=convert_to_font(str(stats['skipped'])),
            inline=True
        )
        embed.add_field(
            name=convert_to_font("ошибок"),
            value=convert_to_font(str(stats['errors'])),
            inline=True
        )
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(convert_to_font(f"❌ ошибка синхронизации: {e}"))


# ==================== События для XP ====================

@bot.event
async def on_voice_state_update(member, before, after):
    """Обработка изменения голосового состояния с начислением XP"""
    # Игнорируем ботов
    if member.bot:
        return
    
    # Сохраняем старый XP перед начислением
    user = db.get_user(str(member.id))
    old_xp = user.get('xp', 0)
    
    # Передаём db в voice_tracking для начисления XP
    await voice_tracking.on_voice_state_update(member, before, after, db=db)
    
    # Проверяем выдачу роли только при выходе из войса
    if before.channel is not None and after.channel is None:
        # Пользователь вышел из войса - проверяем роль
        user = db.get_user(str(member.id))
        new_xp = user.get('xp', 0)
        
        if new_xp > old_xp:
            # XP изменился - проверяем роль
            # Создаём фейковый контекст
            class FakeContext:
                def __init__(self, member):
                    self.author = member
                    self.guild = member.guild
                    self.channel = None  # Нет канала для войса
                
                async def send(self, *args, **kwargs):
                    # Отправляем в первый текстовый канал
                    if self.guild:
                        for channel in self.guild.text_channels:
                            try:
                                return await channel.send(*args, **kwargs)
                            except:
                                continue
                    return None
            
            fake_ctx = FakeContext(member)


@bot.event
async def on_message(message):
    """Обработка сообщений с начислением XP"""
    # Игнорируем ботов
    if message.author.bot:
        return
    
    bot.stats['messages_seen'] += 1
    
    # Проверяем канал ChatGPT (обрабатываем ДО команд)
    if chatgpt_system.is_chatgpt_channel(message.channel.id):
        await chatgpt_system.on_message_chatgpt(message, bot)
        return  # Не обрабатываем как обычное сообщение
    
    # Обычное сообщение - начисляем XP
    if voice_tracking.can_earn_message_xp(message.author.id):
        # Рассчитываем XP за сообщение
        xp_reward = voice_tracking.calculate_message_xp(len(message.content))
        
        if xp_reward > 0:
            user = db.get_user(str(message.author.id))
            old_xp = user.get('xp', 0)
            user['xp'] = old_xp + xp_reward
            db.check_rank_up(user)
            db.save_user(str(message.author.id), user)
            
            # Проверяем и обрабатываем повышение роли
            # Создаём фейковый контекст для handle_rank_up
            class FakeContext:
                def __init__(self, message):
                    self.message = message
                    self.author = message.author
                    self.channel = message.channel
                    self.guild = message.guild
                
                async def send(self, *args, **kwargs):
                    return await self.channel.send(*args, **kwargs)
            
            fake_ctx = FakeContext(message)
            await handle_rank_up(fake_ctx, user, old_xp)
            
            # Логируем
            print(f"💬 {message.author.name} получил {xp_reward} XP за сообщение ({len(message.content)} символов)")
    
    await bot.process_commands(message)


# ==================== Запуск бота ====================

if __name__ == "__main__":
    try:
        bot.run(config.DISCORD_TOKEN)
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
