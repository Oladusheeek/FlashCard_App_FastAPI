from database import engine
from sqlalchemy import text

def run_migration():
    print("🚑 Начинаем лечение базы данных...")
    
    with engine.connect() as conn:
        conn = conn.execution_options(isolation_level="AUTOCOMMIT")
        
        # Список команд для добавления колонок
        commands = [
            "ALTER TABLE cards ADD COLUMN IF NOT EXISTS next_review_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();",
            "ALTER TABLE cards ADD COLUMN IF NOT EXISTS interval FLOAT DEFAULT 0.0;",
            "ALTER TABLE cards ADD COLUMN IF NOT EXISTS easiness_factor FLOAT DEFAULT 2.5;",
            "ALTER TABLE cards ADD COLUMN IF NOT EXISTS repetitions INTEGER DEFAULT 0;"
        ]

        for command in commands:
            try:
                conn.execute(text(command))
                print(f"✅ Успех: {command[:50]}...")
            except Exception as e:
                # Если ошибка 'already exists', это нормально, значит колонка уже есть
                print(f"⚠️  Инфо: {e}")

    print("🎉 Лечение завершено! Теперь база данных здорова.")

if __name__ == "__main__":
    run_migration()