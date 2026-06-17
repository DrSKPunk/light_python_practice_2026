import sys
import argparse
import os
from database import DataBase

def main():
    razbor = argparse.ArgumentParser(description="Индексатор папок")
    razbor.add_argument("put", help="Путь к папке для индексации")
    razbor.add_argument("--db", default="file_index.db", help="Путь к файлу базы данных")
    
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
    baza.Close()

if __name__ == "__main__":
    main()