# Веб-сайт для бота
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash, send_from_directory
from datetime import datetime
from werkzeug.utils import secure_filename
import config
import os
import uuid

# Пытаемся использовать PostgreSQL, если нет - JSON
try:
    from database_postgres import db, RANKS
    print("✅ Используется PostgreSQL")
except Exception as e:
    from database import db, RANKS
    print(f"⚠️ Используется JSON файл: {e}")

from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

# Настройки загрузки файлов
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'svg'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov', 'avi'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'mpeg', 'wav', 'ogg', 'flac'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Создаём папки для загрузок
os.makedirs(os.path.join(UPLOAD_FOLDER, 'avatars'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'music'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'backgrounds'), exist_ok=True)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Данные бота (будут обновляться из main.py)
bot_data = {
    'status': 'offline',
    'uptime': 0,
    'guilds': 0,
    'users': 0,
    'commands_used': 0,
    'messages_seen': 0,
    'latency': 0,
    'online_members': [],
}

@app.route('/landing')
def landing():
    """Modern landing page"""
    return render_template('landing.html')

@app.route('/landing-pro')
def landing_pro():
    """Modern landing page PRO with advanced features"""
    return render_template('landing_pro.html')

@app.route('/landing-premium')
def landing_premium():
    """Premium landing page - guns.lol style"""
    return render_template('landing_premium.html')

@app.route('/clan')
def clan():
    """TTFD Clan Website - Elite esports style"""
    return send_from_directory('website', 'index.html')

@app.route('/test-design')
def test_design():
    """Тестовая страница для проверки дизайна"""
    return render_template('test_design.html')

@app.route('/website/<path:filename>')
def website_static(filename):
    """Serve static files for clan website"""
    return send_from_directory('website', filename)

@app.route('/')
def index():
    """Главная страница"""
    current_user = None
    if 'token' in session:
        current_user = db.get_account_by_token(session['token'])
    return render_template('index.html', bot_data=bot_data, current_user=current_user)

@app.route('/games')
def games():
    """Страница со списком игр"""
    current_user = None
    if 'token' in session:
        current_user = db.get_account_by_token(session['token'])
    return render_template('games.html', current_user=current_user)

@app.route('/game')
def game():
    """Страница кликера (старая игра)"""
    current_user = None
    if 'token' in session:
        current_user = db.get_account_by_token(session['token'])
    return render_template('game.html', current_user=current_user)

@app.route('/clicker')
def clicker():
    """Кликер с фиолетовым градиентом"""
    current_user = None
    if 'token' in session:
        current_user = db.get_account_by_token(session['token'])
    return render_template('game.html', current_user=current_user)

@app.route('/snake')
def snake():
    """Страница игры Змейка"""
    current_user = None
    if 'token' in session:
        current_user = db.get_account_by_token(session['token'])
    return render_template('snake.html', current_user=current_user)

@app.route('/leaderboard')
def leaderboard():
    """Таблица лидеров"""
    leaders = db.get_leaderboard(50)
    # Фильтруем Unknown пользователей
    leaders = [user for user in leaders if user.get('username') != 'Unknown']
    
    current_user = None
    if 'token' in session:
        current_user = db.get_account_by_token(session['token'])
    return render_template('leaderboard.html', leaders=leaders, ranks=RANKS, current_user=current_user)

@app.route('/ranks')
def ranks():
    """Список всех рангов"""
    current_user = None
    if 'token' in session:
        current_user = db.get_account_by_token(session['token'])
    return render_template('ranks.html', ranks=RANKS, current_user=current_user)

@app.route('/users')
def users():
    """Список всех пользователей"""
    try:
        # Получаем всех пользователей через универсальный метод
        all_users = db.get_all_accounts()
        
        current_user = None
        if 'token' in session:
            current_user = db.get_account_by_token(session['token'])
        
        return render_template('users.html', users=all_users, current_user=current_user)
    except Exception as e:
        print(f"❌ Ошибка на странице /users: {e}")
        import traceback
        traceback.print_exc()
        return f"Ошибка: {str(e)}", 500

# ==================== АУТЕНТИФИКАЦИЯ ====================

# Регистрация через почту УДАЛЕНА - используется только Discord OAuth

