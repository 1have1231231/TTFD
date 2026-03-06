let currentUser = null;

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadLeaderboard();
    checkAdminAccess();
});

function showSection(id) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    event.target.classList.add('active');
    
    if (id === 'leaderboard') loadLeaderboard();
    if (id === 'roulette') loadRoulette();
    if (id === 'shop') loadShop();
    if (id === 'admin') loadAdmin();
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
        loadGradientColors();
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
    
    if (!currentUser) {
        container.innerHTML = '<div class="auth-msg">Войдите для просмотра магазина</div>';
        return;
    }
    
    try {
        const res = await fetch(`/api/shop/roles?user_id=${currentUser.id}`);
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
        console.error('Shop error:', e);
        container.innerHTML = '<div class="auth-msg">Ошибка загрузки. Попробуйте позже.</div>';
    }
}

async function loadGradientColors() {
    const container = document.getElementById('gradientColors');
    if (!container) return; // Если элемент не найден, пропускаем
    
    container.innerHTML = '<div class="auth-msg">Загрузка градиентных цветов...</div>';
    
    if (!currentUser) {
        container.innerHTML = '<div class="auth-msg">Войдите для просмотра цветов</div>';
        return;
    }
    
    try {
        const res = await fetch(`/api/shop/colors?user_id=${currentUser.id}`);
        const data = await res.json();
        
        if (data.success && data.colors.length > 0) {
            container.innerHTML = `
                <h3 style="color: #58a6ff; margin-bottom: 20px;">🌈 Градиентные цвета</h3>
                <div class="colors-grid">
                    ${data.colors.map(color => `
                        <div class="color-item">
                            <div class="color-preview" style="background: ${color.gradient};">
                                <span class="color-emoji">${color.emoji}</span>
                            </div>
                            <div class="color-name">${color.name}</div>
                            <div class="color-price">${color.price} монет</div>
                            <button class="buy-btn ${color.owned ? (color.active ? 'active' : 'owned') : ''}" 
                                    onclick="${color.owned ? `activateColor('${color.id}')` : `buyColor('${color.id}')`}" 
                                    ${color.active ? 'disabled' : ''}>
                                ${color.active ? '✨ Активен' : color.owned ? '🎨 Активировать' : 'Купить'}
                            </button>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            container.innerHTML = '<div class="auth-msg">Нет доступных градиентных цветов</div>';
        }
    } catch (e) {
        console.error('Gradient colors error:', e);
        container.innerHTML = '<div class="auth-msg">Ошибка загрузки цветов. Попробуйте позже.</div>';
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

async function buyColor(colorId) {
    try {
        const res = await fetch('/api/shop/buy-color', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ user_id: currentUser.id, color_id: colorId })
        });
        
        const data = await res.json();
        
        if (data.success) {
            if (data.was_purchased) {
                showResult(`🌈 Градиентный цвет "${data.color_name}" куплен и активирован!`, 'win');
            } else {
                showResult(`✨ Градиентный цвет "${data.color_name}" активирован!`, 'win');
            }
            loadGradientColors();
            updateShopBalance();
            loadProfile();
        } else {
            showResult(data.error || 'Ошибка покупки цвета', 'lose');
        }
    } catch (e) {
        console.error(e);
        showResult('Ошибка сервера', 'lose');
    }
}

async function activateColor(colorId) {
    // Активация уже купленного цвета
    await buyColor(colorId);
}

function loadAdmin() {
    // Admin panel is always loaded, just clear any previous results
    document.getElementById('userSearchResults').innerHTML = '';
    document.getElementById('adminResult').style.display = 'none';
    
    // Clear form fields
    document.getElementById('userSearch').value = '';
    document.getElementById('xpUserId').value = '';
    document.getElementById('xpAmount').value = '';
    document.getElementById('coinsUserId').value = '';
    document.getElementById('coinsAmount').value = '';
}

// ==================== ADMIN FUNCTIONS ====================

async function checkAdminAccess() {
    if (!currentUser) return;
    
    try {
        const res = await fetch('/api/admin/check', { credentials: 'include' });
        const data = await res.json();
        
        if (data.is_admin) {
            document.getElementById('adminLink').style.display = 'block';
            console.log('✅ Admin access granted');
        }
    } catch (e) {
        console.error('Admin check error:', e);
    }
}

async function searchUser() {
    const query = document.getElementById('userSearch').value.trim();
    const resultsContainer = document.getElementById('userSearchResults');
    
    if (!query) {
        showAdminResult('Введите Discord ID или имя пользователя', 'error');
        return;
    }
    
    resultsContainer.innerHTML = '<div style="color: #8b949e;">Поиск...</div>';
    
    try {
        const res = await fetch(`/api/admin/get-user?query=${encodeURIComponent(query)}`, {
            credentials: 'include'
        });
        const data = await res.json();
        
        if (data.success) {
            if (data.user) {
                // Single user result
                displayUserResult([data.user], resultsContainer);
            } else if (data.users) {
                // Multiple users result
                displayUserResult(data.users, resultsContainer);
            }
        } else {
            resultsContainer.innerHTML = `<div style="color: #da3633;">${data.error}</div>`;
        }
    } catch (e) {
        console.error('Search error:', e);
        resultsContainer.innerHTML = '<div style="color: #da3633;">Ошибка поиска</div>';
    }
}

