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
        'name': 'VIP',
        'price': 5000,
        'color': '#FFD700',
        'emoji': '👑'
    },
    {
        'id': '1478208144319582312',
        'name': 'Premium',
        'price': 3500,
        'color': '#9370DB',
        'emoji': '💎'
    },
    {
        'id': '1478222910794502335',
        'name': 'Supporter',
        'price': 2500,
        'color': '#FF69B4',
        'emoji': '❤️'
    },
    {
        'id': '1478226541094637628',
        'name': 'Booster',
        'price': 1000,
        'color': '#00D4FF',
        'emoji': '🚀'
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

