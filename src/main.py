import sys
import argparse
import os
from database import DataBase
from scanner import Skaner

def main():
    razbor = argparse.ArgumentParser(description="Indeksator papok")
    razbor.add_argument("put", help="Путь к папке для индексации")
    razbor.add_argument("--db", default="file_index.db", help="Путь к файлу базы данных")
    razbor.add_argument("--scan", action="store_true", help="Выполнить сканированние папки")
    razbor.add_argument("--ext", nargs="+", help="Фильтр по расширениям")
    
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
    
    if argumenty.scan:
        skaner = Skaner(baza, argumenty.put)
        if argumenty.ext:
            skaner.ustanovit_filtr(argumenty.ext)
            print("Фильтр расширений: {}".format(argumenty.ext))
        skaner.skanirovat()
    
    baza.Close()

if __name__ == "__main__":
    main()