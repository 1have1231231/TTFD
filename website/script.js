// Language translations
const translations = {
    en: {
        'nav.members': 'MEMBERS',
        'nav.stats': 'STATS',
        'nav.discord': 'DISCORD',
        'hero.subtitle': 'DOMINATE. CONTROL. WIN.',
        'hero.join': 'JOIN CLAN',
        'hero.view': 'VIEW MEMBERS',
        'members.title': 'ROSTER',
        'members.leader': 'LEADER',
        'members.officer': 'OFFICER',
        'members.fighter': 'FIGHTER',
        'members.recruit': 'RECRUIT',
        'members.online': 'ONLINE',
        'members.offline': 'OFFLINE',
        'stats.title': 'STATISTICS',
        'stats.members': 'TOTAL MEMBERS',
        'stats.online': 'ONLINE NOW'
    },
    ru: {
        'nav.members': 'УЧАСТНИКИ',
        'nav.stats': 'СТАТИСТИКА',
        'nav.discord': 'DISCORD',
        'hero.subtitle': 'ДОМИНИРУЙ. КОНТРОЛИРУЙ. ПОБЕЖДАЙ.',
        'hero.join': 'ВСТУПИТЬ В КЛАН',
        'hero.view': 'УЧАСТНИКИ',
        'members.title': 'СОСТАВ',
        'members.leader': 'ЛИДЕР',
        'members.officer': 'ОФИЦЕР',
        'members.fighter': 'БОЕЦ',
        'members.recruit': 'НОВОБРАНЕЦ',
        'members.online': 'В СЕТИ',
        'members.offline': 'НЕ В СЕТИ',
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
    
    // Update all elements with data-i18n
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });
    
    // Update placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        if (translations[lang][key]) {
            element.placeholder = translations[lang][key];
        }
    });
    
    // Update active button
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-lang') === lang) {
            btn.classList.add('active');
        }
    });
}

// Initialize language on page load
document.addEventListener('DOMContentLoaded', () => {
    setLanguage(currentLang);
    
    // Add click handlers to language buttons
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const lang = btn.getAttribute('data-lang');
            setLanguage(lang);
        });
    });
});

// Smooth scroll with offset for fixed nav
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const offset = 80;
            const targetPosition = target.offsetTop - offset;
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Fade-in animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Apply fade-in to sections
document.querySelectorAll('.section').forEach(section => {
    section.style.opacity = '0';
    section.style.transform = 'translateY(30px)';
    section.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
    observer.observe(section);
});

// Nav background on scroll
let lastScroll = 0;
window.addEventListener('scroll', () => {
    const nav = document.querySelector('.nav');
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 100) {
        nav.style.background = 'rgba(10, 10, 10, 0.98)';
    } else {
        nav.style.background = 'rgba(10, 10, 10, 0.95)';
    }
    
    lastScroll = currentScroll;
});

// Dynamic stats counter animation
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);
    
    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            element.textContent = target.toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(start).toLocaleString();
        }
    }, 16);
}

