# intelligent-security-cv
End-to-end machine learning pipeline for real-time object detection and metadata aggregation, built with PyTorch, YOLOv8, OpenCV, and PostgreSQL.

## О проекте

Демо-проект, иллюстрирующий типичные задачи стажёра (junior data science
assistant) в системе видеоаналитики: извлечение данных из БД, очистка,
разведочный анализ (EDA) и запуск инференса готовой модели YOLOv8.

Модель не обучается с нуля — используются предобученные веса `yolov8n.pt`.
Реальные данные компании конфиденциальны, поэтому здесь используется
**синтетический** набор данных той же структуры (с намеренно "грязными"
записями — пропусками, дубликатами, некорректными bounding box), чтобы
воспроизводимо продемонстрировать процесс очистки и анализа.

## Структура

```
sql/                     DDL-схема и примеры запросов (JOIN, GROUP BY, поиск NULL)
scripts/generate_synthetic_logs.py   генерация синтетических "сырых" данных
scripts/clean_data.py                очистка данных (Pandas)
scripts/eda.py                       разведочный анализ + графики
scripts/run_inference.py             инференс YOLOv8n на тестовых изображениях
data/raw/                            сырые (синтетические) данные
data/processed/                      очищенные данные и результаты инференса
reports/figures/                     сохранённые графики EDA
```

## Как воспроизвести

```bash
pip install -r requirements.txt

python scripts/generate_synthetic_logs.py   # data/raw/detection_logs_raw.csv
python scripts/clean_data.py                # data/processed/detection_logs_clean.csv
python scripts/eda.py                       # reports/figures/*.png
python scripts/run_inference.py             # data/processed/inference_results.csv
```

Веса `yolov8n.pt` скачиваются автоматически библиотекой `ultralytics` при
первом запуске.

Для SQL-запросов (`sql/01_schema.sql`, `sql/02_queries.sql`) нужен локальный
PostgreSQL:

```bash
psql -U postgres -d security_demo -f sql/01_schema.sql
psql -U postgres -d security_demo -f sql/02_queries.sql
```
