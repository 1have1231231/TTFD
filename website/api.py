"""
Simple API server for TTFD website
"""
from flask import Flask, jsonify, send_from_directory, redirect, request, session
from flask_cors import CORS
import os
import requests
from datetime import datetime
import secrets

app = Flask(__name__, static_folder='.')
app.secret_key = os.getenv('SESSION_SECRET', secrets.token_hex(32))
CORS(app, supports_credentials=True)

# Discord Bot API URL
DISCORD_BOT_API = os.getenv('DISCORD_BOT_API_URL', 'http://localhost:5555')

# Discord OAuth2
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI')
DISCORD_API_ENDPOINT = 'https://discord.com/api/v10'

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

@app.route('/api/auth/discord')
def discord_login():
    """Redirect to Discord OAuth2"""
    if not DISCORD_CLIENT_ID or not DISCORD_REDIRECT_URI:
        return jsonify({'error': 'Discord OAuth not configured'}), 500
    
    oauth_url = f"{DISCORD_API_ENDPOINT}/oauth2/authorize"
    params = {
        'client_id': DISCORD_CLIENT_ID,
        'redirect_uri': DISCORD_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'identify guilds'
    }
    
    auth_url = f"{oauth_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    return redirect(auth_url)

@app.route('/api/auth/discord/callback')
def discord_callback():
    """Handle Discord OAuth2 callback"""
    code = request.args.get('code')
    
    if not code:
        return redirect('/?error=no_code')
    
    # Exchange code for token
    token_url = f"{DISCORD_API_ENDPOINT}/oauth2/token"
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        response = requests.post(token_url, data=data, headers=headers)
        response.raise_for_status()
        token_data = response.json()
        
        access_token = token_data['access_token']
        
        # Get user info
        user_response = requests.get(
            f"{DISCORD_API_ENDPOINT}/users/@me",
            headers={'Authorization': f"Bearer {access_token}"}
        )
        user_response.raise_for_status()
        user_data = user_response.json()
        
        # Save to session
        session['user'] = {
            'id': user_data['id'],
            'username': user_data['username'],
            'discriminator': user_data.get('discriminator', '0'),
            'avatar': user_data.get('avatar'),
            'access_token': access_token
        }
        
        return redirect('/')
        
    except Exception as e:
        print(f"❌ Discord OAuth error: {e}")
        return redirect('/?error=auth_failed')

@app.route('/api/auth/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect('/')

@app.route('/api/me')
def get_me():
    """Get current user"""
    user = session.get('user')
    
    if not user:
        return jsonify({'authenticated': False}), 401
    
    return jsonify({
        'authenticated': True,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'discriminator': user['discriminator'],
            'avatar': user['avatar']
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    print(f"🚀 Starting TTFD Website API on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
