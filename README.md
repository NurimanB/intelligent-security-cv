# intelligent-security-cv
End-to-end machine learning pipeline for real-time object detection and metadata aggregation, built with PyTorch, YOLOv8, OpenCV, and PostgreSQL.

## О проекте

Проект в системе видеоаналитики: извлечение данных из БД, очистка,
разведочный анализ (EDA) и запуск инференса готовой модели YOLOv8.


## Структура

```
sql/                     DDL-схема и примеры запросов (JOIN, GROUP BY, поиск NULL, треки)
scripts/clean_data.py                очистка данных (Pandas)
scripts/eda.py                       разведочный анализ + графики
scripts/run_inference.py             инференс YOLOv8n на тестовых изображениях
scripts/train.py                     дообучение YOLOv8 + метрики (mAP@0.5, Precision, Recall)
scripts/track_video.py               трекинг объектов на видео (ByteTrack) -> CSV / PostgreSQL
notebooks/train_yolov8_colab.ipynb   полный прогон в Google Colab (GPU)
data/raw/                            сырые данные
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

Пример реального вывода этих запросов — `sql/query_results_example.txt`.

## Дообучение и трекинг

Откройте `notebooks/train_yolov8_colab.ipynb` в Google Colab
(File → Open notebook → GitHub → `NurimanB/intelligent-security-cv`), выберите
GPU T4 и выполните ячейки по порядку. Или локально:

```bash
python scripts/train.py --device 0       # YOLOv8n на 5 классах VOC: person, car, bus, motorbike, bicycle
python scripts/track_video.py --source path/to/video.mp4
psql -U postgres -d security_demo -f sql/03_tracks.sql   # таблица треков + аналитика
```

`train.py` сохраняет метрики в `reports/metrics.json` и графики обучения в
`reports/figures/`.

## Результаты

YOLOv8n, дообученная на 5 классах Pascal VOC (person, car, bus, motorbike, bicycle):
30 эпох, 50% обучающей выборки, Google Colab (GPU T4). Метрики посчитаны на
валидационной выборке VOC (`reports/metrics.json`).

| Модель | Данные | mAP@0.5 | mAP@0.5:0.95 | Precision | Recall |
|---|---|---|---|---|---|
| YOLOv8n, fine-tuned | VOC, 5 классов | **0.889** | 0.674 | 0.869 | 0.804 |

| Класс | AP@0.5 |
|---|---|
| car | 0.920 |
| person | 0.897 |
| motorbike | 0.885 |
| bicycle | 0.882 |
| bus | 0.859 |

Кривые обучения: mAP ещё растёт к 30-й эпохе, так что более долгое обучение,
скорее всего, даст прирост.

![Кривые обучения](reports/figures/train_results.png)

![Матрица ошибок](reports/figures/train_confusion_matrix.png)
