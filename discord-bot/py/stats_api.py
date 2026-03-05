"""
HTTP API для отдачи статистики Discord сервера
"""
from flask import Flask, jsonify
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

def update_stats(data):
    """Обновить статистику"""
    global stats_data
    stats_data = data
    print(f"📊 Статистика обновлена: {data.get('online_members', 0)}/{data.get('total_members', 0)} онлайн, игроков: {len(data.get('top_players', []))}")

def run_api():
    """Запустить API сервер"""
    port = int(os.getenv('STATS_API_PORT', 8080))
    print(f"🌐 Flask API запускается на порту {port}...")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def start_api_server():
    """Запустить API в отдельном потоке"""
    try:
        print("🚀 Создание потока для Stats API...")
        thread = threading.Thread(target=run_api, daemon=True)
        print("✅ Поток создан, запускаем...")
        thread.start()
        print(f"✅ Stats API поток запущен (порт 8080)")
    except Exception as e:
        print(f"❌ Ошибка создания потока Stats API: {e}")
        import traceback
        traceback.print_exc()

