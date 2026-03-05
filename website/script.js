let currentUser = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadLeaderboard();
});

// Show section
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById(sectionId).classList.add('active');
    
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    if (sectionId === 'leaderboard') loadLeaderboard();
    if (sectionId === 'roulette') loadRoulette();
}

// Check auth
async function checkAuth() {
    try {
        const res = await fetch('/api/me', { credentials: 'include' });
        if (res.ok) {
            const data = await res.json();
            if (data.authenticated) {
                currentUser = data.user;
                updateUI();
                loadProfile();
            }
        }
    } catch (e) {
        console.error(e);
    }
}

// Update UI
function updateUI() {
    if (!currentUser) return;
    
    const avatar = currentUser.avatar 
        ? `https://cdn.discordapp.com/avatars/${currentUser.id}/${currentUser.avatar}.png`
        : 'https://cdn.discordapp.com/embed/avatars/0.png';
    
    document.getElementById('avatar').src = avatar;
    document.getElementById('username').textContent = currentUser.username;
    document.getElementById('tag').textContent = `${currentUser.username}#${currentUser.discriminator}`;
    document.getElementById('loginBtn').textContent = 'Профиль';
}

// Load profile
async function loadProfile() {
    if (!currentUser) return;
    
    try {
        const res = await fetch(`/api/user/${currentUser.id}`);
        const data = await res.json();
        
        if (data.success) {
            const user = data.user;
            const level = Math.floor(user.xp / 100) + 1;
            const xpInLevel = user.xp % 100;
            const progress = xpInLevel;
            
            document.getElementById('coins').textContent = user.coins || 0;
            document.getElementById('xp').textContent = user.xp || 0;
            document.getElementById('level').textContent = level;
            document.getElementById('rank').textContent = (user.rank_name || 'F-ранг').charAt(0);
            document.getElementById('xpBar').style.width = progress + '%';
            document.getElementById('xpText').textContent = `${xpInLevel} / 100 XP`;
        }
    } catch (e) {
        console.error(e);
    }
}

// Load leaderboard
async function loadLeaderboard() {
    try {
        const res = await fetch('/api/top/xp');
        const data = await res.json();
        
        if (data.success && data.players.length > 0) {
            document.getElementById('leaderboardList').innerHTML = data.players.map(p => `
                <div class="player-item">
                    <div class="player-rank">#${p.rank}</div>
                    <img class="player-avatar" src="${p.avatar || 'https://cdn.discordapp.com/embed/avatars/0.png'}" alt="${p.username}">
                    <div class="player-info">
                        <div class="player-name">${p.username}</div>
                        <div class="player-xp">${p.xp.toLocaleString()} XP • ${p.rank_name}</div>
                    </div>
                </div>
            `).join('');
        } else {
            document.getElementById('leaderboardList').innerHTML = '<div class="auth-message">Нет данных</div>';
        }
    } catch (e) {
        console.error(e);
    }
}

// Load roulette
function loadRoulette() {
    if (!currentUser) {
        document.getElementById('rouletteAuth').style.display = 'block';
        document.getElementById('rouletteGame').style.display = 'none';
    } else {
        document.getElementById('rouletteAuth').style.display = 'none';
        document.getElementById('rouletteGame').style.display = 'block';
    }
}

// Place bet
async function placeBet(color) {
    const bet = parseInt(document.getElementById('betAmount').value);
    if (!bet || bet < 10) {
        showResult('Минимальная ставка: 10 монет', 'lose');
        return;
    }
    
    const wheel = document.getElementById('wheel');
    wheel.classList.add('spin');
    wheel.textContent = '?';
    
    try {
        const res = await fetch('/api/roulette/play', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ user_id: currentUser.id, bet, color })
        });
        
        const data = await res.json();
        
        setTimeout(() => {
            wheel.classList.remove('spin');
            if (data.success) {
                wheel.textContent = data.number;
                if (data.win) {
                    showResult(`🎉 Выигрыш! +${data.win_amount} монет`, 'win');
                } else {
                    showResult(`😢 Проигрыш! -${bet} монет`, 'lose');
                }
                loadProfile();
            } else {
                showResult(data.error || 'Ошибка', 'lose');
            }
        }, 2000);
    } catch (e) {
        wheel.classList.remove('spin');
        showResult('Ошибка сервера', 'lose');
    }
}

// Show result
function showResult(msg, type) {
    const result = document.getElementById('result');
    result.textContent = msg;
    result.className = `result ${type}`;
    result.style.display = 'block';
    setTimeout(() => result.style.display = 'none', 5000);
}

// Login
function login() {
    if (currentUser) {
        showSection('profile');
    } else {
        window.location.href = '/api/auth/discord';
    }
}
