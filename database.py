import sqlite3
from contextlib import contextmanager

# Настройка подключения к БД
DATABASE_PATH = 'edgram.db'

@contextmanager
def db_connection():
    """Контекстный менеджер для безопасного подключения к БД"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Для доступа к полям по имени
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Инициализация базы данных (вызывается один раз при первом запуске)"""
    with db_connection() as conn:
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            class TEXT,
            school TEXT,
            subject TEXT,
            balance INTEGER DEFAULT 0,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP
        )
        """)
        
        # Таблица задач
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            class TEXT NOT NULL,
            description TEXT NOT NULL,
            answer TEXT NOT NULL,
            reward INTEGER DEFAULT 10,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users (user_id)
        )
        """)
        
        # Таблица транзакций
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            type TEXT NOT NULL,  # 'task', 'purchase', 'reward'
            item_id INTEGER,      # ID задачи/товара
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        """)
        
        conn.commit()
    print("✅ База данных инициализирована")

# Основные функции работы с пользователями
def register_user(user_data: dict):
    """Регистрация нового пользователя"""
    with db_connection() as conn:
        cursor = conn.cursor()
        if user_data['role'] == 'student':
            cursor.execute("""
                INSERT INTO users (user_id, username, full_name, role, class)
                VALUES (?, ?, ?, ?, ?)
                """, (
                user_data['user_id'],
                user_data.get('username'),
                user_data['full_name'],
                user_data['role'],
                user_data['class_or_school']
            ))
        else:
            cursor.execute("""
                INSERT INTO users (user_id, username, full_name, role, school, subject)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                user_data['user_id'],
                user_data.get('username'),
                user_data['full_name'],
                user_data['role'],
                user_data['class_or_school'],
                user_data['subject']
            ))
        conn.commit()

def get_user(user_id: int) -> dict:
    """Получение данных пользователя"""
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return dict(cursor.fetchone() or {})

# Функции для работы с балансом
def update_balance(user_id: int, amount: int, transaction_type: str, item_id: int = None):
    """Обновление баланса с записью транзакции"""
    with db_connection() as conn:
        cursor = conn.cursor()
        
        # Обновляем баланс пользователя
        cursor.execute("""
            UPDATE users 
            SET balance = balance + ? 
            WHERE user_id = ?
            """, (amount, user_id))
        
        # Записываем транзакцию
        cursor.execute("""
            INSERT INTO transactions (user_id, amount, type, item_id)
            VALUES (?, ?, ?, ?)
            """, (user_id, amount, transaction_type, item_id))
        
        conn.commit()

# Функции для работы с задачами
def add_task(task_data: dict):
    """Добавление новой задачи"""
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (author_id, subject, class, description, answer, reward)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
            task_data['author_id'],
            task_data['subject'],
            task_data['class'],
            task_data['description'],
            task_data['answer'],
            task_data.get('reward', 10)
        ))
        conn.commit()
        return cursor.lastrowid
