import os
import time
import hashlib

class Skaner:
    def __init__(self, baza, put_k_papke):
        self.baza = baza
        self.put_k_papke = os.path.abspath(put_k_papke)
        self.kolichestvo_faylov = 0
        self.obshiy_razmer = 0
        self.filtr_rasshireniy = None
        self.spisok_faylov = []
        self.vychislyat_heshi = False
    
    def ustanovit_filtr(self, rasshireniya):
        if rasshireniya:
            self.filtr_rasshireniy = [r.lower() for r in rasshireniya]
    
    def vklyuchit_heshi(self):
        self.vychislyat_heshi = True
    
    def nuzhno_vklyuchat(self, put_k_faylu):
        if not os.path.isfile(put_k_faylu):
            return False
        
        if self.filtr_rasshireniy:
            rasshirenie = os.path.splitext(put_k_faylu)[1].lower()
            return rasshirenie in self.filtr_rasshireniy
        
        return True
    
    def vychislit_hash(self, put_k_faylu):
        try:
            hasher = hashlib.md5()
            with open(put_k_faylu, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (OSError, PermissionError):
            return None
    
    def skanirovat(self):
        print("\nСканирование папки: {}".format(self.put_k_papke))
        
        self.baza.ochistit_fayly()
        self.spisok_faylov = []
        
        for koren, papki, fayly in os.walk(self.put_k_papke):
            for fayl in fayly:
                polniy_put = os.path.join(koren, fayl)
                self._obrabotat_fayl(polniy_put)
        
        print("\n=== СПИСОК ФАЙЛОВ ===")
        for put in self.spisok_faylov:
            print("  {}".format(put))
        
        id_skanirovaniya = self.baza.sohranit_info_o_skanirovanii(
            self.put_k_papke,
            self.kolichestvo_faylov,
            self.obshiy_razmer
        )
        
        print("\nСканирование завершено:")
        print("  Найдено файлов: {}".format(self.kolichestvo_faylov))
        print("  Общий размер: {} байт".format(self.obshiy_razmer))
        print("  ID сканирования: {}".format(id_skanirovaniya))
        
        if self.vychislyat_heshi:
            self.pokazat_duplikaty()
        
        return id_skanirovaniya
    
    def _obrabotat_fayl(self, polniy_put):
        if not self.nuzhno_vklyuchat(polniy_put):
            return
        
        try:
            stat = os.stat(polniy_put)
            otnositelniy_put = os.path.relpath(polniy_put, self.put_k_papke)
            razmer = stat.st_size
            izmenen = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
            tip_fayla = os.path.splitext(polniy_put)[1].lower()
            
            hesh = None
            if self.vychislyat_heshi:
                hesh = self.baza.poluchit_hash_po_puti(otnositelniy_put)
                if hesh is None:
                    hesh = self.vychislit_hash(polniy_put)
            
            self.baza.dobavit_fayl(otnositelniy_put, razmer, izmenen, tip_fayla, hesh)
            
            self.spisok_faylov.append(otnositelniy_put)
            self.kolichestvo_faylov += 1
            self.obshiy_razmer += razmer
            
        except (OSError, PermissionError) as e:
            print("  Ошибка обработки файла {}: {}".format(polniy_put, str(e)))
    
    def pokazat_duplikaty(self):
        duplikaty = self.baza.nayti_duplikaty()
        
        print("\n=== ДУБЛИКАТЫ ФАЙЛОВ ===")
        if not duplikaty:
            print("  Дубликатов не найдено")
            return
        
        print(f"  Найдено групп дубликатов: {len(duplikaty)}")
        print()
        
        for i, (hesh, puti, kolichestvo) in enumerate(duplikaty, 1):
            print(f"Группа {i}: {kolichestvo} файлов с хэшем {hesh[:16]}...")
            for put in puti.split('; '):
                print(f"    - {put}")
            
            self.baza.kursor.execute(
                "SELECT size FROM files WHERE path = ?", 
                (puti.split('; ')[0],)
            )
            razmer = self.baza.kursor.fetchone()
            if razmer:
                print(f"    Размер: {razmer[0]} байт")
            print()