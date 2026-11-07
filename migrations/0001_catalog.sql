CREATE TABLE catalog_state (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    revision INTEGER NOT NULL CHECK (revision >= 0),
    source_hash TEXT NOT NULL
);
INSERT INTO catalog_state VALUES (1, 0, '');

CREATE TABLE items (
    id TEXT PRIMARY KEY,
    body TEXT NOT NULL,
    brand TEXT,
    sort_brand TEXT NOT NULL,
    name TEXT NOT NULL,
    sort_name TEXT NOT NULL,
    category TEXT NOT NULL,
    sku TEXT,
    confirmed INTEGER NOT NULL CHECK (confirmed IN (0, 1)),
    archived INTEGER NOT NULL CHECK (archived IN (0, 1)),
    revision INTEGER NOT NULL CHECK (revision > 0),
    styling_hash TEXT NOT NULL
);
CREATE INDEX items_active_order ON items(archived, sort_brand, sort_name, id);
CREATE INDEX items_active_category ON items(archived, category);
CREATE INDEX items_active_confirmed ON items(archived, confirmed);

CREATE TABLE operations (
    scope TEXT NOT NULL,
    actor TEXT NOT NULL,
    key TEXT NOT NULL,
    request_hash TEXT NOT NULL,
    response TEXT,
    resource_id TEXT,
    PRIMARY KEY (scope, actor, key)
);

CREATE TABLE generations (
    id TEXT PRIMARY KEY,
    local_date TEXT NOT NULL,
    timezone TEXT NOT NULL,
    config_hash TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('running', 'succeeded', 'failed', 'interrupted')),
    body TEXT NOT NULL,
    basis TEXT NOT NULL,
    started_at TEXT NOT NULL
);
CREATE UNIQUE INDEX one_running_generation ON generations(status) WHERE status = 'running';
CREATE INDEX generations_date ON generations(local_date, started_at DESC, id DESC);

CREATE TABLE today_results (
    local_date TEXT PRIMARY KEY,
    timezone TEXT NOT NULL,
    config_hash TEXT NOT NULL,
    body TEXT NOT NULL,
    signatures TEXT NOT NULL
);
