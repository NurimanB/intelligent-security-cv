-- =====================================================================
-- Примеры SQL-запросов, которые обычно поручают стажёру:
-- JOIN, агрегация по дням и поиск пропущенных значений
-- =====================================================================

-- 1. JOIN: получить детекции вместе с названием локации камеры
SELECT
    d.log_id,
    c.location_name,
    d.object_class,
    d.confidence,
    d.detected_at
FROM detection_logs d
JOIN cameras c ON d.camera_id = c.camera_id
ORDER BY d.detected_at;

-- 2. GROUP BY: посчитать количество инцидентов по дням
SELECT
    DATE(detected_at) AS detection_day,
    COUNT(*)          AS total_events
FROM detection_logs
WHERE detected_at IS NOT NULL
GROUP BY DATE(detected_at)
ORDER BY detection_day;

-- 3. Поиск строк с пропущенными значениями (для последующей очистки в Pandas)
SELECT *
FROM detection_logs
WHERE camera_id IS NULL
   OR object_class IS NULL
   OR confidence IS NULL;
