# Система магазина и экономики

import discord
from discord.ext import commands
from datetime import datetime, timedelta
import json
import os
from font_converter import convert_to_font
from theme import BotTheme, shop_embed, success_embed, error_embed

# Файл для хранения предметов магазина
SHOP_FILE = 'json/shop_items.json'

# Предметы магазина по умолчанию
DEFAULT_SHOP_ITEMS = {
    'roles': [
        {
            'id': 'premium_role_1',
            'name': 'Премиум роль 💎',
            'description': 'Эксклюзивная роль',
            'price': 15000,
            'emoji': '💎',
            'category': 'roles',
            'role_id': 1478224551287590983
        },
        {
            'id': 'vip_role',
            'name': 'VIP роль 👑',
            'description': 'VIP статус',
            'price': 10000,
            'emoji': '👑',
            'category': 'roles',
            'role_id': 1478208144319582312
        },
        {
            'id': 'star_role',
            'name': 'Звёздная роль ⭐',
            'description': 'Особая роль',
            'price': 5000,
            'emoji': '⭐',
            'category': 'roles',
            'role_id': 1478222910794502335
        },
        {
            'id': 'supporter_role',
            'name': 'Роль поддержки 🎯',
            'description': 'Роль саппортера',
            'price': 1000,
            'emoji': '🎯',
            'category': 'roles',
            'role_id': 1478226541094637628
        },
    ],
    'boosts': [
        {
            'id': 'xp_boost_1h',
            'name': 'Буст XP (1 час)',
            'description': 'x2 xp на 1 час',
            'price': 500,
            'duration': 3600,  # секунды
            'multiplier': 2,
            'emoji': '⚡',
            'category': 'boosts',
            'boost_type': 'xp'
        },
        {
            'id': 'xp_boost_24h',
            'name': 'Буст XP (24 часа)',
            'description': 'x2 xp на 24 часа',
            'price': 3000,
            'duration': 86400,
            'multiplier': 2,
            'emoji': '🚀',
            'category': 'boosts',
            'boost_type': 'xp'
        },
        {
            'id': 'coins_boost_1h',
            'name': 'Буст монет (1 час)',
            'description': 'x2 монеты на 1 час',
            'price': 600,
            'duration': 3600,
            'multiplier': 2,
            'emoji': '💰',
            'category': 'boosts',
            'boost_type': 'coins'
        },
        {
            'id': 'luck_boost_1h',
            'name': 'Буст удачи (1 час)',
            'description': 'больше шанс выигрыша в играх',
            'price': 800,
            'duration': 3600,
            'multiplier': 1.5,
            'emoji': '🍀',
            'category': 'boosts',
            'boost_type': 'luck'
        },
    ],
    'cosmetics': [
        {
            'id': 'profile_bg_dark',
            'name': 'Тёмный фон профиля',
            'description': 'чёрный фон для профиля',
            'price': 1500,
            'emoji': '🌑',
            'category': 'cosmetics',
            'cosmetic_type': 'background',
            'value': '#0d0d0d'
        },
        {
            'id': 'profile_bg_red',
            'name': 'Красный фон профиля',
            'description': 'кроваво-красный фон',
            'price': 1500,
            'emoji': '🔴',
            'category': 'cosmetics',
            'cosmetic_type': 'background',
            'value': '#8b0000'
        },
        {
            'id': 'profile_bg_gradient',
            'name': 'Градиентный фон',
            'description': 'чёрно-красный градиент',
            'price': 2500,
            'emoji': '🎨',
            'category': 'cosmetics',
            'cosmetic_type': 'background',
            'value': 'gradient'
        },
        {
            'id': 'custom_nickname',
            'name': 'Смена ника',
            'description': 'изменить свой ник на сервере',
            'price': 2000,
            'emoji': '✏️',
            'category': 'cosmetics',
            'cosmetic_type': 'nickname'
        },
    ],
    'special': [
        {
            'id': 'daily_reset',
            'name': 'Сброс daily',
            'description': 'сбросить кулдаун !daily',
            'price': 1000,
            'emoji': '🔄',
            'category': 'special',
            'special_type': 'daily_reset'
        },
        {
            'id': 'rank_boost',
            'name': 'Ускорение ранга',
            'description': '+1000 xp мгновенно',
            'price': 2000,
            'emoji': '📈',
            'category': 'special',
            'special_type': 'xp_instant',
            'value': 1000
        },
    ]
}

