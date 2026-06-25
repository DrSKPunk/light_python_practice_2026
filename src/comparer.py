import os
import time
import hashlib

class BackupComparer:
    def __init__(self, baza):
        self.baza = baza
        self.source_files = {}
        self.backup_files = {}
    
    def skanirovat_papku(self, papka):
        files = {}
        if not os.path.exists(papka):
            print(f"Предупреждение: папка '{papka}' не существует")
            return files
        
        for root, dirs, filenames in os.walk(papka):
            for filename in filenames:
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, papka)
                
                try:
                    stat = os.stat(full_path)
                    files[rel_path] = {
                        'size': stat.st_size,
                        'modified': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
                        'hash': self.vychislit_hash(full_path)
                    }
                except (OSError, PermissionError) as e:
                    print(f"  Ошибка чтения {full_path}: {e}")
        
        return files
    
    def vychislit_hash(self, put_k_faylu):
        try:
            hasher = hashlib.md5()
            with open(put_k_faylu, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (OSError, PermissionError):
            return None
    
    def sravnit(self, source_folder, backup_folder):
        print(f"\n=== СРАВНЕНИЕ ПАПОК ===")
        print(f"Исходная папка: {source_folder}")
        print(f"Папка бэкапа: {backup_folder}")
        
        print("\nСканирование исходной папки...")
        self.source_files = self.skanirovat_papku(source_folder)
        print(f"  Найдено файлов: {len(self.source_files)}")
        
        print("Сканирование папки бэкапа...")
        self.backup_files = self.skanirovat_papku(backup_folder)
        print(f"  Найдено файлов: {len(self.backup_files)}")
        
        rezultaty = self._sravnit_fayly()
        
        comparison_id = self.baza.sohranit_rezultat_sravneniya(
            source_folder,
            backup_folder,
            rezultaty
        )
        
        self._vyvesti_otchet(rezultaty, comparison_id)
        
        return comparison_id
    
    def _sravnit_fayly(self):
        missing = []
        modified = []
        extra = []
        same = []
        
        for path, source_info in self.source_files.items():
            if path not in self.backup_files:
                missing.append({
                    'path': path,
                    'status': 'missing',
                    'source_size': source_info['size'],
                    'source_hash': source_info['hash'],
                    'source_modified': source_info['modified']
                })
            else:
                backup_info = self.backup_files[path]
                
                if (source_info['hash'] == backup_info['hash'] and 
                    source_info['size'] == backup_info['size']):
                    same.append({
                        'path': path,
                        'status': 'same',
                        'source_size': source_info['size'],
                        'backup_size': backup_info['size'],
                        'source_hash': source_info['hash'],
                        'backup_hash': backup_info['hash']
                    })
                else:
                    modified.append({
                        'path': path,
                        'status': 'modified',
                        'source_size': source_info['size'],
                        'backup_size': backup_info['size'],
                        'source_hash': source_info['hash'],
                        'backup_hash': backup_info['hash'],
                        'source_modified': source_info['modified'],
                        'backup_modified': backup_info.get('modified', '')
                    })
        
        for path in self.backup_files:
            if path not in self.source_files:
                backup_info = self.backup_files[path]
                extra.append({
                    'path': path,
                    'status': 'extra',
                    'backup_size': backup_info['size'],
                    'backup_hash': backup_info['hash'],
                    'backup_modified': backup_info['modified']
                })
        
        return {
            'missing': missing,
            'modified': modified,
            'extra': extra,
            'same': same,
            'missing_count': len(missing),
            'modified_count': len(modified),
            'extra_count': len(extra),
            'same_count': len(same),
            'details': missing + modified + extra + same
        }
    
    def _vyvesti_otchet(self, rezultaty, comparison_id):
        print("\n" + "="*60)
        print("ОТЧЕТ О СРАВНЕНИИ")
        print("="*60)
        
        total = (rezultaty['missing_count'] + rezultaty['modified_count'] + 
                 rezultaty['extra_count'] + rezultaty['same_count'])
        
        print(f"\nОБЩАЯ СТАТИСТИКА:")
        print(f"  Всего файлов: {total}")
        print(f"  Одинаковые: {rezultaty['same_count']}")
        print(f"  Отсутствуют в бэкапе: {rezultaty['missing_count']}")
        print(f"  Изменены: {rezultaty['modified_count']}")
        print(f"  Лишние в бэкапе: {rezultaty['extra_count']}")
        
        if rezultaty['missing']:
            print(f"\nОТСУТСТВУЮТ В БЭКАПЕ ({rezultaty['missing_count']}):")
            for item in rezultaty['missing'][:10]:
                print(f"    - {item['path']} ({item['source_size']} байт)")
            if len(rezultaty['missing']) > 10:
                print(f"    ... и еще {len(rezultaty['missing']) - 10} файлов")
        
        if rezultaty['modified']:
            print(f"\nИЗМЕНЕНЫ ({rezultaty['modified_count']}):")
            for item in rezultaty['modified'][:10]:
                print(f"    - {item['path']}")
                print(f"      Исходник: {item['source_size']} байт -> Бэкап: {item['backup_size']} байт")
            if len(rezultaty['modified']) > 10:
                print(f"    ... и еще {len(rezultaty['modified']) - 10} файлов")
        
        if rezultaty['extra']:
            print(f"\nЛИШНИЕ В БЭКАПЕ ({rezultaty['extra_count']}):")
            for item in rezultaty['extra'][:10]:
                print(f"    - {item['path']} ({item['backup_size']} байт)")
            if len(rezultaty['extra']) > 10:
                print(f"    ... и еще {len(rezultaty['extra']) - 10} файлов")
        
        print(f"\n{'='*60}")
        print(f"Результаты сохранены в БД (ID сравнения: {comparison_id})")
        print(f"Для просмотра истории используйте: --history")
        print("="*60)