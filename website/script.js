// ===== TRANSLATIONS =====
const translations = {
    en: {
        'topxp.title': 'TOP XP',
        'topxp.subtitle': 'TOP 3 PLAYERS BY EXPERIENCE',
        'stats.title': 'STATISTICS',
        'stats.total': 'TOTAL MEMBERS',
        'stats.online': 'ONLINE NOW'
    },
    ru: {
        'topxp.title': 'ТОП XP',
        'topxp.subtitle': 'ТОП 3 ИГРОКА ПО ОПЫТУ',
        'stats.title': 'СТАТИСТИКА',
        'stats.total': 'ВСЕГО УЧАСТНИКОВ',
        'stats.online': 'СЕЙЧАС В СЕТИ'
    }
};

let currentLang = localStorage.getItem('language') || 'en';

// ===== LANGUAGE SWITCHER =====
function setLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('language', lang);
    
    const currentLangElement = document.getElementById('currentLang');
    if (currentLangElement) {
        currentLangElement.textContent = lang.toUpperCase();
    }
    
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });
    
    const langDropdown = document.getElementById('langDropdown');
    const langToggle = document.getElementById('langToggle');
    
    if (langDropdown) langDropdown.classList.remove('active');
    if (langToggle) langToggle.classList.remove('active');
    
    // Update active state on lang options
    document.querySelectorAll('.lang-option').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-lang') === lang);
    });
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 TTFD Elite Site Initialized');
    
    setLanguage(currentLang);
    
    // Language toggle
    const langToggle = document.getElementById('langToggle');
    const langDropdown = document.getElementById('langDropdown');
    
    if (langToggle && langDropdown) {
        langToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            langDropdown.classList.toggle('active');
            langToggle.classList.toggle('active');
        });
        
        document.addEventListener('click', () => {
            langDropdown.classList.remove('active');
            langToggle.classList.remove('active');
        });
        
        langDropdown.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }
    
    // Language options
    document.querySelectorAll('.lang-option').forEach(btn => {
        btn.addEventListener('click', () => {
            const lang = btn.getAttribute('data-lang');
            setLanguage(lang);
        });
    });
    
    // Load data
    loadTopXP();
    loadStats();
    
    // Refresh every 3 minutes
    setInterval(() => {
        loadTopXP();
        loadStats();
    }, 180000);
});

// ===== LOAD TOP XP =====
async function loadTopXP() {
    console.log('📊 Loading TOP XP...');
    
    const grid = document.getElementById('topXpGrid');
    if (!grid) return;
    
    try {
        const response = await fetch('/api/stats');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Data received:', data);
        
        // Get top 3 players sorted by XP
        let topPlayers = [];
        if (data.top_players && Array.isArray(data.top_players)) {
            topPlayers = data.top_players
                .sort((a, b) => (b.xp || 0) - (a.xp || 0))
                .slice(0, 3);
        }
        
        if (topPlayers.length === 0) {
            renderEmptyState(grid);
            return;
        }
        
        renderTopXP(grid, topPlayers);
        
    } catch (error) {
        console.error('❌ Error loading TOP XP:', error);
        renderErrorState(grid, error.message);
    }
}

