### brixo_parser
___
### Проект написан с использованием Scrapy и предназначен для сбора данных с сайта https://brixogroup.com/. Данные сохраняются в формате PDF (1 товар - 1 PDF файл).
### Запуск парсера происходит через brix.py
___
### brixo_parser/brix_parser/spiders/brix.py - файл, который делает http запросы и парсит результат и отправляет его в pipeline
### brixo_parser/brix_parser/pipelines.py - принимает данные и формирует PDF файл
___
### Пример PDF файла:
![pdf](https://i.ibb.co/ZLtyWnL/pdf.png)

