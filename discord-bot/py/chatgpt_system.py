# Система ChatGPT для Discord бота

import discord
from discord.ext import commands
import aiohttp
import os
import json
from datetime import datetime, timedelta
from theme import BotTheme, error_embed
from font_converter import convert_to_font

# ID канала для ChatGPT
CHATGPT_CHANNEL_ID = 1466293572604264662

# API ключ OpenAI (из переменных окружения)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Хранилище истории диалогов {user_id: [messages]}
conversation_history = {}

# Максимальная длина истории (чтобы не превышать лимиты токенов)
MAX_HISTORY_LENGTH = 10

# Кулдаун между запросами (секунды)
COOLDOWN_SECONDS = 5

# Последние запросы {user_id: timestamp}
last_requests = {}

# Системный промпт для ChatGPT
SYSTEM_PROMPT = """Ты - дружелюбный помощник Discord бота TTFD. 
Отвечай кратко и по делу. Используй эмодзи для выразительности.
Ты помогаешь пользователям с вопросами об игре, сервере и общими вопросами.
Будь вежливым и полезным."""


def is_chatgpt_channel(channel_id):
    """Проверить является ли канал каналом ChatGPT"""
    return CHATGPT_CHANNEL_ID and channel_id == CHATGPT_CHANNEL_ID


def check_cooldown(user_id):
    """
    Проверить кулдаун пользователя
    
    Returns:
        tuple: (can_use: bool, time_left: int)
    """
    if user_id not in last_requests:
        return True, 0
    
    time_passed = (datetime.now() - last_requests[user_id]).total_seconds()
    
    if time_passed >= COOLDOWN_SECONDS:
        return True, 0
    
    time_left = int(COOLDOWN_SECONDS - time_passed)
    return False, time_left


def get_conversation_history(user_id):
    """Получить историю диалога пользователя"""
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    return conversation_history[user_id]


def add_to_history(user_id, role, content):
    """Добавить сообщение в историю"""
    history = get_conversation_history(user_id)
    history.append({"role": role, "content": content})
    
    # Ограничиваем длину истории
    if len(history) > MAX_HISTORY_LENGTH:
        # Оставляем системный промпт и последние N сообщений
        conversation_history[user_id] = history[-MAX_HISTORY_LENGTH:]


def clear_history(user_id):
    """Очистить историю диалога"""
    if user_id in conversation_history:
        conversation_history[user_id] = []


async def ask_chatgpt(user_id, question):
    """
    Отправить запрос к ChatGPT API
    
    Args:
        user_id: ID пользователя
        question: Вопрос пользователя
    
    Returns:
        dict: {'success': bool, 'response': str, 'error': str}
    """
    if not OPENAI_API_KEY:
        return {
            'success': False,
            'error': 'API ключ OpenAI не настроен. Добавь OPENAI_API_KEY в переменные окружения.'
        }
    
    # Получаем историю диалога
    history = get_conversation_history(user_id)
    
    # Формируем сообщения для API
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": question})
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',  # Можно изменить на gpt-4
                'messages': messages,
                'max_tokens': 500,
                'temperature': 0.7
            }
            
            async with session.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    answer = result['choices'][0]['message']['content']
                    
                    # Добавляем в историю
                    add_to_history(user_id, "user", question)
                    add_to_history(user_id, "assistant", answer)
                    
                    return {
                        'success': True,
                        'response': answer
                    }
                elif response.status == 401:
                    return {
                        'success': False,
                        'error': 'Неверный API ключ OpenAI'
                    }
                elif response.status == 429:
                    return {
                        'success': False,
                        'error': 'Превышен лимит запросов к OpenAI API'
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f'Ошибка API: {response.status} - {error_text}'
                    }
    
    except asyncio.TimeoutError:
        return {
            'success': False,
            'error': 'Превышено время ожидания ответа от ChatGPT'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Ошибка: {str(e)}'
        }


