"""
clean_data.py

Простой скрипт очистки данных на Pandas — типичная задача для стажёра
после выгрузки данных из БД.

Что делаем:
    1. Загружаем "сырые" данные (как будто это результат SQL-запроса).
    2. Убираем дубликаты строк.
    3. Обрабатываем пропуски (NaN) в confidence и object_class.
    4. Фильтруем некорректные bounding box (отрицательная ширина/высота).
    5. Сохраняем очищенный датасет и выводим df.info() / df.describe().

Запуск:
    python scripts/clean_data.py
"""

import pandas as pd

INPUT_PATH = "data/raw/detection_logs_raw.csv"
OUTPUT_PATH = "data/processed/detection_logs_clean.csv"


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["detected_at"])
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    print(f"Исходное количество строк: {len(df)}")

    # 1. Удаляем дубликаты строк (log_id не учитываем, т.к. он всегда уникален
    #    и не позволит найти повторяющиеся по смыслу записи)
    subset_cols = [c for c in df.columns if c != "log_id"]
    df = df.drop_duplicates(subset=subset_cols)
    print(f"После удаления дубликатов: {len(df)}")

    # 2. object_class — критичное поле, без него запись бесполезна -> удаляем строку
    df = df.dropna(subset=["object_class"])

    # 3. confidence — пропуски заполняем медианой по столбцу
    #    (медиана устойчивее к выбросам, чем среднее)
    median_confidence = df["confidence"].median()
    df["confidence"] = df["confidence"].fillna(median_confidence)

    # 4. camera_id — без привязки к камере запись не несёт ценности -> удаляем
    df = df.dropna(subset=["camera_id"])
    df["camera_id"] = df["camera_id"].astype(int)

    # 5. Отбрасываем записи с некорректными (отрицательными) bounding box
    valid_bbox = (df["bbox_width"] > 0) & (df["bbox_height"] > 0)
    df = df[valid_bbox]
    print(f"После фильтрации некорректных bbox: {len(df)}")

    df = df.reset_index(drop=True)
    return df


if __name__ == "__main__":
    raw_df = load_data(INPUT_PATH)

    print("\n=== df.info() до очистки ===")
    raw_df.info()

    clean_df = clean_data(raw_df)

    print("\n=== df.info() после очистки ===")
    clean_df.info()

    print("\n=== df.describe() после очистки ===")
    print(clean_df.describe())

    clean_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nОчищенный датасет сохранён: {OUTPUT_PATH}")
