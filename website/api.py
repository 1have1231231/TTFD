"""
Simple API server for TTFD website
"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
from datetime import datetime

app = Flask(__name__, static_folder='.')
CORS(app)

# Discord Bot API URL
DISCORD_BOT_API = os.getenv('DISCORD_BOT_API_URL', 'http://localhost:5555')

@app.route('/')
def index():
    """Serve index.html"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('.', path)

@app.route('/api/top/xp')
def get_top_xp():
    """Get TOP-3 players by XP from Discord bot"""
    try:
        # Get data from Discord bot API
        response = requests.get(f'{DISCORD_BOT_API}/api/stats', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            top_players = data.get('top_players', [])[:3]  # TOP-3
            
            # Format response
            result = []
            for idx, player in enumerate(top_players, 1):
                result.append({
                    'rank': idx,
                    'username': player.get('display_name', player.get('name', 'Unknown')),
                    'xp': player.get('xp', 0),
                    'avatar': player.get('avatar_url', ''),
                    'rank_name': player.get('rank', 'F-ранг')
                })
            
            return jsonify({
                'success': True,
                'players': result,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Discord bot API unavailable',
                'players': []
            }), 503
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to Discord Bot API: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'players': []
        }), 503

@app.route('/api/stats')
def get_stats():
    """Get server stats from Discord bot"""
    try:
        response = requests.get(f'{DISCORD_BOT_API}/api/stats', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'success': True,
                'online_members': data.get('online_members', 0),
                'total_members': data.get('total_members', 0),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Discord bot API unavailable'
            }), 503
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 503

@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    print(f"🚀 Starting TTFD Website API on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
