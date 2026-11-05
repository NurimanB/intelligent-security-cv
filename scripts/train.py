"""
train.py

Дообучение (fine-tuning) YOLOv8 на классах, важных для видеонаблюдения,
и расчёт метрик качества (Precision, Recall, mAP@0.5, mAP@0.5:0.95).

По умолчанию: Pascal VOC (скачивается автоматически), только 5 классов —
person, car, bus, motorbike, bicycle. Рассчитано на Google Colab (GPU T4).

Запуск:
    python scripts/train.py                      # полный прогон (~1 час на T4)
    python scripts/train.py --data coco8.yaml --epochs 1 --classes   # быстрая проверка
"""

import argparse
import json
import shutil
from pathlib import Path

from ultralytics import YOLO

# индексы классов в VOC.yaml: 1 bicycle, 5 bus, 6 car, 13 motorbike, 14 person
SECURITY_CLASSES = [1, 5, 6, 13, 14]
REPORTS_DIR = Path("reports")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="VOC.yaml")
    parser.add_argument("--model", default="yolov8n.pt")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--fraction", type=float, default=0.5,
                        help="доля обучающей выборки (ускоряет обучение)")
    parser.add_argument("--classes", type=int, nargs="*", default=SECURITY_CLASSES,
                        help="ID классов для обучения; пустой список = все классы")
    parser.add_argument("--device", default=None, help="0 для GPU, cpu для CPU")
    parser.add_argument("--name", default="voc_security")
    return parser.parse_args()


def main():
    args = parse_args()
    classes = args.classes or None

    model = YOLO(args.model)
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        fraction=args.fraction,
        classes=classes,
        device=args.device,
        name=args.name,
        exist_ok=True,
        patience=10,
    )

    train_dir = Path(model.trainer.save_dir)
    best_weights = Path(model.trainer.best)

    # итоговая оценка лучших весов на валидационной выборке
    best = YOLO(best_weights)
    metrics = best.val(data=args.data, imgsz=args.imgsz, batch=args.batch,
                       classes=classes, device=args.device,
                       name=f"{args.name}_val", exist_ok=True)
    val_dir = Path(metrics.save_dir)

    per_class = {
        best.names[int(c)]: round(float(ap50), 4)
        for c, ap50 in zip(metrics.box.ap_class_index, metrics.box.ap50)
    }
    summary = {
        "data": args.data,
        "model": args.model,
        "epochs": args.epochs,
        "train_fraction": args.fraction,
        "weights": str(best_weights),
        "precision": round(float(metrics.box.mp), 4),
        "recall": round(float(metrics.box.mr), 4),
        "mAP50": round(float(metrics.box.map50), 4),
        "mAP50_95": round(float(metrics.box.map), 4),
        "per_class_AP50": per_class,
    }

    REPORTS_DIR.mkdir(exist_ok=True)
    (REPORTS_DIR / "metrics.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    # графики обучения и матрица ошибок — в отчёт
    figures = REPORTS_DIR / "figures"
    figures.mkdir(exist_ok=True)
    for name in ["results.png", "confusion_matrix.png", "PR_curve.png"]:
        for folder in [train_dir, val_dir]:
            if (folder / name).exists():
                shutil.copy(folder / name, figures / f"train_{name}")
                break

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\nmAP@0.5 = {summary['mAP50']:.3f}  ->  reports/metrics.json")
    print(f"Веса модели: {best_weights}")


if __name__ == "__main__":
    main()