function displayUserResult(users, container) {
    container.innerHTML = users.map(user => `
        <div class="user-result">
            <div class="user-info-admin">
                <div class="user-name-admin">${user.username}</div>
                <div class="user-stats-admin">
                    ID: ${user.id} | XP: ${user.xp} | Монеты: ${user.coins} | Ранг: ${user.rank_id} | Игр: ${user.games_played}/${user.games_won}
                </div>
            </div>
            <div class="user-actions">
                <button class="copy-btn" onclick="copyToXP('${user.id}')">→ XP</button>
                <button class="copy-btn" onclick="copyToCoins('${user.id}')">→ Монеты</button>
                <button class="copy-btn" onclick="copyUserId('${user.id}')">Копировать ID</button>
            </div>
        </div>
    `).join('');
}

function copyToXP(userId) {
    document.getElementById('xpUserId').value = userId;
    document.getElementById('xpAmount').focus();
}

function copyToCoins(userId) {
    document.getElementById('coinsUserId').value = userId;
    document.getElementById('coinsAmount').focus();
}

function copyUserId(userId) {
    navigator.clipboard.writeText(userId).then(() => {
        showAdminResult('ID скопирован в буфер обмена', 'success');
    }).catch(() => {
        showAdminResult('Не удалось скопировать ID', 'error');
    });
}

async function giveXP() {
    const userId = document.getElementById('xpUserId').value.trim();
    const xpAmount = parseInt(document.getElementById('xpAmount').value);
    
    if (!userId || !xpAmount || xpAmount <= 0) {
        showAdminResult('Введите корректный Discord ID и количество XP', 'error');
        return;
    }
    
    try {
        const res = await fetch('/api/admin/give-xp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ user_id: userId, xp_amount: xpAmount })
        });
        
        const data = await res.json();
        
        if (data.success) {
            let message = `✅ Выдано ${data.xp_added} XP пользователю ${userId}\n`;
            message += `XP: ${data.old_xp} → ${data.new_xp}`;
            
            if (data.rank_up) {
                message += `\n🎉 Повышение ранга: ${data.old_rank_id} → ${data.new_rank_id}`;
            }
            
            showAdminResult(message, 'success');
            
            // Clear form
            document.getElementById('xpUserId').value = '';
            document.getElementById('xpAmount').value = '';
        } else {
            showAdminResult(`❌ Ошибка: ${data.error}`, 'error');
        }
    } catch (e) {
        console.error('Give XP error:', e);
        showAdminResult('❌ Ошибка сервера', 'error');
    }
}

async function giveCoins() {
    const userId = document.getElementById('coinsUserId').value.trim();
    const coinsAmount = parseInt(document.getElementById('coinsAmount').value);
    
    if (!userId || isNaN(coinsAmount) || coinsAmount === 0) {
        showAdminResult('Введите корректный Discord ID и количество монет', 'error');
        return;
    }
    
    try {
        const res = await fetch('/api/admin/give-coins', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ user_id: userId, coins_amount: coinsAmount })
        });
        
        const data = await res.json();
        
        if (data.success) {
            const action = coinsAmount > 0 ? 'Выдано' : 'Списано';
            let message = `✅ ${action} ${Math.abs(data.coins_added)} монет пользователю ${userId}\n`;
            message += `Монеты: ${data.old_coins} → ${data.new_coins}`;
            
            showAdminResult(message, 'success');
            
            // Clear form
            document.getElementById('coinsUserId').value = '';
            document.getElementById('coinsAmount').value = '';
        } else {
            showAdminResult(`❌ Ошибка: ${data.error}`, 'error');
        }
    } catch (e) {
        console.error('Give coins error:', e);
        showAdminResult('❌ Ошибка сервера', 'error');
    }
}

function showAdminResult(message, type) {
    const result = document.getElementById('adminResult');
    result.innerHTML = message.replace(/\n/g, '<br>');
    result.className = `admin-result ${type}`;
    result.style.display = 'block';
    
    // Auto hide after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            result.style.display = 'none';
        }, 5000);
    }
}

// Add Enter key support for admin forms
document.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const target = e.target;
        
        if (target.id === 'userSearch') {
            searchUser();
        } else if (target.id === 'xpUserId' || target.id === 'xpAmount') {
            giveXP();
        } else if (target.id === 'coinsUserId' || target.id === 'coinsAmount') {
            giveCoins();
        }
    }
});