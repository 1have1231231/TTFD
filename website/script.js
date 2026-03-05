// Global state
let currentUser = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    checkAuth();
});

// Navigation
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const sectionId = item.dataset.section;
            
            // Update active nav
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            // Show section
            document.querySelectorAll('.section').forEach(section => {
                section.classList.remove('active');
            });
            document.getElementById(sectionId).classList.add('active');
            
            // Load section data
            loadSectionData(sectionId);
        });
    });
    
    // Login button
    document.getElementById('loginBtn').addEventListener('click', () => {
        if (currentUser) {
            // Show profile
            document.querySelector('[data-section="profile"]').click();
        } else {
            window.location.href = '/api/auth/discord';
        }
    });
}

// Check authentication
async function checkAuth() {
    try {
        const response = await fetch('/api/me', {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.authenticated) {
                currentUser = data.user;
                updateUIForUser(data.user);
                loadProfile();
            }
        }
    } catch (error) {
        console.error('Auth check error:', error);
    }
}

// Update UI for authenticated user
function updateUIForUser(user) {
    const loginBtn = document.getElementById('loginBtn');
    const userBlock = document.getElementById('userBlock');
    
    const avatar = user.avatar 
        ? `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png`
        : 'https://cdn.discordapp.com/embed/avatars/0.png';
    
    userBlock.innerHTML = `
        <div class="user-info">
            <img src="${avatar}" class="user-avatar" alt="Avatar">
            <div class="user-details">
                <div class="user-name">${user.username}</div>
                <div class="user-coins" id="headerCoins">0 монет</div>
            </div>
        </div>
    `;
}

// Load section data
function loadSectionData(sectionId) {
    switch(sectionId) {
        case 'profile':
            loadProfile();
            break;
        case 'leaderboard':
            loadLeaderboard();
            break;
        case 'roulette':
            loadRoulette();
            break;
        case 'activity':
            loadActivity();
            break;
    }
}

