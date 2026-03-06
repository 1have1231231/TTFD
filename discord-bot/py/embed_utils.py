# Утилиты для создания embed сообщений
"""
Вспомогательные функции для создания красивых embed'ов
"""
import discord
from font_converter import convert_to_font
from theme import BotTheme
from rank_config import RANK_TIERS, get_rank_by_xp, get_xp_for_next_rank, create_progress_bar

def create_balance_embed(user, user_data, target_member):
    """
    Создать embed для команды /balance
    
    Args:
        user: Discord User объект
        user_data: Данные пользователя из БД
        target_member: Discord Member объект
    
    Returns:
        discord.Embed: Готовый embed
    """
    coins = user_data.get('coins', 0)
    xp = user_data.get('xp', 0)
    
    # Получаем информацию о ранге
    rank_info = get_xp_for_next_rank(xp)
    current_rank = rank_info['current_rank']
    next_rank = rank_info['next_rank']
    xp_needed = rank_info['xp_needed']
    progress_percent = rank_info['progress_percent']
    
    # Получаем данные текущего ранга
    current_tier = RANK_TIERS[current_rank]
    
    # Создаём embed
    embed = discord.Embed(
        title=convert_to_font(f"💰 баланс {target_member.name}"),
        color=int(current_tier['color'].replace('#', '0x'), 16)
    )
    
    # Основная информация
    embed.add_field(
        name=convert_to_font("💰 монеты"),
        value=convert_to_font(f"{coins:,}"),
        inline=True
    )
    
    embed.add_field(
        name=convert_to_font("💎 xp"),
        value=convert_to_font(f"{xp:,}"),
        inline=True
    )
    
    embed.add_field(
        name=convert_to_font("🏆 ранг"),
        value=f"{current_tier['emoji']} {convert_to_font(f'ранг {current_rank}')}",
        inline=True
    )
    
    # Прогресс до следующего ранга
    if next_rank:
        next_tier = RANK_TIERS[next_rank]
        
        # Прогресс-бар
        xp_in_tier = xp - current_tier['min_xp']
        total_xp_in_tier = next_tier['min_xp'] - current_tier['min_xp']
        progress_bar = create_progress_bar(xp_in_tier, total_xp_in_tier, 15)
        
        embed.add_field(
            name=convert_to_font(f"📈 прогресс до ранга {next_rank}"),
            value=f"{convert_to_font(progress_bar)}\n{convert_to_font(f'осталось: {xp_needed:,} xp')}",
            inline=False
        )
    else:
        embed.add_field(
            name=convert_to_font("🌟 максимальный ранг"),
            value=convert_to_font("ты достиг максимального ранга!"),
            inline=False
        )
    
    embed.set_thumbnail(url=target_member.display_avatar.url)
    embed.set_footer(text=convert_to_font("используй /daily и /work для заработка"))
    
    return embed