// ===== RENDER TOP XP =====
function renderTopXP(grid, players) {
    grid.innerHTML = '';
    
    players.forEach((player, index) => {
        const rank = index + 1;
        const card = document.createElement('div');
        card.className = `top-card rank-${rank}`;
        
        // Field mapping for compatibility
        const avatarUrl = player.avatar_url || player.avatarUrl || player.avatar || null;
        const displayName = player.display_name || player.displayName || player.name || player.username || 'Unknown';
        const userRank = player.rank || player.role || null;
        const xpValue = player.xp || player.experience || 0;
        const isOnline = player.online || player.isOnline || false;
        
        // Rank badge
        const rankBadge = document.createElement('div');
        rankBadge.className = 'rank-badge';
        rankBadge.textContent = `#${rank}`;
        
        // Avatar
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        if (avatarUrl) {
            const img = document.createElement('img');
            img.src = avatarUrl;
            img.alt = displayName;
            img.onerror = () => {
                img.style.display = 'none';
            };
            avatar.appendChild(img);
        }
        
        // Username
        const username = document.createElement('div');
        username.className = 'username';
        username.textContent = displayName;
        
        // Role (if exists)
        let roleElement = null;
        if (userRank) {
            roleElement = document.createElement('div');
            roleElement.className = 'user-role';
            roleElement.textContent = userRank;
        }
        
        // XP
        const xpValueEl = document.createElement('div');
        xpValueEl.className = 'xp-value';
        xpValueEl.textContent = xpValue.toLocaleString();
        
        const xpLabel = document.createElement('div');
        xpLabel.className = 'xp-label';
        xpLabel.textContent = 'XP';
        
        // Status pill
        const statusPill = document.createElement('div');
        statusPill.className = `status-pill ${isOnline ? 'online' : 'offline'}`;
        statusPill.textContent = isOnline ? 
            (currentLang === 'ru' ? 'В СЕТИ' : 'ONLINE') : 
            (currentLang === 'ru' ? 'НЕ В СЕТИ' : 'OFFLINE');
        
        // View profile button
        const viewBtn = document.createElement('a');
        viewBtn.href = player.profileUrl || player.profile_url || `/cabinet.html`;
        viewBtn.className = 'btn btn-secondary view-profile-btn';
        viewBtn.textContent = currentLang === 'ru' ? 'ПРОФИЛЬ' : 'VIEW PROFILE';
        
        // Assemble card
        card.appendChild(rankBadge);
        card.appendChild(avatar);
        card.appendChild(username);
        if (roleElement) card.appendChild(roleElement);
        card.appendChild(xpValueEl);
        card.appendChild(xpLabel);
        card.appendChild(statusPill);
        card.appendChild(viewBtn);
        
        grid.appendChild(card);
    });
    
    console.log(`✅ Rendered ${players.length} TOP XP cards`);
}

// ===== EMPTY STATE =====
function renderEmptyState(grid) {
    grid.innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">📊</div>
            <div class="empty-state-title">NO DATA YET</div>
            <div class="empty-state-text">Leaderboard will appear once players earn XP</div>
        </div>
    `;
}

// ===== ERROR STATE =====
function renderErrorState(grid, errorMsg) {
    grid.innerHTML = `
        <div class="error-state">
            <div class="error-state-icon">⚠️</div>
            <div class="error-state-title">FAILED TO LOAD LEADERBOARD</div>
            <div class="error-state-text">${errorMsg || 'Please try again later'}</div>
            <button class="btn btn-secondary" onclick="loadTopXP()">RETRY</button>
        </div>
    `;
}

// ===== LOAD STATS =====
async function loadStats() {
    console.log('📈 Loading stats...');
    
    try {
        const response = await fetch('/api/stats');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        const totalMembersEl = document.getElementById('totalMembers');
        const onlineMembersEl = document.getElementById('onlineMembers');
        
        if (totalMembersEl && data.total_members !== undefined) {
            animateCounter(totalMembersEl, data.total_members);
        }
        
        if (onlineMembersEl && data.online_members !== undefined) {
            animateCounter(onlineMembersEl, data.online_members);
        }
        
        console.log('✅ Stats updated');
        
    } catch (error) {
        console.error('❌ Error loading stats:', error);
    }
}

// ===== COUNTER ANIMATION =====
function animateCounter(element, target) {
    const current = parseInt(element.textContent) || 0;
    if (current === target) return;
    
    const duration = 1000;
    const steps = 30;
    const increment = (target - current) / steps;
    let step = 0;
    
    const timer = setInterval(() => {
        step++;
        const value = Math.round(current + (increment * step));
        element.textContent = value;
        
        if (step >= steps) {
            element.textContent = target;
            clearInterval(timer);
        }
    }, duration / steps);
}
