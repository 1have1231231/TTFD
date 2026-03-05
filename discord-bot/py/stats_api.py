"""
HTTP API для отдачи статистики Discord сервера
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import os
import logging

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

