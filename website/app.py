from flask import Flask, send_file, Response, jsonify
from flask_cors import CORS
import os
import sys
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для API запросов

# Get the directory where app.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# URL Discord бота для получения статистики
DISCORD_BOT_API_URL = os.getenv('DISCORD_BOT_API_URL', 'http://localhost:8080')

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
        # Пытаемся получить данные с API Discord бота
        response = requests.get(f'{DISCORD_BOT_API_URL}/api/stats', timeout=5)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            print(f"⚠️ Discord Bot API вернул статус {response.status_code}")
            return jsonify({
                'online_members': 0,
                'total_members': 0,
                'top_players': [],
                'error': f'Discord Bot API returned status {response.status_code}'
            }), 503
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения к Discord Bot API: {e}")
        # Возвращаем пустые данные если не можем подключиться
        return jsonify({
            'online_members': 0,
            'total_members': 0,
            'top_players': [],
            'error': f'Cannot connect to Discord Bot API: {str(e)}'
        }), 503
    except Exception as e:
        print(f"❌ Error in /api/stats: {e}")
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
