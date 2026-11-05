"""
track_video.py

Детекция + мульти-объектный трекинг (ByteTrack) на видео.
Каждый объект получает уникальный track_id; результаты сохраняются в CSV
и, при указании --db-url, в таблицу detection_tracks (sql/03_tracks.sql).

Запуск:
    python scripts/track_video.py --source data/samples/video.mp4 \
        --weights runs/detect/voc_security/weights/best.pt
"""

import argparse
import time
from pathlib import Path

import pandas as pd
from ultralytics import YOLO

OUTPUT_CSV = "data/processed/tracks.csv"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="путь к видео или RTSP-ссылка")
    parser.add_argument("--weights", default="runs/detect/voc_security/weights/best.pt",
                        help="путь к best.pt, который печатает scripts/train.py")
    parser.add_argument("--camera-id", type=int, default=1)
    parser.add_argument("--conf", type=float, default=0.4)
    parser.add_argument("--db-url", default=None,
                        help="например postgresql://postgres:postgres@localhost/security_demo")
    return parser.parse_args()


def track(weights: str, source: str, camera_id: int, conf: float) -> tuple[pd.DataFrame, float]:
    model = YOLO(weights)
    rows = []
    frames = 0
    start = time.perf_counter()

    # stream=True — кадры обрабатываются по одному, без загрузки всего видео в память
    for frame_idx, result in enumerate(model.track(source=source, conf=conf, persist=True,
                                                   tracker="bytetrack.yaml", stream=True,
                                                   save=True, name="track",
                                                   exist_ok=True, verbose=False)):
        frames += 1
        boxes = result.boxes
        if boxes.id is None:
            continue
        for box, track_id in zip(boxes, boxes.id.int().tolist()):
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            rows.append({
                "camera_id": camera_id,
                "frame": frame_idx,
                "track_id": track_id,
                "object_class": result.names[int(box.cls[0])],
                "confidence": round(float(box.conf[0]), 3),
                "bbox_x": int(x1),
                "bbox_y": int(y1),
                "bbox_width": int(x2 - x1),
                "bbox_height": int(y2 - y1),
            })

    fps = frames / (time.perf_counter() - start)
    return pd.DataFrame(rows), fps


if __name__ == "__main__":
    args = parse_args()
    tracks_df, fps = track(args.weights, args.source, args.camera_id, args.conf)

    Path(OUTPUT_CSV).parent.mkdir(parents=True, exist_ok=True)
    tracks_df.to_csv(OUTPUT_CSV, index=False)

    if args.db_url:
        from sqlalchemy import create_engine
        tracks_df.to_sql("detection_tracks", create_engine(args.db_url),
                         if_exists="append", index=False)

    unique = tracks_df.groupby("object_class")["track_id"].nunique() if len(tracks_df) else {}
    print(f"Скорость обработки: {fps:.1f} кадров/с")
    print("Уникальных объектов по классам:")
    print(unique)
    print(f"\nРезультаты сохранены в: {OUTPUT_CSV}; видео с треками — runs/detect/track/")
