"""
eda.py

Разведочный анализ данных (EDA) на очищенном датасете detection_logs.
Строим два графика:
    1. Столбчатая диаграмма — частота классов объектов.
    2. Линейный график — количество детекций по дням недели.

Запуск:
    python scripts/eda.py
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

INPUT_PATH = "data/processed/detection_logs_clean.csv"
FIG_DIR = "reports/figures"

sns.set_theme(style="whitegrid")


def plot_class_distribution(df: pd.DataFrame, save_path: str) -> None:
    plt.figure(figsize=(7, 5))
    order = df["object_class"].value_counts().index
    sns.countplot(data=df, x="object_class", order=order, hue="object_class",
                   palette="viridis", legend=False)
    plt.title("Частота обнаруженных классов объектов")
    plt.xlabel("Класс объекта")
    plt.ylabel("Количество детекций")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Сохранён график: {save_path}")


def plot_detections_over_time(df: pd.DataFrame, save_path: str) -> None:
    daily_counts = (
        df.assign(day=df["detected_at"].dt.date)
        .groupby("day")
        .size()
        .reset_index(name="event_count")
    )

    plt.figure(figsize=(8, 5))
    sns.lineplot(data=daily_counts, x="day", y="event_count", marker="o")
    plt.title("Количество детекций по дням")
    plt.xlabel("Дата")
    plt.ylabel("Количество событий")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Сохранён график: {save_path}")


if __name__ == "__main__":
    df = pd.read_csv(INPUT_PATH, parse_dates=["detected_at"])

    print("Распределение по классам:")
    print(df["object_class"].value_counts())

    plot_class_distribution(df, f"{FIG_DIR}/class_distribution.png")
    plot_detections_over_time(df, f"{FIG_DIR}/detections_over_time.png")
