// Language translations
const translations = {
    en: {
        'nav.about': 'ABOUT',
        'nav.members': 'MEMBERS',
        'nav.stats': 'STATS',
        'nav.apply': 'APPLY',
        'hero.subtitle': 'DOMINATE. CONTROL. WIN.',
        'hero.join': 'JOIN CLAN',
        'hero.view': 'VIEW MEMBERS',
        'about.title': 'ABOUT CLAN',
        'about.description': 'TTFD is an elite Minecraft clan built on dominance, strategy, and excellence. We are not just players — we are competitors who set the standard.',
        'about.elite.title': 'ELITE',
        'about.elite.desc': 'Only the best join our ranks',
        'about.competitive.title': 'COMPETITIVE',
        'about.competitive.desc': 'Victory is our only option',
        'about.professional.title': 'PROFESSIONAL',
        'about.professional.desc': 'Discipline and skill define us',
        'members.title': 'ROSTER',
        'members.leader': 'LEADER',
        'members.officer': 'OFFICER',
        'members.fighter': 'FIGHTER',
        'members.recruit': 'RECRUIT',
        'members.online': 'ONLINE',
        'members.offline': 'OFFLINE',
        'stats.title': 'STATISTICS',
        'stats.members': 'TOTAL MEMBERS',
        'stats.wins': 'CLAN WINS',
        'stats.kills': 'TOTAL KILLS',
        'stats.online': 'ONLINE NOW',
        'apply.title': 'JOIN TTFD',
        'apply.nickname': 'NICKNAME',
        'apply.age': 'AGE',
        'apply.experience': 'EXPERIENCE',
        'apply.discord': 'DISCORD',
        'apply.why': 'WHY DO YOU WANT TO JOIN TTFD?',
        'apply.submit': 'SUBMIT APPLICATION'
    },
    ru: {
        'nav.about': 'О НАС',
        'nav.members': 'УЧАСТНИКИ',
        'nav.stats': 'СТАТИСТИКА',
        'nav.apply': 'ВСТУПИТЬ',
        'hero.subtitle': 'ДОМИНИРУЙ. КОНТРОЛИРУЙ. ПОБЕЖДАЙ.',
        'hero.join': 'ВСТУПИТЬ В КЛАН',
        'hero.view': 'УЧАСТНИКИ',
        'about.title': 'О КЛАНЕ',
        'about.description': 'TTFD — элитный Minecraft клан, построенный на доминировании, стратегии и превосходстве. Мы не просто игроки — мы конкуренты, которые устанавливают стандарты.',
        'about.elite.title': 'ЭЛИТА',
        'about.elite.desc': 'Только лучшие вступают в наши ряды',
        'about.competitive.title': 'КОНКУРЕНТНЫЕ',
        'about.competitive.desc': 'Победа — наш единственный вариант',
        'about.professional.title': 'ПРОФЕССИОНАЛЫ',
        'about.professional.desc': 'Дисциплина и навыки определяют нас',
        'members.title': 'СОСТАВ',
        'members.leader': 'ЛИДЕР',
        'members.officer': 'ОФИЦЕР',
        'members.fighter': 'БОЕЦ',
        'members.recruit': 'НОВОБРАНЕЦ',
        'members.online': 'В СЕТИ',
        'members.offline': 'НЕ В СЕТИ',
        'stats.title': 'СТАТИСТИКА',
        'stats.members': 'ВСЕГО УЧАСТНИКОВ',
        'stats.wins': 'ПОБЕД КЛАНА',
        'stats.kills': 'ВСЕГО УБИЙСТВ',
        'stats.online': 'СЕЙЧАС В СЕТИ',
        'apply.title': 'ВСТУПИТЬ В TTFD',
        'apply.nickname': 'НИКНЕЙМ',
        'apply.age': 'ВОЗРАСТ',
        'apply.experience': 'ОПЫТ',
        'apply.discord': 'DISCORD',
        'apply.why': 'ПОЧЕМУ ВЫ ХОТИТЕ ВСТУПИТЬ В TTFD?',
        'apply.submit': 'ОТПРАВИТЬ ЗАЯВКУ'
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

// Form submission handler
document.querySelector('.apply-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Get form data
    const formData = new FormData(this);
    const data = Object.fromEntries(formData);
    
    // Here you would typically send data to your backend
    console.log('Application submitted:', data);
    
    // Show success message
    alert('APPLICATION SUBMITTED SUCCESSFULLY!\nWe will review your application and contact you soon.');
    
    // Reset form
    this.reset();
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
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        // Обновляем статистику на странице
        const totalMembersElement = document.querySelector('.stats-grid .stat-card:nth-child(1) .stat-number');
        const onlineNowElement = document.querySelector('.stats-grid .stat-card:nth-child(2) .stat-number');
        
        if (totalMembersElement && data.total_members) {
            totalMembersElement.textContent = data.total_members;
        }
        
        if (onlineNowElement && data.online_members) {
            onlineNowElement.textContent = data.online_members;
        }
        
        console.log('📊 Статистика обновлена:', data);
    } catch (error) {
        console.error('❌ Ошибка загрузки статистики:', error);
    }
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
