# Исходный код вариативной части

В этой папке находится реализация индивидуальной вариативной части практики по теме **Python: A Simple Web Server**.

## Состав папки

```text
src/
├── README.md
├── main.py
├── server.py
└── public/
    ├── index.html
    ├── about.html
    ├── 404.html
    └── style.css
```

## Запуск

```bash
python src/main.py
```

С указанием порта:

```bash
python src/main.py --host 127.0.0.1 --port 8080
```

## Реализовано

- запуск локального HTTP-сервера;
- маршруты `/` и `/about`;
- отдача статического CSS-файла через `/static/style.css`;
- ответ `404 Not Found` для неизвестных путей;
- ответ `405 Method Not Allowed` для неподдерживаемых методов;
- логирование запросов в консоль.

## Проверка

Локальная проверка была выполнена на порту `8090`.

| Запрос | Результат |
| --- | --- |
| `/` | `200 OK` |
| `/about` | `200 OK` |
| `/static/style.css` | `200 OK` |
| `/missing` | `404 Not Found` |
| `POST /` | `405 Method Not Allowed` |
