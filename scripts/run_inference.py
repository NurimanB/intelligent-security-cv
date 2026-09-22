"""
run_inference.py

Задача стажёра: запустить готовую (предобученную) модель YOLOv8 на тестовых
изображениях и сохранить результаты детекции в CSV. Обучение модели здесь
не выполняется — используется веса `yolov8n.pt`, предоставленные командой.

Запуск:
    python scripts/run_inference.py
"""

from pathlib import Path

import pandas as pd
from ultralytics import YOLO

MODEL_WEIGHTS = "yolov8n.pt"
IMAGES_DIR = "data/samples"
OUTPUT_CSV = "data/processed/inference_results.csv"


def run_inference(model_path: str, images_dir: str) -> pd.DataFrame:
    model = YOLO(model_path)
    image_paths = sorted(Path(images_dir).glob("*.jpg"))

    rows = []
    for image_path in image_paths:
        results = model.predict(source=str(image_path), verbose=False)

        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                confidence = float(box.conf[0])

                rows.append(
                    {
                        "image_name": image_path.name,
                        "class_name": class_name,
                        "confidence": round(confidence, 3),
                        "x1": round(x1, 1),
                        "y1": round(y1, 1),
                        "x2": round(x2, 1),
                        "y2": round(y2, 1),
                    }
                )

    return pd.DataFrame(rows)


if __name__ == "__main__":
    detections_df = run_inference(MODEL_WEIGHTS, IMAGES_DIR)
    detections_df.to_csv(OUTPUT_CSV, index=False)

    print(f"Всего найдено объектов: {len(detections_df)}")
    print(detections_df.head(15))
    print(f"\nРезультаты сохранены в: {OUTPUT_CSV}")
