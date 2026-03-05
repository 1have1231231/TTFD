"""
HTTP API для отдачи статистики Discord сервера
"""
from flask import Flask, jsonify
from flask_cors import CORS
import threading
import os

app = Flask(__name__)
CORS(app)

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

def run_api():
    """Запустить API сервер"""
    port = int(os.getenv('STATS_API_PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

def start_api_server():
    """Запустить API в отдельном потоке"""
    thread = threading.Thread(target=run_api, daemon=True)
    thread.start()
    print(f"✅ Stats API запущен на порту 8080")
