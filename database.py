import sqlite3
from datetime import datetime
import threading

from telegram import User

class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.lock = threading.Lock()
        self.init_db()
    
    def get_connection(self):
        """Creating Connection"""
        conn = sqlite3.connect(self.db_name, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Creating a tables for first opened"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Таблица пользователей - ИСПРАВЛЕНО: добавлена запятая после CHECK
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    balance INTEGER DEFAULT 0 CHECK(balance >= 0),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_banned INTEGER DEFAULT 0
                )
            ''')
            
            # Таблица транзакций
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    game_type TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    transaction_type TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Таблица игровой статистики
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_stats (
                    user_id INTEGER NOT NULL,
                    game_type TEXT NOT NULL,
                    games_played INTEGER DEFAULT 0 CHECK(games_played >= 0),
                    games_won INTEGER DEFAULT 0 CHECK(games_won >= 0),
                    total_bet INTEGER DEFAULT 0 CHECK(total_bet >= 0),
                    total_won INTEGER DEFAULT 0 CHECK(total_won >= 0),
                    PRIMARY KEY (user_id, game_type),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Индексы для оптимизации
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_time ON transactions(timestamp)')
            
            conn.commit()
            conn.close()
    
    def add_user(self, user_id, username, start_balance):
        """Add new member"""
        with self.lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR IGNORE INTO users (user_id, username, balance, created_at, last_active)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, username, start_balance, datetime.now(), datetime.now()))
                
                conn.commit()
                conn.close()
                return True
            except sqlite3.Error as e:
                print(f"Database error in add_user: {e}")
                return False
    
    def is_user_banned(self, user_id):
        """Check on ban"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
        
        # Приводим user_id к строке или числу
        user_id_value = user_id.id if hasattr(user_id, 'id') else user_id
        
        cursor.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id_value,))
        result = cursor.fetchone()
        conn.close()
        
        return result['is_banned'] == 1 if result else False
    
    def get_balance(self, user_id):
        """Get balance member"""
        with self.lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
                result = cursor.fetchone()
                conn.close()
                
                return result['balance'] if result else 0
            except sqlite3.Error as e:
                print(f"Database error in get_balance: {e}")
                return 0
    
    def update_balance(self, user_id, amount):
        """Refresh balance (amount may be positive or negative)
        Return True if success, False if cost enought"""
        with self.lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                # Проверяем текущий баланс
                cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
                result = cursor.fetchone()
                
                if not result:
                    conn.close()
                    return False
                
                current_balance = result['balance']
                new_balance = current_balance + amount
                
                # Проверка на отрицательный баланс
                if new_balance < 0:
                    conn.close()
                    return False
                
                # Защита от переполнения
                if new_balance > 100000000:
                    conn.close()
                    return False
                
                cursor.execute('''
                    UPDATE users 
                    SET balance = ?, last_active = ?
                    WHERE user_id = ?
                ''', (new_balance, datetime.now(), user_id))
                
                conn.commit()
                conn.close()
                return True
            except sqlite3.Error as e:
                print(f"Database error in update_balance: {e}")
                return False
    
    def add_transaction(self, user_id, game_type, amount, transaction_type):
        """Writing transaction"""
        with self.lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO transactions (user_id, game_type, amount, transaction_type, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, game_type, amount, transaction_type, datetime.now()))
                
                conn.commit()
                conn.close()
                return True
            except sqlite3.Error as e:
                print(f"Database error in add_transaction: {e}")
                return False
    
    def update_game_stats(self, user_id, game_type, won, bet_amount, win_amount):
        """Refresh Game Statistic"""
        with self.lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO game_stats (user_id, game_type, games_played, games_won, total_bet, total_won)
                    VALUES (?, ?, 1, ?, ?, ?)
                    ON CONFLICT(user_id, game_type) DO UPDATE SET
                        games_played = games_played + 1,
                        games_won = games_won + ?,
                        total_bet = total_bet + ?,
                        total_won = total_won + ?
                ''', (user_id, game_type, 1 if won else 0, bet_amount, win_amount, 
                      1 if won else 0, bet_amount, win_amount))
                
                conn.commit()
                conn.close()
                return True
            except sqlite3.Error as e:
                print(f"Database error in update_game_stats: {e}")
                return False
    
    def get_user_stats(self, user_id):
        """Get Members Statistic"""
        with self.lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT game_type, games_played, games_won, total_bet, total_won
                    FROM game_stats
                    WHERE user_id = ?
                ''', (user_id,))
                
                stats = cursor.fetchall()
                conn.close()
                
                return [(row['game_type'], row['games_played'], row['games_won'], 
                        row['total_bet'], row['total_won']) for row in stats]
            except sqlite3.Error as e:
                print(f"Database error in get_user_stats: {e}")
                return []
