# Система приватных каналов для пользователей

import discord
from discord.ext import commands
import json
import os

# ID категории для приватных каналов
PRIVATE_CATEGORY_ID = 1478495227416281353

# ID роли для доступа к приватным каналам
REQUIRED_ROLE_ID = 1478495671727161515

# Файл для хранения маппинга пользователь -> канал
PRIVATE_CHANNELS_FILE = 'json/private_channels.json'

# Кэш приватных каналов {user_id: channel_id}
private_channels_cache = {}


def load_private_channels():
    """Загрузить маппинг приватных каналов"""
    global private_channels_cache
    try:
        if os.path.exists(PRIVATE_CHANNELS_FILE):
            with open(PRIVATE_CHANNELS_FILE, 'r', encoding='utf-8') as f:
                private_channels_cache = json.load(f)
                print(f"📂 Загружено {len(private_channels_cache)} приватных каналов")
    except Exception as e:
        print(f"⚠️ Ошибка загрузки приватных каналов: {e}")
        private_channels_cache = {}


def save_private_channels():
    """Сохранить маппинг приватных каналов"""
    try:
        os.makedirs('json', exist_ok=True)
        with open(PRIVATE_CHANNELS_FILE, 'w', encoding='utf-8') as f:
            json.dump(private_channels_cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Ошибка сохранения приватных каналов: {e}")


def has_required_role(member):
    """Проверить есть ли у пользователя нужная роль"""
    return any(role.id == REQUIRED_ROLE_ID for role in member.roles)


async def create_private_channel(member, category):
    """
    Создать приватный канал для пользователя
    
    Args:
        member: Discord Member
        category: Discord CategoryChannel
    
    Returns:
        discord.TextChannel или None
    """
    try:
        # Проверяем роль
        if not has_required_role(member):
            print(f"⚠️ У {member.name} нет нужной роли для приватного канала")
            return None
        
        # Создаём канал с именем пользователя
        channel_name = member.name.lower().replace(' ', '-')
        
        # Настройки прав доступа
        overwrites = {
            member.guild.default_role: discord.PermissionOverwrite(read_messages=False),  # Все не видят
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),  # Пользователь видит
            member.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)  # Бот видит
        }
        
        # Создаём канал
        channel = await category.create_text_channel(
            name=channel_name,
            overwrites=overwrites,
            topic=f"Приватный канал {member.name}"
        )
        
        # Сохраняем в кэш
        private_channels_cache[str(member.id)] = channel.id
        save_private_channels()
        
        print(f"✅ Создан приватный канал для {member.name}: #{channel.name}")
        
        # Отправляем приветственное сообщение
        embed = discord.Embed(
            title=f"👋 Добро пожаловать, {member.name}!",
            description=(
                "Это твой личный приватный канал.\n\n"
                "🔒 Только ты и бот можете видеть этот канал.\n"
                "💬 Здесь ты можешь общаться с ботом и использовать команды.\n"
                "🤖 Попробуй написать что-нибудь - бот ответит через ChatGPT!"
            ),
            color=discord.Color.blue()
        )
        await channel.send(embed=embed)
        
        return channel
    
    except Exception as e:
        print(f"❌ Ошибка создания приватного канала для {member.name}: {e}")
        return None


async def get_or_create_private_channel(member, bot):
    """
    Получить существующий или создать новый приватный канал
    
    Args:
        member: Discord Member
        bot: Discord Bot
    
    Returns:
        discord.TextChannel или None
    """
    # Проверяем роль
    if not has_required_role(member):
        return None
    
    # Проверяем есть ли уже канал
    user_id = str(member.id)
    if user_id in private_channels_cache:
        channel_id = private_channels_cache[user_id]
        channel = bot.get_channel(channel_id)
        
        if channel:
            return channel
        else:
            # Канал был удалён, убираем из кэша
            del private_channels_cache[user_id]
            save_private_channels()
    
    # Создаём новый канал
    category = bot.get_channel(PRIVATE_CATEGORY_ID)
    if not category:
        print(f"❌ Категория {PRIVATE_CATEGORY_ID} не найдена")
        return None
    
    return await create_private_channel(member, category)


async def setup_private_channels(bot):
    """Настроить систему приватных каналов при запуске бота"""
    print("🔐 Настройка системы приватных каналов...")
    
    # Загружаем кэш
    load_private_channels()
    
    # Получаем категорию
    category = bot.get_channel(PRIVATE_CATEGORY_ID)
    if not category:
        print(f"❌ Категория приватных каналов не найдена (ID: {PRIVATE_CATEGORY_ID})")
        return
    
    print(f"✅ Категория найдена: {category.name}")
    
    # Проходим по всем серверам и создаём каналы для пользователей с ролью
    created_count = 0
    for guild in bot.guilds:
        for member in guild.members:
            if member.bot:
                continue
            
            # Проверяем роль
            if not has_required_role(member):
                continue
            
            # Проверяем есть ли уже канал
            user_id = str(member.id)
            if user_id in private_channels_cache:
                channel_id = private_channels_cache[user_id]
                channel = bot.get_channel(channel_id)
                if channel:
                    continue  # Канал уже существует
                else:
                    # Канал был удалён
                    del private_channels_cache[user_id]
            
            # Создаём канал
            channel = await create_private_channel(member, category)
            if channel:
                created_count += 1
    
    if created_count > 0:
        print(f"✅ Создано {created_count} новых приватных каналов")
    
    save_private_channels()


async def on_member_update_role(before, after, bot):
    """
    Обработка изменения ролей пользователя
    Создаёт приватный канал если пользователь получил нужную роль
    """
    # Проверяем получил ли пользователь нужную роль
    had_role = any(role.id == REQUIRED_ROLE_ID for role in before.roles)
    has_role = any(role.id == REQUIRED_ROLE_ID for role in after.roles)
    
    # Если получил роль - создаём канал
    if not had_role and has_role:
        print(f"🎉 {after.name} получил роль для приватного канала")
        channel = await get_or_create_private_channel(after, bot)
        if channel:
            # Уведомляем пользователя
            try:
                embed = discord.Embed(
                    title="🎉 Приватный канал создан!",
                    description=f"Для тебя создан приватный канал: {channel.mention}",
                    color=discord.Color.green()
                )
                await after.send(embed=embed)
            except:
                pass  # Не можем отправить ЛС
    
    # Если потерял роль - удаляем канал
    elif had_role and not has_role:
        print(f"⚠️ {after.name} потерял роль для приватного канала")
        user_id = str(after.id)
        if user_id in private_channels_cache:
            channel_id = private_channels_cache[user_id]
            channel = bot.get_channel(channel_id)
            if channel:
                try:
                    await channel.delete(reason="Пользователь потерял роль")
                    print(f"🗑️ Удалён приватный канал {channel.name}")
                except Exception as e:
                    print(f"❌ Ошибка удаления канала: {e}")
            
            del private_channels_cache[user_id]
            save_private_channels()


def is_private_channel(channel_id):
    """Проверить является ли канал приватным каналом пользователя"""
    return channel_id in private_channels_cache.values()


def get_channel_owner(channel_id):
    """Получить ID владельца приватного канала"""
    for user_id, ch_id in private_channels_cache.items():
        if ch_id == channel_id:
            return user_id
    return None
