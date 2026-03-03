-- Добавление колонок для системы стриков
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS voice_streak INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_voice_date DATE;