@app.route('/login')
def login():
    """Страница входа - перенаправляет на Discord OAuth"""
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Выход"""
    if 'token' in session:
        db.logout(session['token'])
        session.pop('token', None)
    flash('Вы вышли из аккаунта', 'info')
    return redirect(url_for('index'))

# ==================== ПРОФИЛИ ====================

@app.route('/profile/<username>')
def profile(username):
    """Публичный профиль пользователя"""
    account = db.get_account_by_username(username)
    if not account:
        return "Пользователь не найден", 404
    
    # Получаем игровые данные если привязан Discord
    game_data = None
    if account.get('discord_id'):
        game_data = db.get_user(account['discord_id'])
    
    current_user = None
    if 'token' in session:
        current_user = db.get_account_by_token(session['token'])
    
    return render_template('profile.html', account=account, game_data=game_data, current_user=current_user, ranks=RANKS)

@app.route('/settings')
def settings():
    """Настройки профиля"""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    current_user = db.get_account_by_token(session['token'])
    if not current_user:
        return redirect(url_for('login'))
    
    return render_template('settings_premium.html', current_user=current_user)

@app.route('/api/update_profile', methods=['POST'])
def api_update_profile():
    """API: обновить профиль"""
    if 'token' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    account = db.get_account_by_token(session['token'])
    if not account:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    data = request.json
    result = db.update_profile(account['id'], **data)
    return jsonify(result)

@app.route('/api/change_password', methods=['POST'])
def api_change_password():
    """API: сменить пароль - ОТКЛЮЧЕНО (используется Discord OAuth)"""
    return jsonify({'success': False, 'error': 'Смена пароля недоступна при входе через Discord'}), 403

@app.route('/api/link_discord', methods=['POST'])
def api_link_discord():
    """API: привязать Discord ID"""
    if 'token' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    account = db.get_account_by_token(session['token'])
    if not account:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    data = request.json
    result = db.link_discord(account['id'], data.get('discord_id'))
    return jsonify(result)

@app.route('/api/upload_avatar', methods=['POST'])
def api_upload_avatar():
    """API: загрузить аватарку"""
    if 'token' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    account = db.get_account_by_token(session['token'])
    if not account:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    if 'avatar' not in request.files:
        return jsonify({'success': False, 'error': 'Файл не найден'}), 400
    
    file = request.files['avatar']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Файл не выбран'}), 400
    
    if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        return jsonify({'success': False, 'error': 'Недопустимый формат файла. Используй PNG, JPG, GIF'}), 400
    
    # Генерируем уникальное имя файла
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{account['id']}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, 'avatars', filename)
    
    try:
        file.save(filepath)
        avatar_url = f"/static/uploads/avatars/{filename}"
        
        # Обновляем профиль
        result = db.update_profile(account['id'], avatar_url=avatar_url)
        
        if result['success']:
            return jsonify({'success': True, 'avatar_url': avatar_url})
        else:
            return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Ошибка загрузки: {str(e)}'}), 500

@app.route('/api/upload_music', methods=['POST'])
def api_upload_music():
    """API: загрузить музыку"""
    if 'token' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    account = db.get_account_by_token(session['token'])
    if not account:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    if 'music' not in request.files:
        return jsonify({'success': False, 'error': 'Файл не найден'}), 400
    
    file = request.files['music']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Файл не выбран'}), 400
    
    if not allowed_file(file.filename, ALLOWED_AUDIO_EXTENSIONS):
        return jsonify({'success': False, 'error': 'Недопустимый формат файла. Используй MP3'}), 400
    
    # Генерируем уникальное имя файла
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{account['id']}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, 'music', filename)
    
    try:
        file.save(filepath)
        music_url = f"/static/uploads/music/{filename}"
        
        # Обновляем профиль
        result = db.update_profile(account['id'], music_url=music_url)
        
        if result['success']:
            return jsonify({'success': True, 'music_url': music_url})
        else:
            return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Ошибка загрузки: {str(e)}'}), 500

@app.route('/api/upload_background', methods=['POST'])
def api_upload_background():
    """API: загрузить background (изображение, видео или GIF)"""
    if 'token' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    account = db.get_account_by_token(session['token'])
    if not account:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    if 'background' not in request.files:
        return jsonify({'success': False, 'error': 'Файл не найден'}), 400
    
    file = request.files['background']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Файл не выбран'}), 400
    
    # Проверяем формат файла
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if ext in ALLOWED_IMAGE_EXTENSIONS:
        file_type = 'image'
    elif ext in ALLOWED_VIDEO_EXTENSIONS:
        file_type = 'video'
    else:
        allowed = ', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS))
        return jsonify({'success': False, 'error': f'Недопустимый формат. Используй: {allowed}'}), 400
    
    # Генерируем уникальное имя файла
    filename = f"{account['id']}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, 'backgrounds', filename)
    
    try:
        file.save(filepath)
        background_url = f"/static/uploads/backgrounds/{filename}"
        
        # Обновляем профиль
        result = db.update_profile(account['id'], background_url=background_url, background_type=file_type)
        
        if result['success']:
            return jsonify({'success': True, 'background_url': background_url, 'background_type': file_type})
        else:
            return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Ошибка загрузки: {str(e)}'}), 500

@app.route('/api/upload_profile_bg', methods=['POST'])
def api_upload_profile_bg():
    """API: загрузить фон профиля"""
    if 'token' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    account = db.get_account_by_token(session['token'])
    if not account:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    if 'profile_bg' not in request.files:
        return jsonify({'success': False, 'error': 'Файл не найден'}), 400
    
    file = request.files['profile_bg']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Файл не выбран'}), 400
    
    if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        return jsonify({'success': False, 'error': 'Недопустимый формат файла. Используй JPG, PNG, GIF'}), 400
    
    # Генерируем уникальное имя файла
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{account['id']}_profile_bg_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, 'backgrounds', filename)
    
    try:
        file.save(filepath)
        profile_bg_url = f"/static/uploads/backgrounds/{filename}"
        
        # Обновляем профиль
        result = db.update_profile(account['id'], profile_bg_url=profile_bg_url)
        
        if result['success']:
            return jsonify({'success': True, 'profile_bg_url': profile_bg_url})
        else:
            return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Ошибка загрузки: {str(e)}'}), 500

# ==================== API ====================

@app.route('/api/stats')
def api_stats():
    """API: статистика бота"""
    return jsonify(bot_data)

@app.route('/api/status')
def api_status():
    """API: статус бота"""
    return jsonify({
        'status': bot_data['status'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/online')
def api_online():
    """API: онлайн пользователи"""
    return jsonify({
        'count': len(bot_data['online_members']),
        'members': bot_data['online_members']
    })

@app.route('/api/user/<user_id>')
def api_user(user_id):
    """API: данные пользователя"""
    user = db.get_user(user_id)
    rank = db.get_rank_info(user['rank_id'])
    
    # Следующий ранг
    next_rank = None
    if user['rank_id'] < len(RANKS):
        next_rank = RANKS[user['rank_id']]
    
    # Ищем аккаунт с этим Discord ID
    account = None
    for acc in db.accounts.get('accounts', {}).values():
        if acc.get('discord_id') == user_id:
            account = acc
            break
    
    return jsonify({
        'user': user,
        'rank': rank,
        'next_rank': next_rank,
        'account': account
    })

@app.route('/api/user_by_discord/<discord_id>')
def api_user_by_discord(discord_id):
    """API: получить username по Discord ID"""
    try:
        print(f"🔍 Поиск аккаунта для Discord ID: {discord_id}")
        
        # Ищем аккаунт с этим Discord ID через универсальный метод
        all_accounts = db.get_all_accounts()
        for acc in all_accounts:
            if str(acc.get('discord_id')) == str(discord_id):
                print(f"✅ Найден аккаунт: {acc.get('username')}")
                return jsonify({
                    'success': True,
                    'username': acc.get('username'),
                    'has_account': True
                })
        
        # Если аккаунта нет, возвращаем Discord данные
        print(f"❌ Аккаунт не найден для Discord ID: {discord_id}")
        user = db.get_user(discord_id)
        if user:
            username = user.get('username', 'Unknown')
        else:
            username = 'Unknown'
        
        return jsonify({
            'success': True,
            'username': username,
            'has_account': False
        })
    except Exception as e:
        print(f"❌ Ошибка в api_user_by_discord: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'has_account': False
        }), 500

@app.route('/api/click', methods=['POST'])
def api_click():
    """API: обработка клика в игре"""
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    # Получаем пользователя
    user = db.get_user(user_id)
    
    # Обновляем клики
    new_clicks = user['clicks'] + 1
    db.update_user(user_id, clicks=new_clicks)
    
    # Даём 1 XP за клик
    xp_result = db.add_xp(user_id, 1)
    
    # Получаем обновлённые данные
    user = db.get_user(user_id)
    
    # Обновляем прогресс заданий на основе общего количества кликов
    daily_tasks = user['daily_tasks']
    for task in daily_tasks:
        if not task['completed'] and 'клик' in task['name'].lower():
            # Используем общее количество кликов как прогресс
            task['progress'] = min(user['clicks'], task['target'])
    
    # Сохраняем обновлённые задания
    db.update_user(user_id, daily_tasks=daily_tasks)
    
    return jsonify({
        'success': True,
        'clicks': user['clicks'],
        'xp': user['xp'],
        'coins': user['coins'],
        'rank_up': xp_result['rank_up'],
        'new_rank': db.get_rank_info(xp_result['new_rank']) if xp_result['rank_up'] else None
    })

@app.route('/api/tasks/<user_id>')
def api_tasks(user_id):
    """API: получить задания пользователя"""
    user = db.get_user(user_id)
    return jsonify({
        'tasks': user['daily_tasks']
    })

@app.route('/api/complete_task', methods=['POST'])
def api_complete_task():
    """API: завершить задание"""
    data = request.json
    user_id = data.get('user_id')
    task_id = data.get('task_id')
    
    if not user_id or not task_id:
        return jsonify({'error': 'user_id and task_id required'}), 400
    
    result = db.complete_task(user_id, task_id)
    return jsonify(result)

@app.route('/api/leaderboard')
def api_leaderboard():
    """API: таблица лидеров"""
    leaders = db.get_leaderboard(50)
    return jsonify({
        'leaders': leaders,
        'ranks': RANKS
    })

@app.route('/api/ranks')
def api_ranks():
    """API: все ранги"""
    return jsonify({
        'ranks': RANKS
    })

def update_bot_data(data):
    """Обновить данные бота"""
    global bot_data
    bot_data.update(data)

def run_web():
    """Запуск веб-сервера"""
    print(f"🌐 Веб-сервер запущен на http://localhost:{config.WEB_PORT}")
    app.run(host='0.0.0.0', port=config.WEB_PORT, debug=False)

if __name__ == "__main__":
    run_web()


# ==================== DISCORD OAUTH ====================

from discord_oauth import get_oauth_url, handle_oauth_callback

@app.route('/auth/discord')
def auth_discord():
    """Начать авторизацию через Discord"""
    try:
        oauth_url = get_oauth_url()
        if not oauth_url:
            print("❌ Discord OAuth не настроен")
            flash('Discord OAuth не настроен. Обратитесь к администратору.', 'error')
            return redirect(url_for('login'))
        
        print(f"✅ Редирект на Discord OAuth: {oauth_url[:50]}...")
        return redirect(oauth_url)
    except Exception as e:
        print(f"❌ Ошибка при создании OAuth URL: {e}")
        flash('Ошибка при подключении к Discord', 'error')
        return redirect(url_for('login'))

@app.route('/auth/discord/callback')
def auth_discord_callback():
    """Обработать callback от Discord"""
    try:
        # Проверяем наличие ошибки от Discord
        error = request.args.get('error')
        if error:
            error_description = request.args.get('error_description', 'Unknown error')
            print(f"❌ Discord OAuth error: {error} - {error_description}")
            flash(f'Ошибка Discord: {error_description}', 'error')
            return redirect(url_for('login'))
        
        print("📥 Получен callback от Discord")
        print(f"   State: {request.args.get('state')[:20]}...")
        print(f"   Code: {request.args.get('code')[:20] if request.args.get('code') else 'None'}...")
        
        result = handle_oauth_callback(db)
        
        if result['success']:
            session['token'] = result['token']
            if result['is_new']:
                print(f"✅ Создан новый аккаунт: {result['account']['display_name']}")
                flash(f'Добро пожаловать, {result["account"]["display_name"]}!', 'success')
            elif result.get('was_linked'):
                print(f"🔗 Discord привязан к аккаунту: {result['account']['display_name']}")
                flash(f'Discord успешно привязан! С возвращением, {result["account"]["display_name"]}!', 'success')
            else:
                print(f"✅ Вход выполнен: {result['account']['display_name']}")
                flash(f'С возвращением, {result["account"]["display_name"]}!', 'success')
            return redirect(url_for('index'))
        else:
            error_msg = result.get('error', 'Unknown error')
            print(f"❌ OAuth failed: {error_msg}")
            flash(f'Ошибка авторизации: {error_msg}', 'error')
            return redirect(url_for('login'))
    except Exception as e:
        print(f"❌ Критическая ошибка в OAuth callback: {e}")
        import traceback
        traceback.print_exc()
        flash('Произошла ошибка при авторизации', 'error')
        return redirect(url_for('login'))
