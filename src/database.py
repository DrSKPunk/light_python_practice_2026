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
        
        self.kursor.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                folder_path TEXT NOT NULL,
                total_files INTEGER,
                total_size INTEGER
            )
        """)
        
        self.soedinenie.commit()
        print("Таблицы files и scans созданы")
    
    def Close(self):
        if self.soedinenie:
            self.soedinenie.close()
    
    def ochistit_fayly(self):
        self.kursor.execute("DELETE FROM files")
        self.soedinenie.commit()
    
    def dobavit_fayl(self, put, razmer, izmenen, tip_fayla, hesh=None):
        self.kursor.execute("""
            INSERT OR REPLACE INTO files (path, size, modified, file_type, hash)
            VALUES (?, ?, ?, ?, ?)
        """, (put, razmer, izmenen, tip_fayla, hesh))
        self.soedinenie.commit()
        return self.kursor.lastrowid
    
    def sohranit_info_o_skanirovanii(self, put_k_papke, vsego_faylov, obshiy_razmer):
        self.kursor.execute("""
            INSERT INTO scans (folder_path, total_files, total_size)
            VALUES (?, ?, ?)
        """, (put_k_papke, vsego_faylov, obshiy_razmer))
        self.soedinenie.commit()
        return self.kursor.lastrowid