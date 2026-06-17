import sqlite3

class DataBase:
    def __init__(self, put_k_baze):
        self.put_k_baze = put_k_baze
        self.soedinenie = None
        self.kursor = None
    
    def Create(self):
        self.soedinenie = sqlite3.connect(self.put_k_baze)
        self.kursor = self.soedinenie.cursor()
        
        self.kursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL,
                size INTEGER,
                modified TIMESTAMP,
                file_type TEXT,
                hash TEXT,
                scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(path)
            )
        """)
        
        self.soedinenie.commit()
        print("Таблица files создана")
    
    def Close(self):
        if self.soedinenie:
            self.soedinenie.close()