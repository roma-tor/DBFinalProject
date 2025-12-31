-- включаем расширение pg_trgm (один раз на базу)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- добавляем JSONB поле
ALTER TABLE product
ADD COLUMN IF NOT EXISTS meta JSONB;

-- наполняем JSON полем (пример)
UPDATE product
SET meta = jsonb_build_object(
  'tags', jsonb_build_array('food', 'daily'),
  'desc', 'Basic product description',
  'brand', COALESCE(manufacturer, 'unknown')
)
WHERE meta IS NULL;