async def setup_chatgpt_commands(bot):
    """Настроить команды ChatGPT"""
    
    @bot.command(name='ask')
    async def ask_command(ctx, *, question: str = None):
        """Задать вопрос ChatGPT"""
        # Проверяем канал
        if not is_chatgpt_channel(ctx.channel.id):
            await ctx.send(
                convert_to_font(f"❌ эта команда работает только в канале <#{CHATGPT_CHANNEL_ID}>"),
                delete_after=5
            )
            return
        
        if not question:
            await ctx.send(
                convert_to_font("❌ укажи вопрос: !ask [твой вопрос]"),
                delete_after=5
            )
            return
        
        # Проверяем кулдаун
        can_use, time_left = check_cooldown(ctx.author.id)
        if not can_use:
            await ctx.send(
                convert_to_font(f"⏰ подожди {time_left} секунд перед следующим вопросом"),
                delete_after=5
            )
            return
        
        # Отправляем сообщение о загрузке
        async with ctx.typing():
            # Отправляем запрос к ChatGPT
            result = await ask_chatgpt(ctx.author.id, question)
            
            if result['success']:
                # Обновляем время последнего запроса
                last_requests[ctx.author.id] = datetime.now()
                
                # Создаём embed с ответом
                embed = BotTheme.create_embed(
                    title="🤖 ChatGPT",
                    description=result['response'],
                    embed_type='info'
                )
                embed.set_footer(text=f"Вопрос от {ctx.author.name}")
                
                await ctx.reply(embed=embed, mention_author=False)
            else:
                # Ошибка
                embed = error_embed(
                    title=convert_to_font("❌ ошибка"),
                    description=convert_to_font(result['error'])
                )
                await ctx.send(embed=embed)
    
    @bot.command(name='clear_chat')
    async def clear_chat_command(ctx):
        """Очистить историю диалога с ChatGPT"""
        if not is_chatgpt_channel(ctx.channel.id):
            await ctx.send(
                convert_to_font(f"❌ эта команда работает только в канале <#{CHATGPT_CHANNEL_ID}>"),
                delete_after=5
            )
            return
        
        clear_history(ctx.author.id)
        
        embed = BotTheme.create_embed(
            title="🗑️ История очищена",
            description=convert_to_font("твоя история диалога с ChatGPT очищена"),
            embed_type='success'
        )
        
        await ctx.send(embed=embed, delete_after=10)
    
    @bot.command(name='chatgpt_help')
    async def chatgpt_help_command(ctx):
        """Помощь по ChatGPT"""
        if not is_chatgpt_channel(ctx.channel.id):
            await ctx.send(
                convert_to_font(f"❌ эта команда работает только в канале <#{CHATGPT_CHANNEL_ID}>"),
                delete_after=5
            )
            return
        
        embed = BotTheme.create_embed(
            title="🤖 ChatGPT - Помощь",
            description="Как использовать ChatGPT в Discord",
            embed_type='info'
        )
        
        embed.add_field(
            name="📝 Команды",
            value=(
                "**!ask [вопрос]** - задать вопрос ChatGPT\n"
                "**!clear_chat** - очистить историю диалога\n"
                "**!chatgpt_help** - эта справка"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⏰ Ограничения",
            value=f"Кулдаун между вопросами: {COOLDOWN_SECONDS} секунд",
            inline=False
        )
        
        embed.add_field(
            name="💡 Советы",
            value=(
                "• Задавай конкретные вопросы\n"
                "• ChatGPT помнит последние 10 сообщений\n"
                "• Используй !clear_chat для начала нового диалога"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)


async def on_message_chatgpt(message, bot):
    """
    Обработка сообщений в канале ChatGPT
    Автоматически отвечает на сообщения без команды
    """
    # Игнорируем ботов
    if message.author.bot:
        return
    
    # Проверяем канал
    if not is_chatgpt_channel(message.channel.id):
        return
    
    # Игнорируем команды
    if message.content.startswith('!'):
        return
    
    # Проверяем кулдаун
    can_use, time_left = check_cooldown(message.author.id)
    if not can_use:
        await message.reply(
            convert_to_font(f"⏰ подожди {time_left} секунд"),
            delete_after=5,
            mention_author=False
        )
        return
    
    # Отправляем запрос к ChatGPT
    async with message.channel.typing():
        result = await ask_chatgpt(message.author.id, message.content)
        
        if result['success']:
            # Обновляем время последнего запроса
            last_requests[message.author.id] = datetime.now()
            
            # Создаём embed с ответом
            embed = BotTheme.create_embed(
                title="🤖 ChatGPT",
                description=result['response'],
                embed_type='info'
            )
            embed.set_footer(text=f"Вопрос от {message.author.name}")
            
            await message.reply(embed=embed, mention_author=False)
        else:
            # Ошибка
            embed = error_embed(
                title=convert_to_font("❌ ошибка"),
                description=convert_to_font(result['error'])
            )
            await message.channel.send(embed=embed)


def set_chatgpt_channel(channel_id):
    """Установить ID канала для ChatGPT"""
    global CHATGPT_CHANNEL_ID
    CHATGPT_CHANNEL_ID = channel_id
    print(f"✅ ChatGPT канал установлен: {channel_id}")
