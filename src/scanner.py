import os
import time

class Skaner:
    def __init__(self, baza, put_k_papke):
        self.baza = baza
        self.put_k_papke = os.path.abspath(put_k_papke)
        self.kolichestvo_faylov = 0
        self.obshiy_razmer = 0
        self.filtr_rasshireniy = None
        self.spisok_faylov = []
    
    def ustanovit_filtr(self, rasshireniya):
        if rasshireniya:
            self.filtr_rasshireniy = [r.lower() for r in rasshireniya]
    
    def nuzhno_vklyuchat(self, put_k_faylu):
        if not os.path.isfile(put_k_faylu):
            return False
        
        if self.filtr_rasshireniy:
            rasshirenie = os.path.splitext(put_k_faylu)[1].lower()
            return rasshirenie in self.filtr_rasshireniy
        
        return True
    
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
            
            self.baza.dobavit_fayl(otnositelniy_put, razmer, izmenen, tip_fayla)
            
            self.spisok_faylov.append(otnositelniy_put)
            self.kolichestvo_faylov += 1
            self.obshiy_razmer += razmer
            
        except (OSError, PermissionError) as e:
            print("  Ошибка обработки файла {}: {}".format(polniy_put, str(e)))