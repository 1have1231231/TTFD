from flask import Flask, send_file, Response, jsonify
from flask_cors import CORS
import os
import sys

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для API запросов

# Get the directory where app.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Импортируем Discord бота для получения статистики
sys.path.append(os.path.join(BASE_DIR, '..', 'discord-bot', 'py'))

# Глобальная переменная для хранения статистики
discord_stats = {
    'online_members': 0,
    'total_members': 0,
    'last_update': None
}

@app.route('/')
def index():
    return send_file(os.path.join(BASE_DIR, 'index.html'))

@app.route('/styles.css')
def styles():
    return send_file(os.path.join(BASE_DIR, 'styles.css'), mimetype='text/css')

@app.route('/script.js')
def script():
    return send_file(os.path.join(BASE_DIR, 'script.js'), mimetype='application/javascript')

@app.route('/api/stats')
def get_stats():
    """API endpoint для получения статистики Discord сервера"""
    try:
        import json
        stats_file = os.path.join(BASE_DIR, 'discord_stats.json')
        
        if os.path.exists(stats_file):
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
                return jsonify(stats)
        else:
            # Возвращаем пустые данные если файл не существует
            return jsonify({
                'online_members': 0,
                'total_members': 0,
                'top_players': [],
                'last_update': None,
                'error': 'Stats file not found - bot may not be running'
            })
    except Exception as e:
        print(f"Error in /api/stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'online_members': 0,
            'total_members': 0,
            'top_players': [],
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