// Load profile
async function loadProfile() {
    if (!currentUser) return;
    
    try {
        const response = await fetch(`/api/user/${currentUser.id}`);
        const data = await response.json();
        
        if (data.success) {
            const user = data.user;
            const avatar = currentUser.avatar 
                ? `https://cdn.discordapp.com/avatars/${currentUser.id}/${currentUser.avatar}.png`
                : 'https://cdn.discordapp.com/embed/avatars/0.png';
            
            // Update profile
            document.getElementById('profileAvatar').src = avatar;
            document.getElementById('profileUsername').textContent = currentUser.username;
            document.getElementById('profileTag').textContent = `${currentUser.username}#${currentUser.discriminator}`;
            
            // Calculate level
            const level = Math.floor(user.xp / 100) + 1;
            const currentLevelXP = user.xp % 100;
            const nextLevelXP = 100;
            const progress = (currentLevelXP / nextLevelXP) * 100;
            
            document.getElementById('profileLevel').textContent = level;
            document.getElementById('currentLevel').textContent = level;
            document.getElementById('currentXP').textContent = currentLevelXP;
            document.getElementById('nextLevelXP').textContent = nextLevelXP;
            document.getElementById('xpBarFill').style.width = `${progress}%`;
            
            // Update stats
            document.getElementById('statCoins').textContent = user.coins || 0;
            document.getElementById('statXP').textContent = user.xp || 0;
            document.getElementById('statLevel').textContent = level;
            document.getElementById('statRank').textContent = user.rank_name || 'F-ранг';
            
            // Update header coins
            const headerCoins = document.getElementById('headerCoins');
            if (headerCoins) {
                headerCoins.textContent = `${user.coins || 0} монет`;
            }
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

// Load leaderboard
async function loadLeaderboard() {
    const container = document.getElementById('topPlayers');
    container.innerHTML = '<div class="loading-spinner"></div>';
    
    try {
        const response = await fetch('/api/top/xp');
        const data = await response.json();
        
        if (data.success && data.players.length > 0) {
            const top3 = data.players.slice(0, 3);
            
            // Reorder: 2nd, 1st, 3rd
            const ordered = top3.length === 3 
                ? [top3[1], top3[0], top3[2]]
                : top3.length === 2
                ? [top3[1], top3[0]]
                : top3;
            
            container.innerHTML = ordered.map((player, idx) => {
                const actualRank = player.rank;
                const isTop1 = actualRank === 1;
                
                return `
                    <div class="player-card ${isTop1 ? 'top-1' : ''}">
                        <div class="player-rank-badge">#${actualRank}</div>
                        <img src="${player.avatar || 'https://cdn.discordapp.com/embed/avatars/0.png'}" 
                             class="player-avatar-large" alt="${player.username}">
                        <div class="player-name">${player.username}</div>
                        <div class="player-level">${player.rank_name}</div>
                        <div class="player-xp">${player.xp.toLocaleString()} XP</div>
                    </div>
                `;
            }).join('');
        } else {
            container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">Нет данных</p>';
        }
    } catch (error) {
        console.error('Error loading leaderboard:', error);
        container.innerHTML = '<p style="text-align: center; color: var(--danger);">Ошибка загрузки</p>';
    }
}

// Load roulette
async function loadRoulette() {
    if (!currentUser) {
        document.getElementById('rouletteAuth').style.display = 'block';
        document.getElementById('rouletteGame').style.display = 'none';
        return;
    }
    
    document.getElementById('rouletteAuth').style.display = 'none';
    document.getElementById('rouletteGame').style.display = 'block';
    
    await updateRouletteBalance();
}

// Update roulette balance
async function updateRouletteBalance() {
    try {
        const response = await fetch(`/api/user/${currentUser.id}`);
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('rouletteBalance').textContent = data.user.coins || 0;
        }
    } catch (error) {
        console.error('Error updating balance:', error);
    }
}

// Place bet
async function placeBet(color) {
    const betAmount = parseInt(document.getElementById('betAmount').value);
    
    if (!betAmount || betAmount < 10) {
        showRouletteResult('Минимальная ставка: 10 монет', 'lose');
        return;
    }
    
    // Disable buttons
    const buttons = document.querySelectorAll('.bet-btn');
    buttons.forEach(btn => btn.disabled = true);
    
    // Animate wheel
    const wheel = document.getElementById('rouletteWheel');
    const numberEl = document.getElementById('rouletteNumber');
    
    wheel.classList.add('spinning');
    numberEl.textContent = '?';
    
    try {
        const response = await fetch('/api/roulette/play', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                user_id: currentUser.id,
                bet: betAmount,
                color: color
            })
        });
        
        const data = await response.json();
        
        setTimeout(() => {
            wheel.classList.remove('spinning');
            
            if (data.success) {
                numberEl.textContent = data.number;
                
                // Change wheel color
                if (data.color === 'green') {
                    wheel.style.background = 'linear-gradient(135deg, #4ADE80, #22C55E)';
                } else if (data.color === 'red') {
                    wheel.style.background = 'linear-gradient(135deg, #EF4444, #DC2626)';
                } else {
                    wheel.style.background = 'linear-gradient(135deg, #2C3E50, #1A252F)';
                }
                
                setTimeout(() => {
                    wheel.style.background = 'linear-gradient(135deg, var(--accent-color), #9D6CFF)';
                }, 2000);
                
                if (data.win) {
                    showRouletteResult(`🎉 Выигрыш! +${data.win_amount} монет`, 'win');
                } else {
                    showRouletteResult(`😢 Проигрыш! -${betAmount} монет`, 'lose');
                }
                
                updateRouletteBalance();
                loadProfile(); // Update profile stats
            } else {
                showRouletteResult(data.error || 'Ошибка', 'lose');
            }
            
            buttons.forEach(btn => btn.disabled = false);
        }, 2000);
        
    } catch (error) {
        console.error('Error placing bet:', error);
        wheel.classList.remove('spinning');
        showRouletteResult('Ошибка сервера', 'lose');
        buttons.forEach(btn => btn.disabled = false);
    }
}

// Show roulette result
function showRouletteResult(message, type) {
    const resultEl = document.getElementById('rouletteResult');
    resultEl.textContent = message;
    resultEl.className = `roulette-result ${type}`;
    
    setTimeout(() => {
        resultEl.textContent = '';
        resultEl.className = 'roulette-result';
    }, 5000);
}

// Load activity
function loadActivity() {
    if (!currentUser) {
        document.getElementById('activityAuth').style.display = 'block';
        document.getElementById('activityList').style.display = 'none';
        return;
    }
    
    document.getElementById('activityAuth').style.display = 'none';
    document.getElementById('activityList').style.display = 'flex';
    
    // Mock activity data
    const activities = [
        { type: 'xp', text: '+50 XP за активность в чате', time: '5 минут назад' },
        { type: 'coins', text: 'Выигрыш в рулетке +200 монет', time: '1 час назад' },
        { type: 'voice', text: 'Присоединился к голосовому каналу', time: '2 часа назад' },
        { type: 'xp', text: '+30 XP за сообщения', time: '3 часа назад' },
    ];
    
    document.getElementById('activityList').innerHTML = activities.map(activity => `
        <div class="activity-item">
            <div class="activity-icon ${activity.type}">
                ${getActivityIcon(activity.type)}
            </div>
            <div class="activity-content">
                <div class="activity-text">${activity.text}</div>
                <div class="activity-time">${activity.time}</div>
            </div>
        </div>
    `).join('');
}

// Get activity icon
function getActivityIcon(type) {
    const icons = {
        xp: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path></svg>',
        coins: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v12M9 9h6"></path></svg>',
        voice: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>'
    };
    return icons[type] || '';
}
