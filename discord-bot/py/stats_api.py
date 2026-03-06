"""
HTTP API для отдачи статистики Discord сервера
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import os
import logging
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)

# Отключаем логи Flask
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Глобальная переменная для хранения статистики
stats_data = {
    'online_members': 0,
    'total_members': 0,
    'top_players': [],
    'last_update': None
}

# Глобальная переменная для Discord бота
discord_bot = None

def set_bot(bot):
    """Установить ссылку на Discord бота"""
    global discord_bot
    discord_bot = bot
    print("✅ Discord бот подключен к Stats API")

@app.route('/api/stats')
def get_stats():
    """Отдаём статистику"""
    return jsonify(stats_data)

@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'ok'})

@app.route('/api/auth/exchange', methods=['POST'])
def exchange_code():
    """Exchange Discord OAuth code for user info"""
    try:
        data = request.get_json()
        code = data.get('code')
        redirect_uri = data.get('redirect_uri')
        
        if not code or not redirect_uri:
            return jsonify({'error': 'Missing code or redirect_uri'}), 400
        
        # Exchange code for token
        import requests as req
        token_url = 'https://discord.com/api/v10/oauth2/token'
        token_data = {
            'client_id': os.getenv('DISCORD_CLIENT_ID'),
            'client_secret': os.getenv('DISCORD_CLIENT_SECRET'),
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        token_response = req.post(token_url, data=token_data, headers=headers)
        token_response.raise_for_status()
        token_json = token_response.json()
        
        access_token = token_json['access_token']
        
        # Get user info
        user_response = req.get(
            'https://discord.com/api/v10/users/@me',
            headers={'Authorization': f"Bearer {access_token}"}
        )
        user_response.raise_for_status()
        user_data = user_response.json()
        
        return jsonify({
            'success': True,
            'user': user_data
        })
        
    except Exception as e:
        print(f"❌ OAuth exchange error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<user_id>')
def get_user(user_id):
    """Get user data"""
    try:
        from database_postgres import PostgresDatabase, RANKS
        db = PostgresDatabase()
        
        user = db.get_user(user_id)
        
        if user:
            rank_id = user.get('rank_id', 1)
            rank_name = RANKS[rank_id - 1]['name'] if rank_id <= len(RANKS) else 'F-ранг'
            
            return jsonify({
                'success': True,
                'user': {
                    'id': str(user['id']),
                    'username': user.get('username', 'Unknown'),
                    'xp': user.get('xp', 0),
                    'coins': user.get('coins', 0),
                    'clicks': user.get('clicks', 0),
                    'rank_id': rank_id,
                    'rank_name': rank_name
                }
            })
        else:
            return jsonify({'success': False, 'error': 'User not found'}), 404
            
    except Exception as e:
        print(f"❌ Error getting user: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/roulette/play', methods=['POST'])
def play_roulette():
    """Play roulette"""
    try:
        import random
        
        try:
            from database_postgres import PostgresDatabase
            db = PostgresDatabase()
        except Exception as db_error:
            print(f"⚠️ PostgreSQL unavailable: {db_error}")
            return jsonify({'success': False, 'error': 'База данных временно недоступна'}), 503
        
        data = request.get_json()
        user_id = data.get('user_id')
        bet = data.get('bet')
        color = data.get('color')
        
        if not user_id or not bet or not color:
            return jsonify({'success': False, 'error': 'Missing parameters'}), 400
        
        bet = int(bet)
        
        # Get user
        user = db.get_user(user_id)
        
        if not user or user.get('coins', 0) < bet:
            return jsonify({'success': False, 'error': 'Недостаточно монет'}), 400
        
        # Generate number (0-14)
        number = random.randint(0, 14)
        
        # Determine color
        if number == 0:
            result_color = 'green'
        elif number % 2 == 0:
            result_color = 'black'
        else:
            result_color = 'red'
        
        # Check win
        win = False
        win_amount = 0
        
        if color == result_color:
            win = True
            if color == 'green':
                win_amount = bet * 14
            else:
                win_amount = bet * 2
        
        # Update balance
        if win:
            new_coins = user['coins'] + win_amount - bet
        else:
            new_coins = user['coins'] - bet
        
        # Update user coins in database
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET coins = %s WHERE id = %s", (new_coins, str(user_id)))
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'number': number,
            'color': result_color,
            'win': win,
            'win_amount': win_amount if win else 0,
            'new_balance': new_coins
        })
        
    except Exception as e:
        print(f"❌ Roulette error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Ошибка сервера: {str(e)}'}), 500

def update_stats(data):
    """Обновить статистику"""
    global stats_data
    stats_data = data
    print(f"📊 Статистика обновлена: {data.get('online_members', 0)}/{data.get('total_members', 0)} онлайн, игроков: {len(data.get('top_players', []))}")

def run_api():
    """Запустить API сервер"""
    port = int(os.getenv('STATS_API_PORT', 5555))  # Изменён порт на 5555
    print(f"🌐 Flask API запускается на порту {port}...")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def start_api_server():
    """Запустить API в отдельном потоке"""
    try:
        print("🚀 Создание потока для Stats API...")
        thread = threading.Thread(target=run_api, daemon=True)
        print("✅ Поток создан, запускаем...")
        thread.start()
        print(f"✅ Stats API поток запущен (порт 5555)")
    except Exception as e:
        print(f"❌ Ошибка создания потока Stats API: {e}")
        import traceback
        traceback.print_exc()



@app.route('/api/wheel/spin', methods=['POST'])
def spin_wheel():
    """Wheel of Fortune - крутить колесо"""
    try:
        import random
        
        try:
            from database_postgres import PostgresDatabase
            db = PostgresDatabase()
        except Exception as db_error:
            print(f"⚠️ PostgreSQL unavailable: {db_error}")
            return jsonify({'success': False, 'error': 'База данных временно недоступна'}), 503
        
        data = request.json
        user_id = data.get('user_id')
        bet = data.get('bet', 0)
        
        if not user_id or bet < 10:
            return jsonify({'success': False, 'error': 'Неверные данные'}), 400
        
        # Get user
        user = db.get_user(user_id)
        
        if not user or user.get('coins', 0) < bet:
            return jsonify({'success': False, 'error': 'Недостаточно монет'}), 400
        
        # Wheel segments with probabilities
        # x0: 16.67% (2/12), x1.2: 25% (3/12), x1.5: 16.67% (2/12)
        # x2: 16.67% (2/12), x3: 8.33% (1/12), x5: 8.33% (1/12), x10: 8.33% (1/12)
        multipliers = [0, 1.2, 1.5, 2, 0, 3, 1.2, 5, 1.5, 2, 10, 1.2]
        
        # Random multiplier
        multiplier = random.choice(multipliers)
        
        # Calculate win
        win_amount = int(bet * multiplier)
        
        # Update balance
        new_coins = user['coins'] - bet + win_amount
        
        # Update user coins in database
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET coins = %s WHERE id = %s", (new_coins, str(user_id)))
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'multiplier': multiplier,
            'win_amount': win_amount,
            'new_balance': new_coins
        })
        
    except Exception as e:
        print(f"❌ Wheel error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# Shop roles configuration
SHOP_ROLES = [
    {
        'id': '1478224551287590983',  # ID роли в Discord
        'name': 'ᴅᴀʀᴋɴᴇss',
        'price': 5000,
        'color': '#FFD700',
        'emoji': '👑'
    },
    {
        'id': '1478208144319582312',
        'name': 'ʜᴜɴᴛᴇʀ',
        'price': 3500,
        'color': '#9370DB',
        'emoji': '💎'
    },
    {
        'id': '1478222910794502335',
        'name': 'ꜰʀᴇᴀᴋ',
        'price': 2500,
        'color': '#FF69B4',
        'emoji': '❤️'
    },
    {
        'id': '1478226541094637628',
        'name': 'ᴄᴀᴛ',
        'price': 1000,
        'color': '#00D4FF',
        'emoji': '🚀'
    }
]

# Градиентные цвета для покупки на сайте
GRADIENT_COLORS_SHOP = [
    {
        'id': 'sunset',
        'name': 'Sunset Gradient',
        'price': 2000,
        'color': '#FF6B35',
        'emoji': '🌅',
        'gradient': 'linear-gradient(45deg, #FF6B35, #F7931E)'
    },
    {
        'id': 'ocean',
        'name': 'Ocean Gradient',
        'price': 2000,
        'color': '#006994',
        'emoji': '🌊',
        'gradient': 'linear-gradient(45deg, #006994, #00A8CC)'
    },
    {
        'id': 'forest',
        'name': 'Forest Gradient',
        'price': 2000,
        'color': '#228B22',
        'emoji': '🌲',
        'gradient': 'linear-gradient(45deg, #228B22, #32CD32)'
    },
    {
        'id': 'galaxy',
        'name': 'Galaxy Gradient',
        'price': 2500,
        'color': '#4B0082',
        'emoji': '🌌',
        'gradient': 'linear-gradient(45deg, #4B0082, #8A2BE2)'
    },
    {
        'id': 'fire',
        'name': 'Fire Gradient',
        'price': 2500,
        'color': '#FF4500',
        'emoji': '🔥',
        'gradient': 'linear-gradient(45deg, #FF4500, #FF6347)'
    },
    {
        'id': 'ice',
        'name': 'Ice Gradient',
        'price': 2000,
        'color': '#87CEEB',
        'emoji': '❄️',
        'gradient': 'linear-gradient(45deg, #87CEEB, #B0E0E6)'
    },
    {
        'id': 'neon',
        'name': 'Neon Gradient',
        'price': 3000,
        'color': '#39FF14',
        'emoji': '💚',
        'gradient': 'linear-gradient(45deg, #39FF14, #00FF7F)'
    },
    {
        'id': 'plasma',
        'name': 'Plasma Gradient',
        'price': 3000,
        'color': '#FF1493',
        'emoji': '💖',
        'gradient': 'linear-gradient(45deg, #FF1493, #FF69B4)'
    },
    {
        'id': 'aurora',
        'name': 'Aurora Gradient',
        'price': 2500,
        'color': '#00CED1',
        'emoji': '🌈',
        'gradient': 'linear-gradient(45deg, #00CED1, #40E0D0)'
    },
    {
        'id': 'cosmic',
        'name': 'Cosmic Gradient',
        'price': 3500,
        'color': '#9370DB',
        'emoji': '🚀',
        'gradient': 'linear-gradient(45deg, #9370DB, #BA55D3)'
    }
]

@app.route('/api/shop/roles', methods=['GET'])
def get_shop_roles():
    """Получить список ролей в магазине"""
    try:
        user_id = request.args.get('user_id')
        
        print(f"🛒 Shop roles request for user: {user_id}")
        print(f"🤖 Discord bot connected: {discord_bot is not None}")
        
        if discord_bot:
            print(f"🤖 Bot guilds: {len(discord_bot.guilds) if discord_bot.guilds else 0}")
        
        roles = []
        for role in SHOP_ROLES:
            owned = False
            
            # Проверяем есть ли роль у пользователя
            if discord_bot and user_id:
                try:
                    guild = discord_bot.guilds[0] if discord_bot.guilds else None
                    if guild:
                        member = guild.get_member(int(user_id))
                        if member:
                            role_obj = guild.get_role(int(role['id']))
                            if role_obj and role_obj in member.roles:
                                owned = True
                                print(f"✅ User {user_id} owns role {role['name']}")
                except Exception as e:
                    print(f"⚠️ Error checking role {role['name']}: {e}")
            
            roles.append({
                **role,
                'owned': owned
            })
        
        print(f"✅ Returning {len(roles)} roles")
        response = jsonify({'success': True, 'roles': roles})
        print(f"✅ Response created: {response}")
        return response
        
    except Exception as e:
        print(f"❌ Shop roles error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/shop/buy', methods=['POST'])
def buy_role():
    """Купить роль"""
    try:
        try:
            from database_postgres import PostgresDatabase
            db = PostgresDatabase()
        except Exception as db_error:
            print(f"⚠️ PostgreSQL unavailable: {db_error}")
            return jsonify({'success': False, 'error': 'База данных временно недоступна'}), 503
        
        data = request.json
        user_id = data.get('user_id')
        role_id = data.get('role_id')
        
        if not user_id or not role_id:
            return jsonify({'success': False, 'error': 'Неверные данные'}), 400
        
        # Найти роль
        role = next((r for r in SHOP_ROLES if r['id'] == role_id), None)
        if not role:
            return jsonify({'success': False, 'error': 'Роль не найдена'}), 404
        
        # Получить пользователя
        user = db.get_user(user_id)
        if not user or user.get('coins', 0) < role['price']:
            return jsonify({'success': False, 'error': 'Недостаточно монет'}), 400
        
        # Проверить есть ли уже роль у пользователя и выдать её
        if discord_bot:
            try:
                guild = discord_bot.guilds[0] if discord_bot.guilds else None
                if guild:
                    member = guild.get_member(int(user_id))
                    if member:
                        role_obj = guild.get_role(int(role_id))
                        if role_obj:
                            if role_obj in member.roles:
                                return jsonify({'success': False, 'error': 'У вас уже есть эта роль'}), 400
                            
                            # Выдать роль
                            import asyncio
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(member.add_roles(role_obj, reason=f"Куплено в магазине за {role['price']} монет"))
                            loop.close()
                            print(f"✅ Роль {role['name']} выдана пользователю {member.name}")
                        else:
                            return jsonify({'success': False, 'error': 'Роль не найдена на сервере'}), 404
                    else:
                        return jsonify({'success': False, 'error': 'Пользователь не найден на сервере'}), 404
                else:
                    return jsonify({'success': False, 'error': 'Сервер не найден'}), 404
            except Exception as e:
                print(f"❌ Ошибка выдачи роли: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({'success': False, 'error': f'Ошибка выдачи роли: {str(e)}'}), 500
        else:
            return jsonify({'success': False, 'error': 'Бот не подключен'}), 500
        
        # Списать монеты
        new_coins = user['coins'] - role['price']
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET coins = %s WHERE id = %s", (new_coins, str(user_id)))
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'new_balance': new_coins,
            'role_name': role['name']
        })
        
    except Exception as e:
        print(f"❌ Buy role error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/shop/colors', methods=['GET'])
def get_shop_colors():
    """Получить список градиентных цветов в магазине"""
    try:
        from database_postgres import PostgresDatabase
        db = PostgresDatabase()
        
        user_id = request.args.get('user_id')
        
        print(f"🎨 Colors shop request for user: {user_id}")
        
        colors = []
        user_purchased_colors = []
        
        # Получаем список купленных цветов пользователя
        if user_id:
            user_data = db.get_user(user_id)
            user_purchased_colors = user_data.get('purchased_colors', [])
        
        for color in GRADIENT_COLORS_SHOP:
            owned = color['id'] in user_purchased_colors
            active = False
            
            # Проверяем активен ли цвет у пользователя (через кастомную роль)
            if discord_bot and user_id and owned:
                try:
                    guild = discord_bot.guilds[0] if discord_bot.guilds else None
                    if guild:
                        member = guild.get_member(int(user_id))
                        if member:
                            # Ищем роль с градиентным цветом
                            for role in member.roles:
                                if role.name.startswith("Custom Color") and role.color.value == int(color['color'].replace('#', '0x'), 16):
                                    active = True
                                    break
                except Exception as e:
                    print(f"⚠️ Error checking color {color['name']}: {e}")
            
            colors.append({
                **color,
                'owned': owned,
                'active': active
            })
        
        print(f"✅ Returning {len(colors)} gradient colors")
        return jsonify({'success': True, 'colors': colors})
        
    except Exception as e:
        print(f"❌ Shop colors error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/shop/buy-color', methods=['POST'])
def buy_color():
    """Купить градиентный цвет"""
    try:
        try:
            from database_postgres import PostgresDatabase
            db = PostgresDatabase()
        except Exception as db_error:
            print(f"⚠️ PostgreSQL unavailable: {db_error}")
            return jsonify({'success': False, 'error': 'База данных временно недоступна'}), 503
        
        data = request.json
        user_id = data.get('user_id')
        color_id = data.get('color_id')
        
        if not user_id or not color_id:
            return jsonify({'success': False, 'error': 'Неверные данные'}), 400
        
        # Найти цвет
        color = next((c for c in GRADIENT_COLORS_SHOP if c['id'] == color_id), None)
        if not color:
            return jsonify({'success': False, 'error': 'Цвет не найден'}), 404
        
        # Получить пользователя
        user = db.get_user(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'Пользователь не найден'}), 404
        
        # Проверяем есть ли уже цвет в купленных
        purchased_colors = user.get('purchased_colors', [])
        if color['id'] in purchased_colors:
            # Цвет уже куплен, просто активируем его
            pass
        else:
            # Проверяем баланс только если цвет не куплен
            if user.get('coins', 0) < color['price']:
                return jsonify({'success': False, 'error': 'Недостаточно монет'}), 400
        
        # Проверить есть ли уже цвет у пользователя и выдать его
        if discord_bot:
            try:
                guild = discord_bot.guilds[0] if discord_bot.guilds else None
                if guild:
                    member = guild.get_member(int(user_id))
                    if member:
                        color_value = int(color['color'].replace('#', '0x'), 16)
                        
                        # Проверяем есть ли уже такой цвет активен
                        for role in member.roles:
                            if role.name.startswith("Custom Color") and role.color.value == color_value:
                                return jsonify({'success': False, 'error': 'У вас уже активен этот цвет'}), 400
                        
                        # Создаём роль с градиентным цветом
                        import asyncio
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        # Удаляем старую цветную роль если есть
                        for role in member.roles:
                            if role.name.startswith("Custom Color"):
                                try:
                                    loop.run_until_complete(member.remove_roles(role, reason="Смена градиентного цвета"))
                                    loop.run_until_complete(role.delete(reason="Старая кастомная роль"))
                                except:
                                    pass
                        
                        # Создаём новую роль
                        new_role = loop.run_until_complete(guild.create_role(
                            name=f"Custom Color - {member.name}",
                            color=discord.Color(color_value),
                            reason=f"Куплен градиентный цвет {color['name']} за {color['price']} монет"
                        ))
                        
                        # Устанавливаем высокий приоритет
                        bot_member = guild.get_member(discord_bot.user.id)
                        if bot_member and bot_member.top_role:
                            target_position = min(bot_member.top_role.position - 1, len(guild.roles) - 1)
                            try:
                                loop.run_until_complete(new_role.edit(position=target_position))
                            except:
                                pass
                        
                        # Выдаём роль
                        loop.run_until_complete(member.add_roles(new_role, reason=f"Покупка градиентного цвета {color['name']}"))
                        loop.close()
                        
                        print(f"✅ Градиентный цвет {color['name']} выдан пользователю {member.name}")
                    else:
                        return jsonify({'success': False, 'error': 'Пользователь не найден на сервере'}), 404
                else:
                    return jsonify({'success': False, 'error': 'Сервер не найден'}), 404
            except Exception as e:
                print(f"❌ Ошибка выдачи градиентного цвета: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({'success': False, 'error': f'Ошибка выдачи цвета: {str(e)}'}), 500
        else:
            return jsonify({'success': False, 'error': 'Бот не подключен'}), 500
        
        # Обновляем данные пользователя
        purchased_colors = user.get('purchased_colors', [])
        new_coins = user.get('coins', 0)
        
        # Если цвет не был куплен ранее - списываем монеты и добавляем в купленные
        if color['id'] not in purchased_colors:
            new_coins -= color['price']
            purchased_colors.append(color['id'])
            user['purchased_colors'] = purchased_colors
            user['coins'] = new_coins
            db.save_user(user_id, user)
            print(f"✅ Цвет {color['name']} добавлен в купленные для пользователя {user_id}")
        
        return jsonify({
            'success': True,
            'new_balance': new_coins,
            'color_name': color['name'],
            'was_purchased': color['id'] not in purchased_colors
        })
        
    except Exception as e:
        print(f"❌ Buy color error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== ADMIN ENDPOINTS ====================

@app.route('/api/admin/give-xp', methods=['POST'])
def admin_give_xp():
    """Give XP to user (admin only)"""
    try:
        from database_postgres import PostgresDatabase
        db = PostgresDatabase()
        
        data = request.json
        user_id = data.get('user_id')
        xp_amount = data.get('xp_amount', 0)
        
        if not user_id or xp_amount <= 0:
            return jsonify({'success': False, 'error': 'Invalid parameters'}), 400
        
        # Get user
        user_data = db.get_user(user_id)
        if not user_data:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Add XP
        old_xp = user_data.get('xp', 0)
        old_rank_id = user_data.get('rank_id', 1)
        
        user_data['xp'] = old_xp + xp_amount
        
        # Check rank up
        new_rank_id = db.check_rank_up(user_data)
        db.save_user(user_id, user_data)
        
        return jsonify({
            'success': True,
            'old_xp': old_xp,
            'new_xp': user_data['xp'],
            'xp_added': xp_amount,
            'rank_up': new_rank_id > old_rank_id,
            'old_rank_id': old_rank_id,
            'new_rank_id': new_rank_id
        })
        
    except Exception as e:
        print(f"❌ Admin give XP error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/give-coins', methods=['POST'])
def admin_give_coins():
    """Give coins to user (admin only)"""
    try:
        from database_postgres import PostgresDatabase
        db = PostgresDatabase()
        
        data = request.json
        user_id = data.get('user_id')
        coins_amount = data.get('coins_amount', 0)
        
        if not user_id:
            return jsonify({'success': False, 'error': 'Invalid parameters'}), 400
        
        # Get user
        user_data = db.get_user(user_id)
        if not user_data:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Add coins (can be negative to remove coins)
        old_coins = user_data.get('coins', 0)
        user_data['coins'] = max(0, old_coins + coins_amount)  # Don't go below 0
        
        db.save_user(user_id, user_data)
        
        return jsonify({
            'success': True,
            'old_coins': old_coins,
            'new_coins': user_data['coins'],
            'coins_added': coins_amount
        })
        
    except Exception as e:
        print(f"❌ Admin give coins error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/get-user', methods=['GET'])
def admin_get_user():
    """Get user by username or ID (admin only)"""
    try:
        from database_postgres import PostgresDatabase
        db = PostgresDatabase()
        
        query = request.args.get('query', '').strip()
        
        if not query:
            return jsonify({'success': False, 'error': 'Query parameter required'}), 400
        
        # Try to find user by ID first
        if query.isdigit():
            user_data = db.get_user(query)
            if user_data:
                return jsonify({
                    'success': True,
                    'user': {
                        'id': user_data['id'],
                        'username': user_data.get('username', 'Unknown'),
                        'xp': user_data.get('xp', 0),
                        'coins': user_data.get('coins', 0),
                        'rank_id': user_data.get('rank_id', 1),
                        'games_played': user_data.get('games_played', 0),
                        'games_won': user_data.get('games_won', 0)
                    }
                })
        
        # Search by username
        all_users = db.get_all_users()
        found_users = []
        
        for user_id, user_data in all_users.items():
            username = user_data.get('username', '').lower()
            if query.lower() in username:
                found_users.append({
                    'id': user_data['id'],
                    'username': user_data.get('username', 'Unknown'),
                    'xp': user_data.get('xp', 0),
                    'coins': user_data.get('coins', 0),
                    'rank_id': user_data.get('rank_id', 1),
                    'games_played': user_data.get('games_played', 0),
                    'games_won': user_data.get('games_won', 0)
                })
        
        if found_users:
            return jsonify({
                'success': True,
                'users': found_users[:10]  # Limit to 10 results
            })
        else:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
    except Exception as e:
        print(f"❌ Admin get user error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500