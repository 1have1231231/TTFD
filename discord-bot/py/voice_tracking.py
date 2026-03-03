# Система отслеживания времени в голосовых каналах

import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import json
import os

# Файл для хранения данных о войс активности
VOICE_DATA_FILE = 'json/voice_data.json'

# Активные сессии {user_id: {'channel_id': int, 'join_time': str, 'session_start': str, 'last_xp_time': str}}
active_sessions = {}

# Глобальные ссылки на бота и БД для фоновой задачи
_bot = None
_db = None

def load_voice_data():
    """Загрузить данные о войс активности"""
    if os.path.exists(VOICE_DATA_FILE):
        try:
            with open(VOICE_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        'users': {},  # {user_id: {'total_time': seconds, 'sessions': []}}
        'channels': {}  # {channel_id: {'total_time': seconds, 'sessions': []}}
    }

def save_voice_data(data):
    """Сохранить данные о войс активности"""
    os.makedirs('json', exist_ok=True)
    with open(VOICE_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def init_voice_tracking(bot, db):
    """
    Инициализировать систему отслеживания войса
    
    Args:
        bot: Discord Bot instance
        db: Database instance
    """
    global _bot, _db
    _bot = bot
    _db = db
    
    # Запускаем фоновую задачу начисления XP
    if not award_voice_xp_task.is_running():
        award_voice_xp_task.start()
        print("✅ Фоновая задача начисления XP за войс запущена")

@tasks.loop(minutes=1)
async def award_voice_xp_task():
    """
    Фоновая задача: начисляет XP каждую минуту всем пользователям в войсе
    и проверяет выдачу ролей за ранги
    """
    if not _bot or not _db:
        return
    
    now = datetime.now()
    
    # Импортируем систему ролей
    try:
        import rank_roles
    except:
        rank_roles = None
    
    # Проходим по всем активным сессиям
    for user_id, session in list(active_sessions.items()):
        try:
            # Получаем время последнего начисления XP
            last_xp_time_str = session.get('last_xp_time', session['join_time'])
            last_xp_time = datetime.fromisoformat(last_xp_time_str)
            
            # Вычисляем время с последнего начисления
            time_since_last_xp = (now - last_xp_time).total_seconds()
            
            # Если прошла минута или больше - начисляем XP
            if time_since_last_xp >= 60:
                # Начисляем 0.5 XP за минуту
                minutes_passed = int(time_since_last_xp / 60)
                xp_reward = minutes_passed * 0.5
                
                # Проверяем бонус за час (каждые 60 минут +10 XP)
                total_minutes_in_voice = (now - datetime.fromisoformat(session['session_start'])).total_seconds() / 60
                hours_completed = int(total_minutes_in_voice / 60)
                previous_hours = int((total_minutes_in_voice - minutes_passed) / 60)
                
                # Если завершился новый час - добавляем бонус
                if hours_completed > previous_hours:
                    hours_bonus = (hours_completed - previous_hours) * 10
                    xp_reward += hours_bonus
                    print(f"🎉 Бонус за {hours_completed} час(ов): +{hours_bonus} XP")
                
                xp_reward = int(xp_reward)
                
                # Обновляем данные пользователя
                user = _db.get_user(user_id)
                old_xp = user.get('xp', 0)
                user['xp'] = old_xp + xp_reward
                _db.check_rank_up(user)
                _db.save_user(user_id, user)
                new_xp = user.get('xp', 0)
                
                # Обновляем время последнего начисления
                session['last_xp_time'] = now.isoformat()
                
                # Получаем информацию о пользователе для логирования и выдачи роли
                member = None
                try:
                    for guild in _bot.guilds:
                        member = guild.get_member(int(user_id))
                        if member:
                            print(f"💎 {member.name} получил {xp_reward} XP за {minutes_passed} мин в войсе (онлайн)")
                            break
                except:
                    print(f"💎 User {user_id} получил {xp_reward} XP за {minutes_passed} мин в войсе (онлайн)")
                
                # Проверяем и выдаём роль если нужно
                if member and rank_roles:
                    try:
                        # Определяем старую и новую роль по XP
                        old_tier = rank_roles.get_role_for_xp(old_xp)
                        new_tier = rank_roles.get_role_for_xp(new_xp)
                        
                        # Если роль изменилась - обновляем
                        if old_tier != new_tier and new_tier:
                            result = await rank_roles.update_user_rank_role(member, new_xp)
                            
                            if result['success'] and result['action'] == 'added':
                                print(f"🎊 {member.name} получил роль {result['role'].name} за достижение {new_xp} XP!")
                                
                                # Отправляем уведомление в канал получения ролей
                                RANK_UP_CHANNEL_ID = 1466294080589008916
                                try:
                                    channel = member.guild.get_channel(RANK_UP_CHANNEL_ID)
                                    if channel and channel.permissions_for(member.guild.me).send_messages:
                                        from theme import BotTheme
                                        from font_converter import convert_to_font
                                        
                                        embed = BotTheme.create_embed(
                                            title=convert_to_font("🎊 новая роль!"),
                                            description=convert_to_font(f"поздравляем {member.mention}!"),
                                            embed_type='success'
                                        )
                                        
                                        if old_tier:
                                            embed.add_field(
                                                name=convert_to_font("старая роль"),
                                                value=convert_to_font(f"{old_tier} - ранг"),
                                                inline=True
                                            )
                                        
                                        embed.add_field(
                                            name=convert_to_font("новая роль"),
                                            value=f"{result['role'].mention}",
                                            inline=True
                                        )
                                        
                                        embed.add_field(
                                            name=convert_to_font("💎 твой xp"),
                                            value=convert_to_font(str(new_xp)),
                                            inline=False
                                        )
                                        
                                        await channel.send(embed=embed)
                                except Exception as notif_error:
                                    print(f"⚠️ Не удалось отправить уведомление о роли: {notif_error}")
                    
                    except Exception as role_error:
                        print(f"⚠️ Ошибка проверки/выдачи роли для {member.name}: {role_error}")
        
        except Exception as e:
            print(f"❌ Ошибка начисления XP для {user_id}: {e}")
            continue

def check_and_update_voice_streak(user, db):
    """
    Проверить и обновить стрик за ежедневный вход в войс
    
    Args:
        user: Данные пользователя
        db: Database instance
    
    Returns:
        dict: {'streak_updated': bool, 'current_streak': int, 'bonus_xp': int}
    """
    from datetime import date
    
    today = date.today()
    last_voice_date = user.get('last_voice_date')
    
    # Если last_voice_date это строка, конвертируем в date
    if isinstance(last_voice_date, str):
        try:
            last_voice_date = date.fromisoformat(last_voice_date)
        except:
            last_voice_date = None
    
    current_streak = user.get('voice_streak', 0)
    bonus_xp = 0
    streak_updated = False
    
    # Если сегодня уже был в войсе - не обновляем
    if last_voice_date == today:
        return {
            'streak_updated': False,
            'current_streak': current_streak,
            'bonus_xp': 0
        }
    
    # Проверяем был ли вчера
    if last_voice_date:
        days_diff = (today - last_voice_date).days
        
        if days_diff == 1:
            # Продолжаем стрик
            current_streak += 1
            streak_updated = True
        elif days_diff > 1:
            # Стрик сброшен
            current_streak = 1
            streak_updated = True
        # days_diff == 0 не должно быть (проверили выше)
    else:
        # Первый раз в войсе
        current_streak = 1
        streak_updated = True
    
    # Рассчитываем бонус XP за стрик
    # 1 день = +5 XP, 7 дней = +10 XP, 30 дней = +20 XP, 100 дней = +50 XP
    if current_streak >= 100:
        bonus_xp = 50
    elif current_streak >= 30:
        bonus_xp = 20
    elif current_streak >= 7:
        bonus_xp = 10
    else:
        bonus_xp = 5
    
    # Обновляем данные пользователя
    if streak_updated:
        user['voice_streak'] = current_streak
        user['last_voice_date'] = today.isoformat()
    
    return {
        'streak_updated': streak_updated,
        'current_streak': current_streak,
        'bonus_xp': bonus_xp
    }

async def on_voice_state_update(member, before, after, db=None):
    """Обработка изменения голосового состояния"""
    user_id = str(member.id)
    now = datetime.now()
    
    voice_data = load_voice_data()
    
    # Инициализация данных пользователя
    if user_id not in voice_data['users']:
        voice_data['users'][user_id] = {
            'total_time': 0,
            'sessions': [],
            'username': member.name
        }
    
    # Пользователь зашёл в войс канал
    if before.channel is None and after.channel is not None:
        channel_id = str(after.channel.id)
        
        # Инициализация данных канала
        if channel_id not in voice_data['channels']:
            voice_data['channels'][channel_id] = {
                'total_time': 0,
                'sessions': [],
                'channel_name': after.channel.name
            }
        
        # Проверяем и обновляем стрик
        if db:
            user = db.get_user(user_id, member.name)
            streak_result = check_and_update_voice_streak(user, db)
            
            if streak_result['streak_updated']:
                # Начисляем бонус XP за стрик
                user['xp'] = user.get('xp', 0) + streak_result['bonus_xp']
                db.check_rank_up(user)
                db.save_user(user_id, user)
                
                print(f"🔥 {member.name} получил стрик {streak_result['current_streak']} дней! Бонус: +{streak_result['bonus_xp']} XP")
        
        # Сохраняем активную сессию
        active_sessions[user_id] = {
            'channel_id': channel_id,
            'join_time': now.isoformat(),
            'session_start': now.isoformat(),
            'last_xp_time': now.isoformat()
        }
        
        print(f"🎤 {member.name} зашёл в {after.channel.name}")
    
    # Пользователь вышел из войс канала
    elif before.channel is not None and after.channel is None:
        if user_id in active_sessions:
            session = active_sessions[user_id]
            channel_id = session['channel_id']
            join_time = datetime.fromisoformat(session['join_time'])
            
            # Вычисляем время сессии
            session_duration = (now - join_time).total_seconds()
            
            # Обновляем данные пользователя
            voice_data['users'][user_id]['total_time'] += session_duration
            voice_data['users'][user_id]['sessions'].append({
                'channel_id': channel_id,
                'start': session['join_time'],
                'end': now.isoformat(),
                'duration': session_duration
            })
            
            # Обновляем данные канала
            if channel_id in voice_data['channels']:
                voice_data['channels'][channel_id]['total_time'] += session_duration
                voice_data['channels'][channel_id]['sessions'].append({
                    'user_id': user_id,
                    'start': session['join_time'],
                    'end': now.isoformat(),
                    'duration': session_duration
                })
            
            # Начисляем XP за время в войсе
            if db and session_duration >= 60:  # Минимум 1 минута
                xp_reward = calculate_voice_xp(session_duration)
                if xp_reward > 0:
                    user = db.get_user(user_id)
                    old_xp = user.get('xp', 0)
                    user['xp'] = old_xp + xp_reward
                    db.check_rank_up(user)
                    db.save_user(user_id, user)
                    print(f"💎 {member.name} получил {xp_reward} XP за {format_time(session_duration)} в войсе")
            
            # Удаляем активную сессию
            del active_sessions[user_id]
            
            print(f"🎤 {member.name} вышел из войса (время: {format_time(session_duration)})")
            
            save_voice_data(voice_data)
    
    # Пользователь переключился между каналами
    elif before.channel is not None and after.channel is not None and before.channel != after.channel:
        # Завершаем старую сессию
        if user_id in active_sessions:
            session = active_sessions[user_id]
            old_channel_id = session['channel_id']
            join_time = datetime.fromisoformat(session['join_time'])
            
            session_duration = (now - join_time).total_seconds()
            
            # Обновляем данные для старого канала
            voice_data['users'][user_id]['total_time'] += session_duration
            voice_data['users'][user_id]['sessions'].append({
                'channel_id': old_channel_id,
                'start': session['join_time'],
                'end': now.isoformat(),
                'duration': session_duration
            })
            
            if old_channel_id in voice_data['channels']:
                voice_data['channels'][old_channel_id]['total_time'] += session_duration
                voice_data['channels'][old_channel_id]['sessions'].append({
                    'user_id': user_id,
                    'start': session['join_time'],
                    'end': now.isoformat(),
                    'duration': session_duration
                })
            
            # Начисляем XP за время в старом канале
            if db and session_duration >= 60:  # Минимум 1 минута
                xp_reward = calculate_voice_xp(session_duration)
                if xp_reward > 0:
                    user = db.get_user(user_id)
                    old_xp = user.get('xp', 0)
                    user['xp'] = old_xp + xp_reward
                    db.check_rank_up(user)
                    db.save_user(user_id, user)
                    print(f"💎 {member.name} получил {xp_reward} XP за {format_time(session_duration)} в войсе")
        
        # Начинаем новую сессию
        new_channel_id = str(after.channel.id)
        
        if new_channel_id not in voice_data['channels']:
            voice_data['channels'][new_channel_id] = {
                'total_time': 0,
                'sessions': [],
                'channel_name': after.channel.name
            }
        
        active_sessions[user_id] = {
            'channel_id': new_channel_id,
            'join_time': now.isoformat(),
            'session_start': now.isoformat(),
            'last_xp_time': now.isoformat()
        }
        
        print(f"🎤 {member.name} переключился в {after.channel.name}")
        
        save_voice_data(voice_data)

def format_time(seconds):
    """Форматировать время в читаемый вид"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}ч {minutes}м {secs}с"
    elif minutes > 0:
        return f"{minutes}м {secs}с"
    else:
        return f"{secs}с"

def get_top_users(limit=10):
    """Получить топ пользователей по времени в войсе"""
    voice_data = load_voice_data()
    
    users = []
    for user_id, data in voice_data['users'].items():
        users.append({
            'user_id': user_id,
            'username': data.get('username', 'Unknown'),
            'total_time': data['total_time'],
            'sessions_count': len(data['sessions'])
        })
    
    users.sort(key=lambda x: x['total_time'], reverse=True)
    return users[:limit]

def get_top_channels(limit=5):
    """Получить топ каналов по активности"""
    voice_data = load_voice_data()
    
    channels = []
    for channel_id, data in voice_data['channels'].items():
        channels.append({
            'channel_id': channel_id,
            'channel_name': data.get('channel_name', 'Unknown'),
            'total_time': data['total_time'],
            'sessions_count': len(data['sessions'])
        })
    
    channels.sort(key=lambda x: x['total_time'], reverse=True)
    return channels[:limit]

def get_longest_session():
    """Получить самую длительную сессию"""
    voice_data = load_voice_data()
    
    longest = None
    longest_duration = 0
    
    for user_id, data in voice_data['users'].items():
        for session in data['sessions']:
            if session['duration'] > longest_duration:
                longest_duration = session['duration']
                longest = {
                    'user_id': user_id,
                    'username': data.get('username', 'Unknown'),
                    'channel_id': session['channel_id'],
                    'duration': session['duration'],
                    'start': session['start'],
                    'end': session['end']
                }
    
    return longest

def get_user_voice_stats(user_id):
    """Получить статистику пользователя"""
    voice_data = load_voice_data()
    user_id = str(user_id)
    
    if user_id not in voice_data['users']:
        return None
    
    data = voice_data['users'][user_id]
    
    # Находим самую длительную сессию пользователя
    longest_session = 0
    for session in data['sessions']:
        if session['duration'] > longest_session:
            longest_session = session['duration']
    
    return {
        'total_time': data['total_time'],
        'sessions_count': len(data['sessions']),
        'longest_session': longest_session,
        'average_session': data['total_time'] / len(data['sessions']) if data['sessions'] else 0
    }


def calculate_voice_xp(duration_seconds):
    """
    Рассчитать XP за время в войсе
    
    Формула:
    - 1 минута = 0.5 XP
    - 1 час = +10 XP бонус к накопленному
    """
    minutes = duration_seconds / 60
    
    # Базовый XP: 0.5 за минуту
    base_xp = minutes * 0.5
    
    # Бонус за каждый час: +10 XP
    hours = int(minutes / 60)
    bonus_xp = hours * 10
    
    total_xp = base_xp + bonus_xp
    
    return int(total_xp)

def calculate_message_xp(message_length):
    """
    XP за сообщения отключен - XP начисляется только за войс
    """
    return 0

# Кулдаун для сообщений убран - каждое сообщение даёт XP
# {user_id: last_message_time}
message_cooldowns = {}

def can_earn_message_xp(user_id):
    """
    Проверить можно ли получить XP за сообщение
    Кулдаун убран - каждое сообщение даёт XP
    """
    # Всегда возвращаем True - кулдауна нет
    return True
