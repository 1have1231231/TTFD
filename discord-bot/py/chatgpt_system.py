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
                        'error': 'Неверный API ключ OpenAI. Проверь переменную OPENAI_API_KEY в Railway.'
                    }
                elif response.status == 429:
                    error_data = await response.json()
                    error_message = error_data.get('error', {}).get('message', 'Превышен лимит запросов')
                    
                    # Проверяем тип ошибки
                    if 'quota' in error_message.lower() or 'insufficient' in error_message.lower():
                        return {
                            'success': False,
                            'error': '❌ Недостаточно средств на аккаунте OpenAI\n\n💡 Пополни баланс на https://platform.openai.com/account/billing'
                        }
                    else:
                        return {
                            'success': False,
                            'error': f'⏰ Превышен лимит запросов к OpenAI API\n\n{error_message}\n\n💡 Подожди немного и попробуй снова'
                        }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f'Ошибка API: {response.status}\n{error_text}'
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
    """Настроить slash команды ChatGPT"""
    
    @bot.tree.command(name="ask", description="Задать вопрос ChatGPT")
    @discord.app_commands.describe(question="Твой вопрос к ChatGPT")
    async def ask_slash(interaction: discord.Interaction, question: str):
        """Slash команда для вопроса ChatGPT"""
        # Проверяем канал
        if not is_chatgpt_channel(interaction.channel_id):
            await interaction.response.send_message(
                convert_to_font(f"❌ эта команда работает только в канале <#{CHATGPT_CHANNEL_ID}>"),
                ephemeral=True
            )
            return
        
        # Проверяем кулдаун
        can_use, time_left = check_cooldown(interaction.user.id)
        if not can_use:
            await interaction.response.send_message(
                convert_to_font(f"⏰ подожди {time_left} секунд перед следующим вопросом"),
                ephemeral=True
            )
            return
        
        # Отправляем сообщение о загрузке
        await interaction.response.defer()
        
        # Отправляем запрос к ChatGPT
        result = await ask_chatgpt(interaction.user.id, question)
        
        if result['success']:
            # Обновляем время последнего запроса
            last_requests[interaction.user.id] = datetime.now()
            
            # Создаём embed с ответом
            embed = BotTheme.create_embed(
                title="🤖 ChatGPT",
                description=result['response'],
                embed_type='info'
            )
            embed.set_footer(text=f"Вопрос от {interaction.user.name}")
            
            await interaction.followup.send(embed=embed)
        else:
            # Ошибка
            embed = error_embed(
                title=convert_to_font("❌ ошибка"),
                description=convert_to_font(result['error'])
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="clear_chat", description="Очистить историю диалога с ChatGPT")
    async def clear_chat_slash(interaction: discord.Interaction):
        """Slash команда для очистки истории"""
        if not is_chatgpt_channel(interaction.channel_id):
            await interaction.response.send_message(
                convert_to_font(f"❌ эта команда работает только в канале <#{CHATGPT_CHANNEL_ID}>"),
                ephemeral=True
            )
            return
        
        clear_history(interaction.user.id)
        
        embed = BotTheme.create_embed(
            title="🗑️ История очищена",
            description=convert_to_font("твоя история диалога с ChatGPT очищена"),
            embed_type='success'
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="chatgpt_help", description="Помощь по ChatGPT")
    async def chatgpt_help_slash(interaction: discord.Interaction):
        """Slash команда для справки"""
        embed = BotTheme.create_embed(
            title="🤖 ChatGPT - Помощь",
            description="Как использовать ChatGPT в Discord",
            embed_type='info'
        )
        
        embed.add_field(
            name="📝 Команды",
            value=(
                "**/ask [вопрос]** - задать вопрос ChatGPT\n"
                "**/clear_chat** - очистить историю диалога\n"
                "**/chatgpt_help** - эта справка"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💬 Автоматический режим",
            value=f"Просто пиши в канале <#{CHATGPT_CHANNEL_ID}> без команды - бот автоматически ответит!",
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
                "• Используй /clear_chat для начала нового диалога"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    print(f"✅ Зарегистрировано 3 ChatGPT команды")


async def on_message_chatgpt(message, bot):
    """
    Обработка сообщений в канале ChatGPT или приватных каналах
    Автоматически отвечает на сообщения без команды
    """
    # Игнорируем ботов
    if message.author.bot:
        return
    
    # Проверяем канал (ChatGPT канал или приватный канал)
    import private_channels_system
    is_chatgpt = is_chatgpt_channel(message.channel.id)
    is_private = private_channels_system.is_private_channel(message.channel.id)
    
    if not is_chatgpt and not is_private:
        return
    
    # Игнорируем команды
    if message.content.startswith('!') or message.content.startswith('/'):
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
