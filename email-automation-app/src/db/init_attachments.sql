-- Tabela załączników do kroków kampanii
CREATE TABLE
    IF NOT EXISTS attachments (
        id SERIAL PRIMARY KEY,
        step_id INTEGER REFERENCES campaign_steps (id) ON DELETE CASCADE,
        filename TEXT NOT NULL,
        remote_path TEXT NOT NULL
    );

CREATE INDEX IF NOT EXISTS idx_attachments_step_id ON attachments (step_id);