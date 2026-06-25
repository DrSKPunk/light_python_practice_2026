import sqlite3
import hashlib

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
            CREATE INDEX IF NOT EXISTS idx_hash ON files(hash)
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
        
        self.kursor.execute("""
            CREATE TABLE IF NOT EXISTS backup_comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comparison_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_folder TEXT NOT NULL,
                backup_folder TEXT NOT NULL,
                total_missing INTEGER DEFAULT 0,
                total_modified INTEGER DEFAULT 0,
                total_extra INTEGER DEFAULT 0,
                total_same INTEGER DEFAULT 0
            )
        """)
        
        self.kursor.execute("""
            CREATE TABLE IF NOT EXISTS comparison_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comparison_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                status TEXT NOT NULL,
                source_size INTEGER,
                backup_size INTEGER,
                source_hash TEXT,
                backup_hash TEXT,
                source_modified TIMESTAMP,
                backup_modified TIMESTAMP,
                FOREIGN KEY (comparison_id) REFERENCES backup_comparisons(id)
            )
        """)
        
        self.soedinenie.commit()
        print("Таблицы созданы/обновлены")
    
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
    
    def poluchit_hash_po_puti(self, put):
        self.kursor.execute("SELECT hash FROM files WHERE path = ?", (put,))
        result = self.kursor.fetchone()
        return result[0] if result else None
    
    def obnovit_hash(self, put, hesh):
        self.kursor.execute("""
            UPDATE files SET hash = ? WHERE path = ?
        """, (hesh, put))
        self.soedinenie.commit()
    
    def nayti_duplikaty(self):
        self.kursor.execute("""
            SELECT hash, GROUP_CONCAT(path, '; '), COUNT(*)
            FROM files
            WHERE hash IS NOT NULL AND hash != ''
            GROUP BY hash
            HAVING COUNT(*) >= 2
            ORDER BY COUNT(*) DESC
        """)
        return self.kursor.fetchall()
    
    def sohranit_rezultat_sravneniya(self, source_folder, backup_folder, rezultaty):
        self.kursor.execute("""
            INSERT INTO backup_comparisons 
            (source_folder, backup_folder, total_missing, total_modified, total_extra, total_same)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            source_folder,
            backup_folder,
            rezultaty['missing_count'],
            rezultaty['modified_count'],
            rezultaty['extra_count'],
            rezultaty['same_count']
        ))
        comparison_id = self.kursor.lastrowid
        
        for item in rezultaty['details']:
            self.kursor.execute("""
                INSERT INTO comparison_details 
                (comparison_id, file_path, status, source_size, backup_size, 
                 source_hash, backup_hash, source_modified, backup_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                comparison_id,
                item['path'],
                item['status'],
                item.get('source_size'),
                item.get('backup_size'),
                item.get('source_hash'),
                item.get('backup_hash'),
                item.get('source_modified'),
                item.get('backup_modified')
            ))
        
        self.soedinenie.commit()
        return comparison_id
    
    def poluchit_istoriju_sravneniy(self, limit=10):
        self.kursor.execute("""
            SELECT id, comparison_date, source_folder, backup_folder, 
                   total_missing, total_modified, total_extra, total_same
            FROM backup_comparisons
            ORDER BY comparison_date DESC
            LIMIT ?
        """, (limit,))
        return self.kursor.fetchall()
    
    def poluchit_detali_sravneniya(self, comparison_id):
        self.kursor.execute("""
            SELECT file_path, status, source_size, backup_size, 
                   source_hash, backup_hash, source_modified, backup_modified
            FROM comparison_details
            WHERE comparison_id = ?
            ORDER BY status, file_path
        """, (comparison_id,))
        return self.kursor.fetchall()