// Fetch Discord stats from API
async function updateDiscordStats() {
    console.log('🔄 Загрузка статистики...');
    try {
        const response = await fetch('/api/stats');
        console.log('📡 Ответ получен:', response.status);
        
        const data = await response.json();
        console.log('📊 Данные:', data);
        
        // Обновляем статистику на странице
        const totalMembersElement = document.querySelector('.stats-grid .stat-card:nth-child(1) .stat-number');
        const onlineNowElement = document.querySelector('.stats-grid .stat-card:nth-child(2) .stat-number');
        
        if (totalMembersElement && data.total_members !== undefined) {
            totalMembersElement.textContent = data.total_members;
            console.log('✅ Обновлено total_members:', data.total_members);
        }
        
        if (onlineNowElement && data.online_members !== undefined) {
            onlineNowElement.textContent = data.online_members;
            console.log('✅ Обновлено online_members:', data.online_members);
        }
        
        // Обновляем карточки игроков
        console.log('👥 Игроков в данных:', data.top_players ? data.top_players.length : 0);
        if (data.top_players) {
            updateMembersGrid(data.top_players);
        } else {
            console.warn('⚠️ Нет данных top_players');
            updateMembersGrid([]);
        }
        
        console.log('✅ Статистика обновлена успешно');
    } catch (error) {
        console.error('❌ Ошибка загрузки статистики:', error);
        // Показываем сообщение об ошибке
        const grid = document.getElementById('members-grid');
        if (grid) {
            grid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: #ff4444;">
                    <h3>ERROR LOADING DATA</h3>
                    <p style="color: #666; margin-top: 1rem;">${error.message}</p>
                    <p style="color: #666; margin-top: 0.5rem;">Check console for details</p>
                </div>
            `;
        }
    }
}

// Обновление карточек игроков
function updateMembersGrid(players) {
    console.log('🎮 updateMembersGrid вызвана с', players.length, 'игроками');
    
    const grid = document.getElementById('members-grid');
    if (!grid) {
        console.error('❌ Элемент members-grid не найден!');
        return;
    }
    
    console.log('✅ Элемент members-grid найден');
    
    // Очищаем сетку
    grid.innerHTML = '';
    console.log('🗑️ Сетка очищена');
    
    // Если нет игроков, показываем сообщение
    if (!players || players.length === 0) {
        console.warn('⚠️ Нет игроков для отображения');
        const message = document.createElement('div');
        message.style.gridColumn = '1 / -1';
        message.style.textAlign = 'center';
        message.style.padding = '3rem';
        message.style.color = '#666';
        message.textContent = 'NO PLAYERS DATA AVAILABLE';
        grid.appendChild(message);
        return;
    }
    
    console.log('👥 Создаём карточки для', players.length, 'игроков');
    
    // Создаём карточки для каждого игрока
    players.forEach((player, index) => {
        console.log(`📝 Создаём карточку ${index + 1}:`, player.name);
        
        const card = document.createElement('div');
        card.className = 'member-card';
        card.style.animation = `fadeInUp 0.6s ease ${index * 0.1}s both`;
        
        // Аватарка
        const avatar = document.createElement('div');
        avatar.className = 'member-avatar';
        if (player.avatar_url) {
            const img = document.createElement('img');
            img.src = player.avatar_url;
            img.alt = player.name;
            img.onerror = function() {
                console.warn('⚠️ Не удалось загрузить аватар для', player.name);
                this.style.display = 'none';
            };
            avatar.appendChild(img);
        }
        
        // Имя
        const name = document.createElement('h3');
        name.className = 'member-name';
        name.textContent = player.display_name || player.name;
        
        // Ранг
        const role = document.createElement('p');
        role.className = 'member-role';
        role.textContent = player.rank || 'F';
        
        // Статус
        const status = document.createElement('span');
        status.className = `member-status ${player.online ? 'online' : 'offline'}`;
        
        // Переводим статус
        const currentLang = localStorage.getItem('language') || 'en';
        const statusText = player.online ? 
            (currentLang === 'ru' ? 'В СЕТИ' : 'ONLINE') : 
            (currentLang === 'ru' ? 'НЕ В СЕТИ' : 'OFFLINE');
        status.textContent = statusText;
        
        // XP
        const xpInfo = document.createElement('p');
        xpInfo.className = 'member-xp';
        xpInfo.style.color = '#666';
        xpInfo.style.fontSize = '0.85rem';
        xpInfo.style.marginTop = '0.5rem';
        xpInfo.textContent = `${(player.xp || 0).toLocaleString()} XP`;
        
        // Собираем карточку
        card.appendChild(avatar);
        card.appendChild(name);
        card.appendChild(role);
        card.appendChild(xpInfo);
        card.appendChild(status);
        
        grid.appendChild(card);
    });
    
    console.log('✅ Все карточки созданы и добавлены');
}

// Обновляем статистику при загрузке и каждые 30 секунд
document.addEventListener('DOMContentLoaded', () => {
    updateDiscordStats();
    setInterval(updateDiscordStats, 30000); // Обновление каждые 30 секунд
});

// Trigger counter animation when stats section is visible
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const statNumbers = entry.target.querySelectorAll('.stat-number');
            statNumbers.forEach(stat => {
                const target = parseInt(stat.textContent.replace(/,/g, ''));
                animateCounter(stat, target);
            });
            statsObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

const statsSection = document.querySelector('.stats');
if (statsSection) {
    statsObserver.observe(statsSection);
}
