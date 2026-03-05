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
    
    // Mock data for now
    const mockPlayers = [
        { rank: 1, name: 'Player One', xp: 15000, avatar: '' },
        { rank: 2, name: 'Player Two', xp: 12500, avatar: '' },
        { rank: 3, name: 'Player Three', xp: 10000, avatar: '' }
    ];
    
    leaderboard.innerHTML = mockPlayers.map(player => `
        <div class="player-card">
            <div class="player-rank">#${player.rank}</div>
            <div class="player-avatar"></div>
            <div class="player-info">
                <div class="player-name">${player.name}</div>
                <div class="player-xp">${player.xp.toLocaleString()} XP</div>
            </div>
        </div>
    `).join('');
}
