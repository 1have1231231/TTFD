// Language translations
const translations = {
    en: {
        'members.title': 'ROSTER',
        'stats.title': 'STATISTICS',
        'stats.members': 'TOTAL MEMBERS',
        'stats.online': 'ONLINE NOW'
    },
    ru: {
        'members.title': 'СОСТАВ',
        'stats.title': 'СТАТИСТИКА',
        'stats.members': 'ВСЕГО УЧАСТНИКОВ',
        'stats.online': 'СЕЙЧАС В СЕТИ'
    }
};

// Language switcher
let currentLang = localStorage.getItem('language') || 'en';

function setLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('language', lang);
    
    document.getElementById('currentLang').textContent = lang.toUpperCase();
    
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });
    
    document.getElementById('langDropdown').classList.remove('active');
    document.getElementById('langToggle').classList.remove('active');
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setLanguage(currentLang);
    
    // Language toggle
    const langToggle = document.getElementById('langToggle');
    const langDropdown = document.getElementById('langDropdown');
    
    langToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        langDropdown.classList.toggle('active');
        langToggle.classList.toggle('active');
    });
    
    document.addEventListener('click', () => {
        langDropdown.classList.remove('active');
        langToggle.classList.remove('active');
    });
    
    // Update stats
    updateDiscordStats();
    setInterval(updateDiscordStats, 180000);
});

// Fetch Discord stats
async function updateDiscordStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        const totalMembersElement = document.querySelector('.stats-grid .stat-card:nth-child(1) .stat-number');
        const onlineNowElement = document.querySelector('.stats-grid .stat-card:nth-child(2) .stat-number');
        
        if (totalMembersElement && data.total_members !== undefined) {
            totalMembersElement.textContent = data.total_members;
        }
        
        if (onlineNowElement && data.online_members !== undefined) {
            onlineNowElement.textContent = data.online_members;
        }
        
        if (data.top_players) {
            updateMembersGrid(data.top_players);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Update members grid
function updateMembersGrid(players) {
    const grid = document.getElementById('members-grid');
    if (!grid) return;
    
    grid.innerHTML = '';
    
    if (!players || players.length === 0) {
        const message = document.createElement('div');
        message.style.gridColumn = '1 / -1';
        message.style.textAlign = 'center';
        message.style.padding = '3rem';
        message.style.color = '#666';
        message.textContent = 'NO PLAYERS DATA AVAILABLE';
        grid.appendChild(message);
        return;
    }
    
    players.forEach((player, index) => {
        const card = document.createElement('div');
        card.className = 'member-card';
        card.style.animation = `fadeInUp 0.6s ease ${index * 0.1}s both`;
        
        const avatar = document.createElement('div');
        avatar.className = 'member-avatar';
        if (player.avatar_url) {
            const img = document.createElement('img');
            img.src = player.avatar_url;
            img.alt = player.name;
            img.onerror = function() {
                this.style.display = 'none';
            };
            avatar.appendChild(img);
        }
        
        const name = document.createElement('h3');
        name.className = 'member-name';
        name.textContent = player.display_name || player.name;
        
        const role = document.createElement('p');
        role.className = 'member-role';
        role.textContent = player.rank || 'F';
        
        const status = document.createElement('span');
        status.className = `member-status ${player.online ? 'online' : 'offline'}`;
        const statusText = player.online ? 
            (currentLang === 'ru' ? 'В СЕТИ' : 'ONLINE') : 
            (currentLang === 'ru' ? 'НЕ В СЕТИ' : 'OFFLINE');
        status.textContent = statusText;
        
        const xpInfo = document.createElement('p');
        xpInfo.className = 'member-xp';
        xpInfo.style.color = '#666';
        xpInfo.style.fontSize = '0.85rem';
        xpInfo.style.marginTop = '0.5rem';
        xpInfo.textContent = `${(player.xp || 0).toLocaleString()} XP`;
        
        card.appendChild(avatar);
        card.appendChild(name);
        card.appendChild(role);
        card.appendChild(xpInfo);
        card.appendChild(status);
        
        grid.appendChild(card);
    });
}
