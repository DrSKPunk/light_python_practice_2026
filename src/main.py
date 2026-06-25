import sys
import argparse
import os
from database import DataBase
from scanner import Skaner
from comparer import BackupComparer

def main():
    razbor = argparse.ArgumentParser()
    
    razbor.add_argument("put", help="Путь к папке для индексации")
    razbor.add_argument("--scan", action="store_true", help="Выполнить сканирование папки")
    razbor.add_argument("--ext", nargs="+", help="Фильтр по расширениям (пример: .py .md)")
    razbor.add_argument("--db", default="file_index.db", help="Путь к файлу базы данных (по умолчанию: file_index.db)")
    razbor.add_argument("--hash", action="store_true", help="Вычислить хэши файлов и найти дубликаты")
    razbor.add_argument("--duplicates", action="store_true", help="Показать дубликаты из существующей БД (без сканирования)")
    razbor.add_argument("--compare", help="Сравнить исходную папку с папкой бэкапа (указать путь к бэкапу)")
    razbor.add_argument("--history", action="store_true", help="Показать историю сравнений")
    razbor.add_argument("--show-comparison", type=int, help="Показать детали сравнения по ID")
    
    argumenty = razbor.parse_args()
    
    if not argumenty.duplicates and not argumenty.history and not argumenty.show_comparison:
        if not os.path.exists(argumenty.put):
            print("Ошибка: путь '{}' не существует".format(argumenty.put))
            sys.exit(1)
        
        if not os.path.isdir(argumenty.put) and not argumenty.compare:
            print("Ошибка: '{}' не является папкой".format(argumenty.put))
            sys.exit(1)
    
    print("База данных: {}".format(argumenty.db))
    
    baza = DataBase(argumenty.db)
    baza.Create()
    
    if argumenty.history:
        _pokazat_istoriyu(baza)
        baza.Close()
        return
    
    if argumenty.show_comparison:
        _pokazat_detali_sravneniya(baza, argumenty.show_comparison)
        baza.Close()
        return
    
    if argumenty.compare:
        _sravnit_papki(baza, argumenty.put, argumenty.compare)
        baza.Close()
        return
    
    if argumenty.duplicates:
        skaner = Skaner(baza, argumenty.put)
        skaner.pokazat_duplikaty()
        baza.Close()
        return
    
    if argumenty.scan:
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
        print("Для сравнения папок используйте --compare")
        print("Для просмотра дубликатов используйте --duplicates")
        print("Для просмотра истории используйте --history")
    
    baza.Close()

def _sravnit_papki(baza, source_folder, backup_folder):
    if not os.path.exists(source_folder):
        print(f"Ошибка: исходная папка '{source_folder}' не существует")
        return
    
    if not os.path.isdir(source_folder):
        print(f"Ошибка: '{source_folder}' не является папкой")
        return
    
    if not os.path.exists(backup_folder):
        print(f"Ошибка: папка бэкапа '{backup_folder}' не существует")
        return
    
    if not os.path.isdir(backup_folder):
        print(f"Ошибка: '{backup_folder}' не является папкой")
        return
    
    comparer = BackupComparer(baza)
    comparer.sravnit(source_folder, backup_folder)

def _pokazat_istoriyu(baza):
    history = baza.poluchit_istoriju_sravneniy()
    
    if not history:
        print("\nИстория сравнений пуста")
        return
    
    print("\n" + "="*80)
    print("ИСТОРИЯ СРАВНЕНИЙ")
    print("="*80)
    
    for item in history:
        (id, date, source, backup, missing, modified, extra, same) = item
        print(f"\nID: {id}")
        print(f"  Дата: {date}")
        print(f"  Исходная: {source}")
        print(f"  Бэкап: {backup}")
        print(f"  Одинаковых: {same}")
        print(f"  Отсутствует: {missing}")
        print(f"  Изменено: {modified}")
        print(f"  Лишних: {extra}")
        print(f"  Всего: {same + missing + modified + extra}")
        print(f"  Подробности: --show-comparison {id}")

def _pokazat_detali_sravneniya(baza, comparison_id):
    details = baza.poluchit_detali_sravneniya(comparison_id)
    
    if not details:
        print(f"\nСравнение с ID {comparison_id} не найдено")
        return
    
    print(f"\n=== ДЕТАЛИ СРАВНЕНИЯ (ID: {comparison_id}) ===")
    
    groups = {'missing': [], 'modified': [], 'extra': [], 'same': []}
    for detail in details:
        path, status, source_size, backup_size, source_hash, backup_hash, source_modified, backup_modified = detail
        groups[status].append(detail)
    
    if groups['missing']:
        print(f"\n ОТСУТСТВУЮТ В БЭКАПЕ ({len(groups['missing'])}):")
        for detail in groups['missing'][:20]:
            path = detail[0]
            source_size = detail[2]
            print(f"    - {path} ({source_size} байт)")
        if len(groups['missing']) > 20:
            print(f"    ... и еще {len(groups['missing']) - 20} файлов")
    
    if groups['modified']:
        print(f"\n ИЗМЕНЕНЫ ({len(groups['modified'])}):")
        for detail in groups['modified'][:20]:
            path = detail[0]
            source_size = detail[2]
            backup_size = detail[3]
            print(f"    - {path}")
            print(f"      Размер: {source_size} → {backup_size} байт")
        if len(groups['modified']) > 20:
            print(f"    ... и еще {len(groups['modified']) - 20} файлов")
    
    if groups['extra']:
        print(f"\n ЛИШНИЕ В БЭКАПЕ ({len(groups['extra'])}):")
        for detail in groups['extra'][:20]:
            path = detail[0]
            backup_size = detail[3]
            print(f"    - {path} ({backup_size} байт)")
        if len(groups['extra']) > 20:
            print(f"    ... и еще {len(groups['extra']) - 20} файлов")

if __name__ == "__main__":
    main()