def load_shop_items():
    """Загрузить предметы магазина"""
    if os.path.exists(SHOP_FILE):
        try:
            with open(SHOP_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_SHOP_ITEMS

def save_shop_items(items):
    """Сохранить предметы магазина"""
    os.makedirs('json', exist_ok=True)
    with open(SHOP_FILE, 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

def get_all_items():
    """Получить все предметы магазина"""
    shop_items = load_shop_items()
    all_items = []
    for category in shop_items.values():
        all_items.extend(category)
    return all_items

def find_item(item_id):
    """Найти предмет по ID"""
    for item in get_all_items():
        if item['id'] == item_id:
            return item
    return None

def get_shop_embed_page(page=1, category='all'):
    """Создать embed магазина с пагинацией"""
    shop_items = load_shop_items()
    
    embed = shop_embed(
        title=convert_to_font("🛒 магазин"),
        description=convert_to_font("купи предметы за монеты!")
    )
    
    # Фильтруем по категории
    if category == 'all':
        categories_to_show = shop_items.keys()
    else:
        categories_to_show = [category] if category in shop_items else []
    
    for cat in categories_to_show:
        if cat not in shop_items:
            continue
            
        items = shop_items[cat]
        if not items:
            continue
        
        # Названия категорий
        category_names = {
            'roles': '👑 роли',
            'boosts': '⚡ бусты',
            'cosmetics': '🎨 косметика',
            'special': '✨ особое'
        }
        
        items_text = []
        for item in items:
            items_text.append(
                f"{item['emoji']} **{item['id']}** - {convert_to_font(item['name'])}\n"
                f"   {convert_to_font(item['description'])} | {convert_to_font(str(item['price']))} монет"
            )
        
        if items_text:
            embed.add_field(
                name=convert_to_font(category_names.get(cat, cat)),
                value='\n\n'.join(items_text),
                inline=False
            )
    
    embed.set_footer(text=convert_to_font("используй !buy [id] для покупки"))
    
    return embed

def get_shop_items(category='all'):
    """Получить предметы магазина по категории"""
    shop_items = load_shop_items()
    
    if category == 'all':
        all_items = []
        for items in shop_items.values():
            all_items.extend(items)
        return all_items
    
    return shop_items.get(category, [])

def buy_item(db, user_id, item_id):
    """
    Купить предмет (для использования в Views)
    Возвращает dict с результатом: {'success': bool, 'item': dict, 'error': str}
    """
    user = db.get_user(user_id)
    
    if not user:
        return {'success': False, 'error': 'пользователь не зарегистрирован'}
    
    item = find_item(item_id)
    
    if not item:
        return {'success': False, 'error': f"предмет '{item_id}' не найден"}
    
    # Проверка баланса
    if user.get('coins', 0) < item['price']:
        return {
            'success': False,
            'error': f"недостаточно монет\nнужно: {item['price']}, у тебя: {user.get('coins', 0)}"
        }
    
    # Инициализация инвентаря
    if 'inventory' not in user:
        user['inventory'] = []
    
    # Проверка на повторную покупку (для ролей и косметики)
    if item['category'] in ['roles', 'cosmetics']:
        if item_id in user['inventory']:
            return {'success': False, 'error': 'у тебя уже есть этот предмет'}
    
    # Покупка
    user['coins'] -= item['price']
    
    # Обработка по типу предмета
    if item['category'] in ['roles', 'cosmetics']:
        user['inventory'].append(item_id)
    
    elif item['category'] == 'boosts':
        # Активация буста
        if 'active_boosts' not in user:
            user['active_boosts'] = []
        
        boost_data = {
            'item_id': item_id,
            'boost_type': item.get('boost_type', 'xp'),
            'multiplier': item.get('multiplier', 2),
            'expires_at': (datetime.now() + timedelta(seconds=item['duration'])).isoformat()
        }
        
        user['active_boosts'].append(boost_data)
    
    elif item['category'] == 'special':
        special_type = item.get('special_type')
        
        if special_type == 'daily_reset':
            user['last_daily_date'] = None
        
        elif special_type == 'xp_instant':
            xp_amount = item.get('value', 1000)
            user['xp'] = user.get('xp', 0) + xp_amount
            db.check_rank_up(user)
    
    db.save_user(user_id, user)
    
    return {'success': True, 'item': item}

async def buy_item_legacy(ctx, bot, db, item_id):
    """Купить предмет (старая версия для команды !buy)"""
    user = db.get_user(str(ctx.author.id))
    
    if not user:
        return False, error_embed(
            title=convert_to_font("❌ ошибка"),
            description=convert_to_font("ты не зарегистрирован!")
        )
    
    item = find_item(item_id)
    
    if not item:
        return False, error_embed(
            title=convert_to_font("❌ предмет не найден"),
            description=convert_to_font(f"предмет '{item_id}' не существует")
        )
    
    # Проверка баланса
    if user['coins'] < item['price']:
        return False, error_embed(
            title=convert_to_font("❌ недостаточно монет"),
            description=convert_to_font(f"нужно: {item['price']}, у тебя: {user['coins']}")
        )
    
    # Инициализация инвентаря
    if 'inventory' not in user:
        user['inventory'] = []
    
    # Проверка на повторную покупку (для ролей и косметики)
    if item['category'] in ['roles', 'cosmetics']:
        if item_id in user['inventory']:
            return False, error_embed(
                title=convert_to_font("❌ уже куплено"),
                description=convert_to_font("у тебя уже есть этот предмет!")
            )
    
    # Покупка
    user['coins'] -= item['price']
    
    # Обработка по типу предмета
    result_message = ""
    
    if item['category'] == 'roles':
        # Выдача роли
        if item.get('role_id'):
            try:
                role = ctx.guild.get_role(item['role_id'])
                if role:
                    await ctx.author.add_roles(role)
                    result_message = convert_to_font(f"роль {role.name} выдана!")
                else:
                    result_message = convert_to_font("роль не настроена на сервере")
            except Exception as e:
                result_message = convert_to_font(f"ошибка выдачи роли: {e}")
        else:
            result_message = convert_to_font("роль не настроена (обратись к админу)")
        
        user['inventory'].append(item_id)
    
    elif item['category'] == 'boosts':
        # Активация буста
        if 'active_boosts' not in user:
            user['active_boosts'] = []
        
        boost_data = {
            'item_id': item_id,
            'boost_type': item.get('boost_type', 'xp'),
            'multiplier': item.get('multiplier', 2),
            'expires_at': (datetime.now() + timedelta(seconds=item['duration'])).isoformat()
        }
        
        user['active_boosts'].append(boost_data)
        
        hours = item['duration'] // 3600
        minutes = (item['duration'] % 3600) // 60
        time_str = f"{hours}ч" if hours > 0 else f"{minutes}м"
        
        result_message = convert_to_font(f"буст активирован на {time_str}!")
    
    elif item['category'] == 'cosmetics':
        user['inventory'].append(item_id)
        
        if item.get('cosmetic_type') == 'background':
            # Автоматически применяем фон
            if 'profile_settings' not in user:
                user['profile_settings'] = {}
            user['profile_settings']['background'] = item.get('value', '#0d0d0d')
            result_message = convert_to_font("фон профиля изменён!")
        elif item.get('cosmetic_type') == 'nickname':
            result_message = convert_to_font("используй !setnick [новый ник] для смены")
        else:
            result_message = convert_to_font("предмет добавлен в инвентарь!")
    
    elif item['category'] == 'special':
        special_type = item.get('special_type')
        
        if special_type == 'daily_reset':
            user['last_daily_date'] = None
            result_message = convert_to_font("кулдаун !daily сброшен!")
        
        elif special_type == 'rank_up':
            # Повышаем ранг на следующий уровень
            current_rank_id = user.get('rank_id', 1)
            all_ranks = db.get_all_ranks()
            
            if current_rank_id < len(all_ranks):
                # Переходим на следующий ранг
                user['rank_id'] = current_rank_id + 1
                new_rank = db.get_rank_info(user['rank_id'])
                
                # Устанавливаем XP на минимум для нового ранга
                user['xp'] = new_rank['required_xp']
                
                result_message = convert_to_font(f"ранг повышен до {new_rank['name']}!")
            else:
                # Уже максимальный ранг
                result_message = convert_to_font("у тебя уже максимальный ранг!")
        
        elif special_type == 'xp_instant':
            xp_amount = item.get('value', 1000)
            user['xp'] = user.get('xp', 0) + xp_amount
            db.check_rank_up(user)
            result_message = convert_to_font(f"+{xp_amount} xp получено!")
    
    db.save_user(str(ctx.author.id), user)
    
    embed = success_embed(
        title=convert_to_font(f"✅ куплено: {item['name']}"),
        description=result_message
    )
    embed.add_field(
        name=convert_to_font("💰 баланс"),
        value=convert_to_font(f"{user['coins']} монет"),
        inline=True
    )
    
    return True, embed

def get_inventory_embed(user, bot=None):
    """Создать embed инвентаря"""
    inventory = user.get('inventory', [])
    active_boosts = user.get('active_boosts', [])
    
    embed = BotTheme.create_embed(
        title=convert_to_font("🎒 твой инвентарь"),
        embed_type='profile'
    )
    
    # Предметы
    if inventory:
        items_text = []
        for item_id in inventory:
            item = find_item(item_id)
            if item:
                items_text.append(f"{item['emoji']} {convert_to_font(item['name'])}")
        
        if items_text:
            embed.add_field(
                name=convert_to_font("📦 предметы"),
                value='\n'.join(items_text),
                inline=False
            )
    
    # Активные бусты
    if active_boosts:
        boosts_text = []
        now = datetime.now()
        
        # Удаляем истёкшие бусты
        active_boosts = [b for b in active_boosts if datetime.fromisoformat(b['expires_at']) > now]
        user['active_boosts'] = active_boosts
        
        for boost in active_boosts:
            item = find_item(boost['item_id'])
            if item:
                expires = datetime.fromisoformat(boost['expires_at'])
                time_left = expires - now
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)
                time_str = f"{hours}ч {minutes}м" if hours > 0 else f"{minutes}м"
                
                boosts_text.append(
                    f"{item['emoji']} {convert_to_font(item['name'])} - {convert_to_font(time_str)}"
                )
        
        if boosts_text:
            embed.add_field(
                name=convert_to_font("⚡ активные бусты"),
                value='\n'.join(boosts_text),
                inline=False
            )
    
    # Баланс
    embed.add_field(
        name=convert_to_font("💰 монеты"),
        value=convert_to_font(str(user.get('coins', 0))),
        inline=True
    )
    
    if not inventory and not active_boosts:
        embed.description = convert_to_font("твой инвентарь пуст. посети !shop")
    
    return embed

def check_active_boosts(user):
    """Проверить и очистить истёкшие бусты"""
    if 'active_boosts' not in user:
        return {}
    
    now = datetime.now()
    active_boosts = []
    boost_multipliers = {}
    
    for boost in user['active_boosts']:
        expires = datetime.fromisoformat(boost['expires_at'])
        if expires > now:
            active_boosts.append(boost)
            boost_type = boost.get('boost_type', 'xp')
            multiplier = boost.get('multiplier', 1)
            
            if boost_type not in boost_multipliers:
                boost_multipliers[boost_type] = multiplier
            else:
                boost_multipliers[boost_type] = max(boost_multipliers[boost_type], multiplier)
    
    user['active_boosts'] = active_boosts
    
    return boost_multipliers

def apply_boost_to_reward(user, reward_type, amount):
    """Применить буст к награде"""
    boosts = check_active_boosts(user)
    
    if reward_type in boosts:
        multiplier = boosts[reward_type]
        boosted_amount = int(amount * multiplier)
        bonus = boosted_amount - amount
        return boosted_amount, bonus
    
    return amount, 0

# Инициализация магазина при первом запуске
if not os.path.exists(SHOP_FILE):
    save_shop_items(DEFAULT_SHOP_ITEMS)
    print("✅ Магазин инициализирован с предметами по умолчанию")
