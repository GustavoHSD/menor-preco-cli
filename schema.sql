CREATE TABLE IF NOT EXISTS local (
    id INTEGER PRIMARY KEY,
    geohash TEXT UNIQUE,
    name TEXT
);

CREATE TABLE IF NOT EXISTS category (
    id INTEGER PRIMARY KEY,
    nota_id TEXT UNIQUE, 
    description TEXT
);

CREATE TABLE IF NOT EXISTS query (
    id INTEGER PRIMARY KEY,
    term TEXT,
    radius REAL,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES category(id)
);

CREATE TABLE IF NOT EXISTS query_local (
    query_id INTEGER,
    local_id INTEGER,
    FOREIGN KEY (query_id) REFERENCES query(id),
    FOREIGN KEY (local_id) REFERENCES local(id),
    PRIMARY KEY (query_id, local_id)
);

CREATE TABLE IF NOT EXISTS spreadsheet (
    id INTEGER PRIMARY KEY,
    google_id TEXT UNIQUE,
    query_id INTEGER,
    is_populated INTEGER,
    last_populated TEXT,
    FOREIGN KEY (query_id) REFERENCES query(id)
);
