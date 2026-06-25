# Запуск в командной строке

python src/main.py C:\\Users\\anime\\OneDrive\\Рабочий стол\\light\_python\_practice\_2026



## Индексатор папок



Сканирование папки

python src/main.py . --scan



Сканирование с фильтром по расширениям

python src/main.py . --scan --ext .py .md .txt



Указать путь к базе данных

python src/main.py . --db my\_database.db --scan



Сканирование с фильтром и своей базой

python src/main.py . --scan --ext .py --db my\_database.db



Сканирование дубликатов

python src/main.py . --scan --hash



Показать дубликаты из базы данных

python src/main.py . --duplicates



Сравнение с бэкапом

\--compare "Путь к бэкапу" (сравнение)

\--history (история сравнений)

\--show-comparison "id сравнения" (результаты сравнения по id)



Помощь

python src/main.py -h

