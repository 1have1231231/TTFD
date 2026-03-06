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
    if (id === 'shop') loadShop();
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
    
    try {
        const res = await fetch('/api/roulette/play', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ user_id: currentUser.id, bet, color })
        });
        
        const data = await res.json();
        
        if (data.success) {
            // Вычисляем угол для остановки на выигрышном числе
            const sectorAngle = 24;
            const numberAngle = data.number * sectorAngle;
            const targetAngle = 180 - numberAngle;
            const spins = 5;
            const finalAngle = (360 * spins) + targetAngle;
            
            wheel.style.transition = 'transform 3s cubic-bezier(0.17, 0.67, 0.12, 0.99)';
            wheel.style.transform = `rotate(${finalAngle}deg)`;
            
            setTimeout(() => {
                resultNumber.textContent = data.number;
                wheelResult.style.display = 'flex';
                
                setTimeout(() => {
                    wheelResult.style.display = 'none';
                }, 2500);
                
                if (data.win) {
                    showResult(`🎉 Выигрыш! +${data.win_amount} монет`, 'win');
                } else {
                    showResult(`😢 Проигрыш! -${bet} монет`, 'lose');
                }
                
                updateRouletteBalance();
                loadProfile();
                buttons.forEach(btn => btn.disabled = false);
            }, 3000);
        } else {
            showResult(data.error || 'Ошибка', 'lose');
            buttons.forEach(btn => btn.disabled = false);
        }
    } catch (e) {
        console.error(e);
        showResult('Ошибка сервера', 'lose');
        buttons.forEach(btn => btn.disabled = false);
    }
}
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
    
    try {
        const res = await fetch('/api/roulette/play', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ user_id: currentUser.id, bet, color })
        });
        
        const data = await res.json();
        
        if (data.success) {
            // Вычисляем угол для остановки на выигрышном числе
            // 15 секторов, каждый 24°, 0 находится сверху
            // Стрелка внизу, поэтому нужно повернуть на 180° + угол сектора
            const sectorAngle = 24; // градусов на сектор
            const numberAngle = data.number * sectorAngle; // угол числа от 0
            const targetAngle = 180 - numberAngle; // чтобы число оказалось внизу
            const spins = 5; // количество полных оборотов
            const finalAngle = (360 * spins) + targetAngle;
            
            // Применяем вращение
            wheel.style.transition = 'transform 3s cubic-bezier(0.17, 0.67, 0.12, 0.99)';
            wheel.style.transform = `rotate(${finalAngle}deg)`;
            
            setTimeout(() => {
                // Показать результат
                resultNumber.textContent = data.number;
                wheelResult.style.display = 'flex';
                
                // Скрыть результат через 2 секунды
                setTimeout(() => {
                    wheelResult.style.display = 'none';
                }, 2500);
                
                if (data.win) {
                    showResult(`🎉 Выигрыш! +${data.win_amount} монет`, 'win');
                } else {
                    showResult(`😢 Проигрыш! -${bet} монет`, 'lose');
                }
                
                updateRouletteBalance();
                loadProfile();
                buttons.forEach(btn => btn.disabled = false);
            }, 3000);
        } else {
            showResult(data.error || 'Ошибка', 'lose');
            buttons.forEach(btn => btn.disabled = false);
        }
    } catch (e) {
        console.error(e);
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


// Shop functions
function loadShop() {
    if (!currentUser) {
        document.getElementById('shopAuth').style.display = 'block';
        document.getElementById('shopContent').style.display = 'none';
    } else {
        document.getElementById('shopAuth').style.display = 'none';
        document.getElementById('shopContent').style.display = 'block';
        loadShopItems();
        updateShopBalance();
    }
}

async function updateShopBalance() {
    try {
        const res = await fetch(`/api/user/${currentUser.id}`);
        const data = await res.json();
        if (data.success) {
            document.getElementById('shopBalance').textContent = data.user.coins || 0;
        }
    } catch (e) {
        console.error(e);
    }
}

async function loadShopItems() {
    const container = document.getElementById('shopItems');
    container.innerHTML = '<div class="auth-msg">Загрузка...</div>';
    
    try {
        const res = await fetch('/api/shop/roles');
        const data = await res.json();
        
        if (data.success && data.roles.length > 0) {
            container.innerHTML = data.roles.map(role => `
                <div class="shop-item">
                    <div class="role-icon" style="background: ${role.color}20; color: ${role.color};">
                        ${role.emoji}
                    </div>
                    <div class="role-name" style="color: ${role.color};">${role.name}</div>
                    <div class="role-price">${role.price} монет</div>
                    <button class="buy-btn ${role.owned ? 'owned' : ''}" 
                            onclick="buyRole('${role.id}')" 
                            ${role.owned ? 'disabled' : ''}>
                        ${role.owned ? '✓ Куплено' : 'Купить'}
                    </button>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<div class="auth-msg">Нет доступных ролей</div>';
        }
    } catch (e) {
        console.error(e);
        container.innerHTML = '<div class="auth-msg">Ошибка загрузки</div>';
    }
}

async function buyRole(roleId) {
    try {
        const res = await fetch('/api/shop/buy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ user_id: currentUser.id, role_id: roleId })
        });
        
        const data = await res.json();
        
        if (data.success) {
            showResult(`✅ Роль успешно куплена!`, 'win');
            loadShopItems();
            updateShopBalance();
            loadProfile();
        } else {
            showResult(data.error || 'Ошибка покупки', 'lose');
        }
    } catch (e) {
        console.error(e);
        showResult('Ошибка сервера', 'lose');
    }
}
