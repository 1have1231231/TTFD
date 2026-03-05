// Navigation
document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');
    
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
        alert('Discord OAuth будет добавлен позже');
    });
});

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
