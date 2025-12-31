-- GIN индекс на trigram по тексту JSON
CREATE INDEX IF NOT EXISTS idx_product_meta_trgm
ON product
USING GIN ((meta::text) gin_trgm_ops);

