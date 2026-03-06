// Wheel of Fortune - множители и их вероятности
const wheelSegments = [
    { multiplier: 0, color: '#DC143C', angle: 0 },      // x0 - Красный
    { multiplier: 1.2, color: '#1E90FF', angle: 30 },   // x1.2 - Синий
    { multiplier: 1.5, color: '#9370DB', angle: 60 },   // x1.5 - Фиолетовый
    { multiplier: 2, color: '#32CD32', angle: 90 },     // x2 - Зелёный
    { multiplier: 0, color: '#DC143C', angle: 120 },    // x0 - Красный
    { multiplier: 3, color: '#FF8C00', angle: 150 },    // x3 - Оранжевый
    { multiplier: 1.2, color: '#1E90FF', angle: 180 },  // x1.2 - Синий
    { multiplier: 5, color: '#FFD700', angle: 210 },    // x5 - Золотой
    { multiplier: 1.5, color: '#9370DB', angle: 240 },  // x1.5 - Фиолетовый
    { multiplier: 2, color: '#32CD32', angle: 270 },    // x2 - Зелёный
    { multiplier: 10, color: '#FF1493', angle: 300 },   // x10 - Розовый
    { multiplier: 1.2, color: '#1E90FF', angle: 330 }   // x1.2 - Синий
];

async function spinWheel() {
    const bet = parseInt(document.getElementById('betAmount').value);
    if (!bet || bet < 10) {
        showResult('Минимальная ставка: 10 монет', 'lose');
        return;
    }
    
    const wheel = document.getElementById('wheel');
    const wheelResult = document.getElementById('wheelResult');
    const resultMultiplier = document.getElementById('resultMultiplier');
    const resultWin = document.getElementById('resultWin');
    const spinBtn = document.getElementById('spinBtn');
    
    spinBtn.disabled = true;
    wheelResult.style.display = 'none';
    
    try {
        const res = await fetch('/api/wheel/spin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ user_id: currentUser.id, bet })
        });
        
        const data = await res.json();
        
        if (data.success) {
            // Находим сектор с выпавшим множителем
            const segment = wheelSegments.find(s => s.multiplier === data.multiplier);
            if (!segment) {
                showResult('Ошибка: неизвестный множитель', 'lose');
                spinBtn.disabled = false;
                return;
            }
            
            // Вычисляем угол для остановки
            const targetAngle = 180 - segment.angle; // Стрелка внизу
            const spins = 5;
            const finalAngle = (360 * spins) + targetAngle + (Math.random() * 20 - 10); // Добавляем случайность
            
            // Вращаем колесо
            wheel.style.transition = 'transform 4s cubic-bezier(0.17, 0.67, 0.12, 0.99)';
            wheel.style.transform = `rotate(${finalAngle}deg)`;
            
            setTimeout(() => {
                // Показываем результат
                resultMultiplier.textContent = `x${data.multiplier}`;
                resultWin.textContent = data.win_amount > 0 ? `+${data.win_amount}` : '0';
                wheelResult.style.display = 'flex';
                
                setTimeout(() => {
                    wheelResult.style.display = 'none';
                }, 3000);
                
                if (data.win_amount > 0) {
                    showResult(`🎉 Выигрыш! x${data.multiplier} = +${data.win_amount} монет`, 'win');
                } else {
                    showResult(`😢 Проигрыш! x${data.multiplier}`, 'lose');
                }
                
                updateRouletteBalance();
                loadProfile();
                spinBtn.disabled = false;
            }, 4000);
        } else {
            showResult(data.error || 'Ошибка', 'lose');
            spinBtn.disabled = false;
        }
    } catch (e) {
        console.error(e);
        showResult('Ошибка сервера', 'lose');
        spinBtn.disabled = false;
    }
}
