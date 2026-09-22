"""
generate_synthetic_logs.py

Скрипт эмулирует выгрузку данных из таблицы detection_logs (PostgreSQL) в CSV.
Реальные данные компании использовать нельзя (конфиденциальность), поэтому
для отчёта/презентации создаётся синтетический набор данных с такой же
структурой и с теми же типами "грязных" записей, что встречались на практике:
пропуски (NaN), дубликаты строк и некорректные bounding box (отрицательные
ширина/высота).

Запуск:
    python scripts/generate_synthetic_logs.py
"""

import numpy as np
import pandas as pd

RANDOM_SEED = 42
N_ROWS = 1500
OUTPUT_PATH = "data/raw/detection_logs_raw.csv"

CAMERAS = [
    (1, "Главный вход"),
    (2, "Парковка A"),
    (3, "Складское помещение"),
    (4, "Запасной выход"),
]

OBJECT_CLASSES = ["person", "vehicle", "unattended_bag"]
# person встречается чаще всего, unattended_bag — редкое событие (дисбаланс классов)
CLASS_WEIGHTS = [0.65, 0.30, 0.05]


def generate_raw_dataframe(n_rows: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    camera_ids = rng.choice([c[0] for c in CAMERAS], size=n_rows)

    # события за последние 7 дней, больше событий в дневное время
    start = pd.Timestamp("2024-06-01")
    day_offsets = rng.integers(0, 7, size=n_rows)
    hour_offsets = rng.integers(0, 24, size=n_rows)
    minute_offsets = rng.integers(0, 60, size=n_rows)
    timestamps = [
        start + pd.Timedelta(days=int(d), hours=int(h), minutes=int(m))
        for d, h, m in zip(day_offsets, hour_offsets, minute_offsets)
    ]

    object_classes = rng.choice(OBJECT_CLASSES, size=n_rows, p=CLASS_WEIGHTS)
    confidence = np.clip(rng.normal(loc=0.82, scale=0.12, size=n_rows), 0.1, 0.99).round(3)

    bbox_x = rng.integers(0, 1800, size=n_rows)
    bbox_y = rng.integers(0, 1000, size=n_rows)
    bbox_width = rng.integers(20, 300, size=n_rows)
    bbox_height = rng.integers(20, 300, size=n_rows)

    df = pd.DataFrame(
        {
            "camera_id": camera_ids,
            "detected_at": timestamps,
            "object_class": object_classes,
            "confidence": confidence,
            "bbox_x": bbox_x,
            "bbox_y": bbox_y,
            "bbox_width": bbox_width,
            "bbox_height": bbox_height,
        }
    )

    # --- намеренно "загрязняем" данные, как это бывает в реальной БД ---

    # 1) пропуски в confidence (~3% строк)
    missing_conf_idx = rng.choice(df.index, size=int(0.03 * n_rows), replace=False)
    df.loc[missing_conf_idx, "confidence"] = np.nan

    # 2) пропуски в object_class (~2% строк)
    missing_class_idx = rng.choice(df.index, size=int(0.02 * n_rows), replace=False)
    df.loc[missing_class_idx, "object_class"] = np.nan

    # 3) дубликаты строк (~2% строк копируем повторно)
    duplicate_rows = df.sample(n=int(0.02 * n_rows), random_state=seed)
    df = pd.concat([df, duplicate_rows], ignore_index=True)

    # 4) некорректные bounding box: отрицательные ширина/высота (~1.5% строк)
    bad_bbox_idx = rng.choice(df.index, size=int(0.015 * len(df)), replace=False)
    df.loc[bad_bbox_idx, "bbox_width"] = -df.loc[bad_bbox_idx, "bbox_width"]

    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    df.insert(0, "log_id", range(1, len(df) + 1))
    return df


if __name__ == "__main__":
    raw_df = generate_raw_dataframe(N_ROWS, RANDOM_SEED)
    raw_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Сгенерировано строк: {len(raw_df)}")
    print(f"Файл сохранён: {OUTPUT_PATH}")
