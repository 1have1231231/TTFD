// Navigation
let currentUser = null;

document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');
    
    // Check authentication
    checkAuth();
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            
            // Update active nav link
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // Show target section
            sections.forEach(section => {
                section.classList.remove('active');
                if (section.id === targetId) {
                    section.classList.add('active');
                }
            });
            
            // Load data based on section
            if (targetId === 'leaderboard') {
                loadLeaderboard();
            } else if (targetId === 'cabinet') {
                loadProfile();
            } else if (targetId === 'roulette') {
                loadRoulette();
            }
        });
    });
    
    // Login button
    const loginBtn = document.getElementById('loginBtn');
    loginBtn.addEventListener('click', () => {
        if (currentUser) {
            // Show cabinet
            document.querySelector('a[href="#cabinet"]').click();
        } else {
            window.location.href = '/api/auth/discord';
        }
    });
});

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
            }
        }
    } catch (error) {
        console.error('Auth check error:', error);
    }
}

// Update UI for authenticated user
function updateUIForUser(user) {
    const loginBtn = document.getElementById('loginBtn');
    const cabinetLink = document.getElementById('cabinetLink');
    
    loginBtn.textContent = 'Профиль';
    cabinetLink.style.display = 'block';
}

// Load profile
async function loadProfile() {
    if (!currentUser) {
        document.getElementById('cabinetAuth').style.display = 'block';
        document.getElementById('cabinetContent').style.display = 'none';
        return;
    }
    
    document.getElementById('cabinetAuth').style.display = 'none';
    document.getElementById('cabinetContent').style.display = 'block';
    
    try {
        const response = await fetch(`/api/user/${currentUser.id}`);
        const data = await response.json();
        
        if (data.success) {
            const user = data.user;
            const avatar = currentUser.avatar 
                ? `https://cdn.discordapp.com/avatars/${currentUser.id}/${currentUser.avatar}.png`
                : 'https://cdn.discordapp.com/embed/avatars/0.png';
            
            document.getElementById('profileAvatar').src = avatar;
            document.getElementById('profileUsername').textContent = currentUser.username;
            document.getElementById('profileRank').textContent = user.rank_name || 'F-ранг';
            document.getElementById('profileXP').textContent = user.xp || 0;
            document.getElementById('profileCoins').textContent = user.coins || 0;
            document.getElementById('profileClicks').textContent = user.clicks || 0;
        }
    } catch (error) {
        console.error('Error loading profile:', error);
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
    
    // Load balance
    await updateBalance();
}

// Update balance
async function updateBalance() {
    try {
        const response = await fetch(`/api/user/${currentUser.id}`);
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('balanceAmount').textContent = data.user.coins || 0;
        }
    } catch (error) {
        console.error('Error updating balance:', error);
    }
}

// Place bet
async function placeBet(color) {
    const betAmount = parseInt(document.getElementById('betAmount').value);
    
    if (!betAmount || betAmount < 10) {
        showResult('Минимальная ставка: 10 монет', 'lose');
        return;
    }
    
    // Disable buttons
    const buttons = document.querySelectorAll('.bet-btn');
    buttons.forEach(btn => btn.disabled = true);
    
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
        
        if (data.success) {
            // Animate wheel
            const wheel = document.querySelector('.roulette-wheel');
            const numberEl = document.getElementById('rouletteNumber');
            
            wheel.style.animation = 'none';
            setTimeout(() => {
                wheel.style.animation = 'spin 2s ease-in-out';
            }, 10);
            
            setTimeout(() => {
                numberEl.textContent = data.number;
                
                if (data.win) {
                    showResult(`🎉 Выигрыш! +${data.win_amount} монет`, 'win');
                } else {
                    showResult(`😢 Проигрыш! -${betAmount} монет`, 'lose');
                }
                
                updateBalance();
                buttons.forEach(btn => btn.disabled = false);
            }, 2000);
        } else {
            showResult(data.error || 'Ошибка', 'lose');
            buttons.forEach(btn => btn.disabled = false);
        }
    } catch (error) {
        console.error('Error placing bet:', error);
        showResult('Ошибка сервера', 'lose');
        buttons.forEach(btn => btn.disabled = false);
    }
}

// Show result
function showResult(message, type) {
    const resultEl = document.getElementById('rouletteResult');
    resultEl.textContent = message;
    resultEl.className = `roulette-result ${type}`;
}

// Logout
function logout() {
    window.location.href = '/api/auth/logout';
}

// Load leaderboard
async function loadLeaderboard() {
    const leaderboard = document.querySelector('.leaderboard');
    leaderboard.innerHTML = '<div class="loading">Загрузка...</div>';
    
    try {
        const response = await fetch('/api/top/xp');
        const data = await response.json();
        
        if (data.success && data.players.length > 0) {
            leaderboard.innerHTML = data.players.map(player => `
                <div class="player-card">
                    <div class="player-rank">#${player.rank}</div>
                    <div class="player-avatar" style="background-image: url('${player.avatar || ''}')"></div>
                    <div class="player-info">
                        <div class="player-name">${player.username}</div>
                        <div class="player-xp">${player.xp.toLocaleString()} XP • ${player.rank_name}</div>
                    </div>
                </div>
            `).join('');
        } else {
            leaderboard.innerHTML = '<div class="loading">Нет данных</div>';
        }
    } catch (error) {
        console.error('Error loading leaderboard:', error);
        leaderboard.innerHTML = '<div class="loading">Ошибка загрузки</div>';
    }
}
