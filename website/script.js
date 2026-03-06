let currentUser = null;

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadLeaderboard();
});

function showSection(id) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    event.target.classList.add('active');
    
    if (id === 'leaderboard') loadLeaderboard();
    if (id === 'roulette') loadRoulette();
}

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

function updateUI() {
    if (!currentUser) return;
    
    const avatar = currentUser.avatar 
        ? `https://cdn.discordapp.com/avatars/${currentUser.id}/${currentUser.avatar}.png`
        : 'https://cdn.discordapp.com/embed/avatars/0.png';
    
    document.getElementById('profileAvatar').src = avatar;
    document.getElementById('profileName').textContent = currentUser.username;
    document.getElementById('profileTag').textContent = `${currentUser.username}#${currentUser.discriminator}`;
    
    const userSection = document.querySelector('.user-section');
    userSection.innerHTML = `
        <div class="user-info">
            <img src="${avatar}" class="user-avatar" alt="Avatar">
            <div>
                <div class="user-name">${currentUser.username}</div>
                <div class="user-coins" id="headerCoins">0 монет</div>
            </div>
        </div>
    `;
}

async function loadProfile() {
    if (!currentUser) return;
    
    try {
        const res = await fetch(`/api/user/${currentUser.id}`);
        const data = await res.json();
        
        if (data.success) {
            const user = data.user;
            const level = Math.floor(user.xp / 100) + 1;
            const xpInLevel = user.xp % 100;
            
            document.getElementById('statCoins').textContent = user.coins || 0;
            document.getElementById('statXP').textContent = user.xp || 0;
            document.getElementById('statLevel').textContent = level;
            const rankName = user.rank_name || 'F-ранг';
            const rankLetter = rankName.includes('-') ? rankName.split('-')[0] : rankName.charAt(0);
            document.getElementById('statRank').textContent = rankLetter;
            
            document.getElementById('levelBadge').textContent = level;
            document.getElementById('currentLevel').textContent = level;
            document.getElementById('currentXP').textContent = xpInLevel;
            document.getElementById('nextXP').textContent = 100;
            document.getElementById('xpFill').style.width = xpInLevel + '%';
            
            const headerCoins = document.getElementById('headerCoins');
            if (headerCoins) headerCoins.textContent = `${user.coins || 0} монет`;
        }
    } catch (e) {
        console.error(e);
    }
}

async function loadLeaderboard() {
    const container = document.getElementById('topPlayers');
    container.innerHTML = '<div class="auth-msg">Загрузка...</div>';
    
    try {
        const res = await fetch('/api/top/xp');
        const data = await res.json();
        
        if (data.success && data.players.length > 0) {
            const top3 = data.players.slice(0, 3);
            const ordered = top3.length === 3 ? [top3[1], top3[0], top3[2]] : top3;
            
            container.innerHTML = ordered.map(p => {
                const isTop1 = p.rank === 1;
                return `
                    <div class="player-card ${isTop1 ? 'top-1' : ''}">
                        <div class="rank-badge">#${p.rank}</div>
                        <img src="${p.avatar || 'https://cdn.discordapp.com/embed/avatars/0.png'}" 
                             class="player-avatar-large" alt="${p.username}">
                        <div class="player-name">${p.username}</div>
                        <div class="player-level">${p.rank_name}</div>
                        <div class="player-xp">${p.xp.toLocaleString()} XP</div>
                    </div>
                `;
            }).join('');
        } else {
            container.innerHTML = '<div class="auth-msg">Нет данных</div>';
        }
    } catch (e) {
        console.error(e);
        container.innerHTML = '<div class="auth-msg">Ошибка загрузки</div>';
    }
}

function loadRoulette() {
    if (!currentUser) {
        document.getElementById('rouletteAuth').style.display = 'block';
        document.getElementById('rouletteGame').style.display = 'none';
    } else {
        document.getElementById('rouletteAuth').style.display = 'none';
        document.getElementById('rouletteGame').style.display = 'block';
        updateRouletteBalance();
    }
}

async function updateRouletteBalance() {
    try {
        const res = await fetch(`/api/user/${currentUser.id}`);
        const data = await res.json();
        if (data.success) {
            document.getElementById('rouletteBalance').textContent = data.user.coins || 0;
        }
    } catch (e) {
        console.error(e);
    }
}

async function placeBet(color) {
    const bet = parseInt(document.getElementById('betAmount').value);
    if (!bet || bet < 10) {
        showResult('Минимальная ставка: 10 монет', 'lose');
        return;
    }
    
    const wheel = document.getElementById('wheel');
    const wheelResult = document.getElementById('wheelResult');
    const resultNumber = document.getElementById('resultNumber');
    const buttons = document.querySelectorAll('.bet-btn');
    buttons.forEach(btn => btn.disabled = true);
    
    // Скрыть предыдущий результат
    wheelResult.style.display = 'none';
    
    // Запустить вращение
    wheel.classList.add('spinning');
    
    try {
        const res = await fetch('/api/roulette/play', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ user_id: currentUser.id, bet, color })
        });
        
        const data = await res.json();
        
        setTimeout(() => {
            wheel.classList.remove('spinning');
            
            if (data.success) {
                // Показать результат
                resultNumber.textContent = data.number;
                wheelResult.style.display = 'flex';
                
                // Скрыть результат через 2 секунды
                setTimeout(() => {
                    wheelResult.style.display = 'none';
                }, 2000);
                
                if (data.win) {
                    showResult(`🎉 Выигрыш! +${data.win_amount} монет`, 'win');
                } else {
                    showResult(`😢 Проигрыш! -${bet} монет`, 'lose');
                }
                
                updateRouletteBalance();
                loadProfile();
            } else {
                showResult(data.error || 'Ошибка', 'lose');
            }
            
            buttons.forEach(btn => btn.disabled = false);
        }, 3000);
    } catch (e) {
        console.error(e);
        wheel.classList.remove('spinning');
        wheelResult.style.display = 'none';
        showResult('Ошибка сервера', 'lose');
        buttons.forEach(btn => btn.disabled = false);
    }
}

function showResult(msg, type) {
    const result = document.getElementById('result');
    result.textContent = msg;
    result.className = `result-box ${type}`;
    result.style.display = 'block';
    setTimeout(() => result.style.display = 'none', 5000);
}

function login() {
    if (currentUser) {
        showSection('profile');
    } else {
        window.location.href = '/api/auth/discord';
    }
}
