"""
Менеджер команд бота
Автоматически собирает и обновляет список команд в канале Discord
"""

from font_converter import convert_to_font
from datetime import datetime

# Список всех команд бота с описаниями
# При добавлении новой команды - добавь её сюда!
COMMANDS_LIST = {
    '📌 основные': [
        ('/help', 'список всех команд'),
        ('/ping', 'проверка задержки'),
        ('/stats', 'статистика бота'),
        ('/links', 'актуальные ссылки'),
    ],
    '👤 профиль': [
        ('/profile [@игрок]', 'профиль пользователя'),
        ('/balance [@игрок]', 'баланс, XP и прогресс до следующего ранга'),
        ('/rank', 'твой ранг и прогресс'),
        ('/top [категория]', 'таблица лидеров (xp/coins/games)'),
        ('/streak [@игрок]', 'стрик за ежедневный войс'),
    ],
    '💰 заработок': [
        ('/daily', 'ежедневная награда (24 часа)'),
        ('/work', 'поработать (1 раз в час)'),
    ],
    '🎮 мини-игры': [
        ('/dice', 'бросить кубик (1 раз в час)'),
        ('/coinflip [выбор]', 'подбросить монетку (1 раз в час)'),
    ],
    '🛒 магазин': [
        ('/shop', 'открыть магазин ролей'),
        ('/buyrole [номер]', 'купить роль за монеты'),
        ('/pay [@игрок] [сумма]', 'перевести монеты'),
    ],
    '🎨 кастомизация': [
        ('/color [цвет]', 'изменить цвет своего никнейма'),
    ],
    '🔗 интеграция': [
        ('/getcode', 'получить код для привязки Telegram'),
        ('/checklink', 'проверить статус привязки Telegram'),
        ('/unlink', 'отвязать Telegram аккаунт'),
    ],
    '💬 поддержка': [
        ('/ticket', 'создать тикет поддержки'),
        ('/close', 'закрыть тикет'),
    ],
    '⚙️ администрирование': [
        ('/clear [кол-во]', 'очистить сообщения (1-100)'),
        ('/sync', 'синхронизировать команды бота'),
        ('/updatecommands', 'обновить список команд в канале'),
        ('/setupverification', 'настроить систему верификации'),
        ('/setuptickets', 'настроить кнопку тикетов'),
        ('/setuprankroles [tier] [@роль]', 'настроить роли для рангов'),
        ('/syncrankroles', 'синхронизировать роли всех пользователей'),
    ],
}

def get_commands_text():
    """
    Получить отформатированный текст со списком команд
    
    Returns:
        str: Текст для отправки в Discord канал
    """
    date_str = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    text_parts = [
        convert_to_font('🎮 команды бота'),
        convert_to_font('━━━━━━━━━━━━━━━━━━'),
        ''
    ]
    
    # Добавляем команды по категориям
    for category, commands in COMMANDS_LIST.items():
        text_parts.append(convert_to_font(category))
        for cmd, desc in commands:
            # Форматируем команду с выравниванием
            if desc:  # Если есть описание
                text_parts.append(convert_to_font(f'{cmd:<12} — {desc}'))
            else:  # Если описания нет
                text_parts.append(convert_to_font(f'{cmd}'))
        text_parts.append('')
    
    # Добавляем футер
    text_parts.extend([
        convert_to_font('━━━━━━━━━━━━━━━━━━'),
        convert_to_font('🏆 ранговая система: F → E → D → C → B → A → S'),
        convert_to_font('🎨 доступные цвета: red, blue, green, yellow, purple, pink, orange, cyan, white, black, gold, silver, brown, lime, navy, teal, magenta, crimson, indigo, violet'),
        convert_to_font('🎮 играй в игры на сайте и получай ранги!'),
        convert_to_font(f'📅 обновлено: {date_str}')
    ])
    
    return '\n'.join(text_parts)

def add_command(category, command, description):
    """
    Добавить новую команду в список
    
    Args:
        category (str): Категория команды (например, '🎮 мини-игры')
        command (str): Название команды (например, '!newgame')
        description (str): Описание команды
    """
    if category not in COMMANDS_LIST:
        COMMANDS_LIST[category] = []
    
    COMMANDS_LIST[category].append((command, description))
    print(f"✅ Команда {command} добавлена в категорию {category}")

def remove_command(command):
    """
    Удалить команду из списка
    
    Args:
        command (str): Название команды для удаления
    """
    for category, commands in COMMANDS_LIST.items():
        for i, (cmd, desc) in enumerate(commands):
            if cmd == command:
                COMMANDS_LIST[category].pop(i)
                print(f"✅ Команда {command} удалена из категории {category}")
                return True
    
    print(f"⚠️ Команда {command} не найдена")
    return False

def get_all_commands():
    """
    Получить список всех команд
    
    Returns:
        dict: Словарь с категориями и командами
    """
    return COMMANDS_LIST

# Тестирование
if __name__ == "__main__":
    print("="*70)
    print("СПИСОК КОМАНД БОТА")
    print("="*70)
    print(get_commands_text())
    print("="*70)
