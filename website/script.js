// Navigation
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
            
            // Load leaderboard data if needed
            if (targetId === 'leaderboard') {
                loadLeaderboard();
            }
        });
    });
    
    // Login button
    const loginBtn = document.getElementById('loginBtn');
    loginBtn.addEventListener('click', () => {
        window.location.href = '/api/auth/discord';
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
    const avatar = user.avatar 
        ? `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png`
        : 'https://cdn.discordapp.com/embed/avatars/0.png';
    
    loginBtn.innerHTML = `
        <img src="${avatar}" style="width: 32px; height: 32px; border-radius: 50%; margin-right: 8px;">
        ${user.username}
    `;
    loginBtn.style.display = 'flex';
    loginBtn.style.alignItems = 'center';
    
    loginBtn.onclick = () => {
        if (confirm('Выйти из аккаунта?')) {
            window.location.href = '/api/auth/logout';
        }
    };
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
