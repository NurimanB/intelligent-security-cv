-- =====================================================================
-- Схема базы данных для системы видеоаналитики (учебный/демо-проект)
-- Уровень: стажёр (junior) — простые таблицы, без сложной нормализации
-- =====================================================================

-- Таблица камер видеонаблюдения
CREATE TABLE IF NOT EXISTS cameras (
    camera_id     SERIAL PRIMARY KEY,
    location_name VARCHAR(100) NOT NULL,   -- например, 'Главный вход', 'Парковка'
    is_active     BOOLEAN DEFAULT TRUE,
    installed_at  DATE
);

-- Таблица логов детекции объектов (сырые данные, как их отдаёт модель)
-- Специально оставлены "грязные" данные: NULL-значения и дубликаты,
-- т.к. на практике исходные данные почти никогда не бывают идеальными
CREATE TABLE IF NOT EXISTS detection_logs (
    log_id          SERIAL PRIMARY KEY,
    camera_id       INTEGER REFERENCES cameras(camera_id),
    detected_at     TIMESTAMP,
    object_class    VARCHAR(50),      -- 'person', 'vehicle', 'unattended_bag'
    confidence      NUMERIC(4, 3),    -- уверенность модели, от 0 до 1
    bbox_x          INTEGER,          -- координата X левого верхнего угла
    bbox_y          INTEGER,          -- координата Y левого верхнего угла
    bbox_width      INTEGER,
    bbox_height     INTEGER
);

-- Наполняем таблицу камер
INSERT INTO cameras (location_name, is_active, installed_at) VALUES
    ('Главный вход', TRUE, '2023-02-10'),
    ('Парковка A',   TRUE, '2023-02-10'),
    ('Складское помещение', TRUE, '2023-05-01'),
    ('Запасной выход', FALSE, '2022-11-20');

-- Наполняем таблицу логов детекции (небольшой пример "грязных" данных)
INSERT INTO detection_logs
    (camera_id, detected_at, object_class, confidence, bbox_x, bbox_y, bbox_width, bbox_height)
VALUES
    (1, '2024-06-01 08:12:03', 'person',  0.91, 120, 45, 60, 140),
    (1, '2024-06-01 08:12:03', 'person',  0.91, 120, 45, 60, 140), -- дубликат строки
    (2, '2024-06-01 09:05:11', 'vehicle', 0.87, 300, 210, 220, 130),
    (2, '2024-06-01 09:07:45', 'vehicle', NULL, 310, 205, 200, 120), -- пропущена confidence
    (3, '2024-06-01 12:30:00', NULL,      0.76, 90, 60, 40, 90),      -- пропущен класс объекта
    (1, '2024-06-01 18:45:22', 'person',  0.65, -10, 20, 55, 130),    -- некорректная координата (bbox_x < 0)
    (2, '2024-06-02 07:59:59', 'vehicle', 0.94, 250, 190, -50, 100),  -- некорректная ширина (bbox_width < 0)
    (3, '2024-06-02 14:22:10', 'unattended_bag', 0.58, 400, 300, 35, 40),
    (NULL, '2024-06-02 15:00:00', 'person', 0.72, 100, 100, 50, 120); -- пропущен camera_id
