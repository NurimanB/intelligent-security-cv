# intelligent-security-cv
End-to-end machine learning pipeline for real-time object detection and metadata aggregation, built with PyTorch, YOLOv8, OpenCV, and PostgreSQL.

## О проекте

Проект в системе видеоаналитики: извлечение данных из БД, очистка,
разведочный анализ (EDA) и запуск инференса готовой модели YOLOv8.


## Структура

```
sql/                     DDL-схема и примеры запросов (JOIN, GROUP BY, поиск NULL)
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

python scripts/clean_data.py                # data/processed/detection_logs_clean.csv
python scripts/eda.py                       # reports/figures/*.png
python scripts/run_inference.py             # data/processed/inference_results.csv
```

`data/raw/detection_logs_raw.csv` уже входит в репозиторий, поэтому
генерировать его заново не требуется.

Веса `yolov8n.pt` скачиваются автоматически библиотекой `ultralytics` при
первом запуске.

Для SQL-запросов (`sql/01_schema.sql`, `sql/02_queries.sql`) нужен локальный
PostgreSQL:

```bash
psql -U postgres -d security_demo -f sql/01_schema.sql
psql -U postgres -d security_demo -f sql/02_queries.sql
```
