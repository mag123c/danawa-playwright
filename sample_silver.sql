CREATE TABLE crawl_sources (
    id SERIAL PRIMARY KEY,                      -- 내부 시스템용 크롤링 소스 ID
    source_name VARCHAR(100) NOT NULL unique,   -- 크롤링 소스 이름 ('danawa', 'naver' 등)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE crawl_sources IS '크롤링 출처';
COMMENT on COLUMN crawl_sources.source_name is '크롤링 소스 이름(danawa, naver 등)';



CREATE TABLE categories_silver (
    id BIGSERIAL PRIMARY KEY,                   -- 내부 시스템용 카테고리 고유 ID
    crawl_source_id INTEGER NOT NULL,           -- 크롤링 소스 ID (FK)
    category_code VARCHAR(100) NOT NULL,        -- 카테고리 코드
    category_name VARCHAR(255),                 -- 카테고리명
    parent_category_code VARCHAR(100),          -- 부모 카테고리 코드 (Optional)
    depth SMALLINT,                             -- 카테고리 깊이
    raw_data JSONB,                             -- 크롤링한 카테고리 관련 모든 원본 정보
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,  --

    CONSTRAINT fk_categories_crawl_source
        FOREIGN KEY(crawl_source_id)
        REFERENCES crawl_sources(id)
        ON DELETE RESTRICT, -- 소스 정보가 삭제되면 해당 소스의 카테고리도 문제이므로 제한
    CONSTRAINT uq_category_source_code UNIQUE (crawl_source_id, category_code)
);
COMMENT ON TABLE categories_silver IS '크롤링된 카테고리 테이블 (silver layer)';
COMMENT ON COLUMN categories_silver.category_name IS '카테고리명';
COMMENT ON COLUMN categories_silver.depth IS '카테고리 깊이';
COMMENT ON COLUMN categories_silver.raw_data IS '크롤링한 카테고리 관련 모든 원본 정보';



CREATE TABLE products_silver (
    id BIGSERIAL PRIMARY KEY,
    crawl_source_id INTEGER NOT NULL,
    product_id VARCHAR(255) NOT NULL,
    product_name TEXT,
    category_silver_id BIGINT,
    detail_url TEXT,
    image_url TEXT,
    raw_specs_text TEXT,
    parsed_specs_json JSONB,
    price VARCHAR(50),
    maker VARCHAR(255),
    review_count INTEGER,
    average_rating DECIMAL(3, 1),
    crawled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_products_crawl_source
        FOREIGN KEY(crawl_source_id)
        REFERENCES crawl_sources(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_products_source_category
        FOREIGN KEY(category_silver_id)
        REFERENCES categories_silver(id)
        ON DELETE SET NULL,

    CONSTRAINT uq_product_source_id_crawled_at
        UNIQUE (crawl_source_id, product_id, crawled_at)
);
COMMENT ON TABLE products_silver IS '크롤링된 상품 데이터 테이블 (silver layer)';
COMMENT ON COLUMN products_silver.id IS '내부 시스템용 상품 고유 ID';
COMMENT ON COLUMN products_silver.crawl_source_id IS '크롤링 소스 ID (FK)';
COMMENT ON COLUMN products_silver.product_id IS '커머스의 상품 ID (예: productItem6062612)';
COMMENT ON COLUMN products_silver.product_name IS '상품명';
COMMENT ON COLUMN products_silver.category_silver_id IS 'categories_silver.id (FK)';
COMMENT ON COLUMN products_silver.detail_url IS '상품 상세 페이지 URL';
COMMENT ON COLUMN products_silver.image_url IS '대표 이미지 URL';
COMMENT ON COLUMN products_silver.raw_specs_text IS '''raw_specs'' 원본 문자열';
COMMENT ON COLUMN products_silver.parsed_specs_json IS '''specs'' 파싱 결과 JSON 객체';
COMMENT ON COLUMN products_silver.price IS '가격';
COMMENT ON COLUMN products_silver.maker IS '제조사명';
COMMENT ON COLUMN products_silver.review_count IS '리뷰 개수';
COMMENT ON COLUMN products_silver.average_rating IS '평균 평점';
COMMENT ON COLUMN products_silver.crawled_at IS '크롤링 시점';
COMMENT ON COLUMN products_silver.created_at IS '레코드 생성 시각';
COMMENT ON COLUMN products_silver.updated_at IS '레코드 갱신 시각';



CREATE TABLE reviews_silver (
    id BIGSERIAL PRIMARY KEY,
    crawl_source_id INTEGER NOT NULL,
    product_silver_id BIGINT NOT NULL,
    review TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_reviews_crawl_source
        FOREIGN KEY(crawl_source_id)
        REFERENCES crawl_sources(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_reviews_product_silver_id
        FOREIGN KEY(product_silver_id)
        REFERENCES products_silver(id)
        ON DELETE CASCADE
);
COMMENT ON TABLE reviews_silver IS '크롤링된 리뷰 데이터 테이블 (silver layer)';
COMMENT ON COLUMN reviews_silver.id IS '내부 시스템용 리뷰 고유 ID';
COMMENT ON COLUMN reviews_silver.crawl_source_id IS '크롤링 소스 ID (FK)';
COMMENT ON COLUMN reviews_silver.product_silver_id IS 'products_silver.id (FK)';
COMMENT ON COLUMN reviews_silver.review IS '리뷰 내용';
COMMENT ON COLUMN reviews_silver.created_at IS '레코드 생성 시각';
COMMENT ON COLUMN reviews_silver.updated_at IS '레코드 갱신 시각';
