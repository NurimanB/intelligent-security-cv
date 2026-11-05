-- Таблица треков объектов (результат scripts/track_video.py)
-- Один объект = один track_id на протяжении нескольких кадров
CREATE TABLE IF NOT EXISTS detection_tracks (
    track_row_id  SERIAL PRIMARY KEY,
    camera_id     INTEGER REFERENCES cameras(camera_id),
    frame         INTEGER NOT NULL,
    track_id      INTEGER NOT NULL,
    object_class  VARCHAR(50),
    confidence    NUMERIC(4, 3),
    bbox_x        INTEGER,
    bbox_y        INTEGER,
    bbox_width    INTEGER,
    bbox_height   INTEGER
);

CREATE INDEX IF NOT EXISTS idx_tracks_camera_track ON detection_tracks (camera_id, track_id);

-- Сколько уникальных объектов каждого класса прошло перед камерой
SELECT camera_id, object_class, COUNT(DISTINCT track_id) AS unique_objects
FROM detection_tracks
GROUP BY camera_id, object_class
ORDER BY camera_id, unique_objects DESC;

-- Как долго (в кадрах) каждый объект оставался в кадре
SELECT track_id, object_class, MAX(frame) - MIN(frame) + 1 AS frames_visible
FROM detection_tracks
GROUP BY track_id, object_class
ORDER BY frames_visible DESC
LIMIT 10;
