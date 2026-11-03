CREATE TABLE IF NOT EXISTS reports (
    region      TEXT NOT NULL,
    week_start  TEXT NOT NULL,          -- 'YYYY-MM-DD'
    file_name   TEXT NOT NULL,
    loaded_at   TEXT NOT NULL,
    PRIMARY KEY (region, week_start)
);

CREATE TABLE IF NOT EXISTS prices (
    id          INTEGER PRIMARY KEY,
    region      TEXT NOT NULL,
    week_start  TEXT NOT NULL,
    city        TEXT NOT NULL,
    product     TEXT NOT NULL,
    brand       TEXT NOT NULL,
    price_low   REAL NOT NULL,
    price_high  REAL NOT NULL,
    CHECK (price_low <= price_high),
    UNIQUE (region, week_start, city, product, brand),
    FOREIGN KEY (region, week_start) REFERENCES reports (region, week_start)
);