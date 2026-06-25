import sys
import argparse
import os
from database import DataBase
from scanner import Skaner

def main():
    razbor = argparse.ArgumentParser()
    
    razbor.add_argument("put", help="Путь к папке для индексации")
    razbor.add_argument("--scan", action="store_true", help="Выполнить сканирование папки")
    razbor.add_argument("--ext", nargs="+", help="Фильтр по расширениям (пример: .py .md)")
    razbor.add_argument("--db", default="file_index.db", help="Путь к файлу базы данных (по умолчанию: file_index.db)")
    razbor.add_argument("--hash", action="store_true", help="Вычислить хэши файлов и найти дубликаты")
    razbor.add_argument("--duplicates", action="store_true", help="Показать дубликаты из существующей БД (без сканирования)")
    
    argumenty = razbor.parse_args()
    
    if not os.path.exists(argumenty.put):
        print("Ошибка: путь '{}' не существует".format(argumenty.put))
        sys.exit(1)
    
    if not os.path.isdir(argumenty.put):
        print("Ошибка: '{}' не является папкой".format(argumenty.put))
        sys.exit(1)
    
    print("Индексация папки: {}".format(argumenty.put))
    print("База данных: {}".format(argumenty.db))
    
    baza = DataBase(argumenty.db)
    baza.Create()
    
    if argumenty.duplicates:
        # Только показать дубликаты из существующей БД
        skaner = Skaner(baza, argumenty.put)
        skaner.pokazat_duplikaty()
    elif argumenty.scan:
        skaner = Skaner(baza, argumenty.put)
        if argumenty.ext:
            skaner.ustanovit_filtr(argumenty.ext)
            print("Фильтр расширений: {}".format(argumenty.ext))
        if argumenty.hash:
            skaner.vklyuchit_heshi()
            print("Вычисление хэшей включено")
        skaner.skanirovat()
    else:
        print("Для сканирования используйте --scan")
        print("Для просмотра дубликатов используйте --duplicates")
    
    baza.Close()

if __name__ == "__main__":
    main()