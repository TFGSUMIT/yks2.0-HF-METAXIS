PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS metaxis_threads (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS metaxis_turns (
    id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    classification TEXT NOT NULL CHECK (classification = 'DEVELOPMENT'),
    operator_text TEXT NOT NULL,
    assistant_text TEXT NOT NULL,
    route TEXT NOT NULL,
    FOREIGN KEY (thread_id) REFERENCES metaxis_threads(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_metaxis_threads_updated
    ON metaxis_threads(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_metaxis_turns_thread_created
    ON metaxis_turns(thread_id, created_at);

CREATE TABLE IF NOT EXISTS metaxis_state_events (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    classification TEXT NOT NULL CHECK (classification = 'DEVELOPMENT'),
    payload_json TEXT NOT NULL CHECK (json_valid(payload_json)),
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_metaxis_state_events_subject_created
    ON metaxis_state_events(subject_id, created_at);
CREATE INDEX IF NOT EXISTS idx_metaxis_state_events_type_created
    ON metaxis_state_events(event_type, created_at);

CREATE TRIGGER IF NOT EXISTS metaxis_state_events_no_update
BEFORE UPDATE ON metaxis_state_events
BEGIN
    SELECT RAISE(ABORT, 'metaxis_state_events is append-only');
END;

CREATE TRIGGER IF NOT EXISTS metaxis_state_events_no_delete
BEFORE DELETE ON metaxis_state_events
BEGIN
    SELECT RAISE(ABORT, 'metaxis_state_events is append-only');
END;
