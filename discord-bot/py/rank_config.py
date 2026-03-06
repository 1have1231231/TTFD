# Конфигурация ранговой системы
"""
Ранговая система F-S с XP порогами
"""

# Ранги по буквам с XP порогами
RANK_TIERS = {
    'F': {'min_xp': 0, 'max_xp': 1249, 'color': '#95a5a6', 'emoji': '🔰'},
    'E': {'min_xp': 1250, 'max_xp': 4999, 'color': '#7f8c8d', 'emoji': '⚪'},
    'D': {'min_xp': 5000, 'max_xp': 10999, 'color': '#3498db', 'emoji': '🔵'},
    'C': {'min_xp': 11000, 'max_xp': 19249, 'color': '#2ecc71', 'emoji': '🟢'},
    'B': {'min_xp': 19250, 'max_xp': 29749, 'color': '#f39c12', 'emoji': '🟡'},
    'A': {'min_xp': 29750, 'max_xp': 42499, 'color': '#e74c3c', 'emoji': '🔴'},
    'S': {'min_xp': 42500, 'max_xp': float('inf'), 'color': '#9b59b6', 'emoji': '🟣'}
}

# Порядок рангов
RANK_ORDER = ['F', 'E', 'D', 'C', 'B', 'A', 'S']

# Допустимые цвета для команды /color (включая градиенты)
ALLOWED_COLORS = {
    # Основные цвета
    'red': 0xFF0000,
    'blue': 0x0000FF,
    'green': 0x00FF00,
    'yellow': 0xFFFF00,
    'purple': 0x800080,
    'pink': 0xFFC0CB,
    'orange': 0xFFA500,
    'cyan': 0x00FFFF,
    'white': 0xFFFFFF,
    'black': 0x000000,
    'gold': 0xFFD700,
    'silver': 0xC0C0C0,
    'brown': 0x8B4513,
    'lime': 0x00FF00,
    'navy': 0x000080,
    'teal': 0x008080,
    'magenta': 0xFF00FF,
    'crimson': 0xDC143C,
    'indigo': 0x4B0082,
    'violet': 0xEE82EE,
    
    # Градиентные цвета (эмуляция через яркие оттенки)
    'sunset': 0xFF6B35,      # Оранжево-красный градиент
    'ocean': 0x006994,       # Сине-голубой градиент  
    'forest': 0x228B22,      # Зелено-темно-зеленый
    'galaxy': 0x4B0082,      # Фиолетово-синий
    'fire': 0xFF4500,        # Красно-оранжевый
    'ice': 0x87CEEB,         # Голубо-белый
    'neon': 0x39FF14,        # Ярко-зеленый неон
    'plasma': 0xFF1493,      # Розово-фиолетовый
    'aurora': 0x00CED1,      # Бирюзово-зеленый
    'cosmic': 0x9370DB,      # Фиолетово-синий космос
}

# ID кастомной цветной роли (создается ботом)
CUSTOM_COLOR_ROLE_NAME = "Custom Color"
CUSTOM_COLOR_ROLE_PERMISSIONS = {
    'administrator': False,
    'manage_guild': False,
    'manage_roles': False,
    'manage_channels': False,
    'kick_members': False,
    'ban_members': False,
    'manage_messages': False,
    'mention_everyone': False,
    'view_audit_log': False,
    'priority_speaker': False,
    'stream': False,
    'send_messages': True,
    'embed_links': True,
    'attach_files': True,
    'add_reactions': True,
    'use_external_emojis': True,
    'connect': True,
    'speak': True,
    'use_voice_activation': True
}

def get_rank_by_xp(xp):
    """
    Получить ранг по количеству XP
    
    Args:
        xp (int): Количество XP
    
    Returns:
        str: Буква ранга (F, E, D, C, B, A, S)
    """
    for rank in RANK_ORDER:
        tier = RANK_TIERS[rank]
        if tier['min_xp'] <= xp <= tier['max_xp']:
            return rank
    return 'F'

def get_next_rank(current_rank):
    """
    Получить следующий ранг
    
    Args:
        current_rank (str): Текущий ранг
    
    Returns:
        str or None: Следующий ранг или None если достигнут максимум
    """
    try:
        current_index = RANK_ORDER.index(current_rank)
        if current_index < len(RANK_ORDER) - 1:
            return RANK_ORDER[current_index + 1]
        return None
    except ValueError:
        return None

def get_xp_for_next_rank(xp):
    """
    Получить сколько XP нужно для следующего ранга
    
    Args:
        xp (int): Текущее количество XP
    
    Returns:
        dict: {
            'current_rank': str,
            'next_rank': str or None,
            'current_xp': int,
            'next_rank_xp': int or None,
            'xp_needed': int or None,
            'progress_percent': float
        }
    """
    current_rank = get_rank_by_xp(xp)
    next_rank = get_next_rank(current_rank)
    
    if not next_rank:
        # Максимальный ранг достигнут
        return {
            'current_rank': current_rank,
            'next_rank': None,
            'current_xp': xp,
            'next_rank_xp': None,
            'xp_needed': None,
            'progress_percent': 100.0
        }
    
    current_tier = RANK_TIERS[current_rank]
    next_tier = RANK_TIERS[next_rank]
    
    xp_needed = next_tier['min_xp'] - xp
    xp_in_current_tier = xp - current_tier['min_xp']
    total_xp_in_tier = next_tier['min_xp'] - current_tier['min_xp']
    progress_percent = (xp_in_current_tier / total_xp_in_tier) * 100 if total_xp_in_tier > 0 else 0
    
    return {
        'current_rank': current_rank,
        'next_rank': next_rank,
        'current_xp': xp,
        'next_rank_xp': next_tier['min_xp'],
        'xp_needed': xp_needed,
        'progress_percent': progress_percent
    }

def format_cooldown(seconds):
    """
    Форматировать кулдаун в читаемый вид
    
    Args:
        seconds (int): Количество секунд
    
    Returns:
        str: Отформатированная строка (например "1 ч 12 мин", "2 мин 18 сек", "43 сек")
    """
    if seconds < 60:
        return f"{seconds} сек"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes} мин {secs} сек"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} ч {minutes} мин"

def create_progress_bar(current, total, length=10):
    """
    Создать визуальный прогресс-бар
    
    Args:
        current (int): Текущее значение
        total (int): Максимальное значение
        length (int): Длина бара
    
    Returns:
        str: Прогресс-бар (например "████████░░ 80%")
    """
    if total <= 0:
        return "░" * length + " 0%"
    
    filled = int((current / total) * length)
    filled = max(0, min(filled, length))
    bar = "█" * filled + "░" * (length - filled)
    percentage = int((current / total) * 100)
    return f"{bar} {percentage}%"
