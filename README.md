# Banking Transactions Analytics

Приложение для анализа банковских транзакций из Excel-файла.

Проект реализует:
- генерацию JSON-ответов для веб-страниц
- аналитические отчёты
- сервисы для поиска и обработки транзакций
- CLI-запуск
- 100% покрытие тестами

---

## 📁 Структура проекта

src/
│
├── banking_transactions_analytics/
│   ├── main.py        # Точка входа (CLI)
│   ├── views.py       # Логика веб-страниц
│   ├── services.py    # Сервисы
│   ├── reports.py     # Отчёты
│   └── utils.py       # Вспомогательные функции
│
tests/                 # Тесты
data/                  # Excel-файл с транзакциями

---

## Установка

```bash
poetry install
```

## Запуск приложения

```bash
poetry run python src/banking_transactions_analytics/main.py
```

## Пример вызова main_page

```python
from banking_transactions_analytics.views import main_page
import pandas as pd

df = pd.read_excel("data/operations.xlsx")

result = main_page("2023-05-20 12:00:00", df)
print(result)
```

## Запуск тестов

```bash
poetry run pytest --cov=src
```
### Покрытие: 100%

### Используемые технологии
	•	Python 3.14
	•	pandas
	•	pytest
	•	mypy
	•	flake8
	•	black
	•	isort
	•	poetry

## Особенности проекта
	•	Разделение бизнес-логики и получения данных
	•	Использование type hints
	•	100% test coverage
	•	Чистая история коммитов
	•	Конфигурация линтеров по требованиям ТЗ

---
