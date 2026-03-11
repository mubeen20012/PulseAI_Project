import sqlite3
import os

# This makes sure the database file is saved in the same folder as this script
db_path = os.path.join(os.path.dirname(__file__), 'health_tracker.db')

def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Page 1: Users
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      username TEXT UNIQUE NOT NULL, 
                      password TEXT NOT NULL)''')
    
    # Page 2: AI Records
    cursor.execute('''CREATE TABLE IF NOT EXISTS health_records 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      user_id INTEGER, 
                      risk_score REAL, 
                      risk_level TEXT, 
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()
    print(f"✅ Database created at: {db_path}")

if __name__ == "__main__":
    init_db()