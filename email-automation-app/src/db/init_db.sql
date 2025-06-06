-- Tabela użytkowników systemu
CREATE TABLE
    IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        email VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

-- Tabela adresów email potencjalnych klientów
CREATE TABLE
    IF NOT EXISTS email_addresses (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users (id) ON DELETE SET NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        company_name VARCHAR(255),
        address VARCHAR(255),
        phone VARCHAR(50),
        contact_name VARCHAR(255),
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

-- Dodanie brakujących kolumn jeśli nie istnieją
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='email_addresses' AND column_name='company_name') THEN
        ALTER TABLE email_addresses ADD COLUMN company_name VARCHAR(255);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='email_addresses' AND column_name='address') THEN
        ALTER TABLE email_addresses ADD COLUMN address VARCHAR(255);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='email_addresses' AND column_name='phone') THEN
        ALTER TABLE email_addresses ADD COLUMN phone VARCHAR(50);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='email_addresses' AND column_name='contact_name') THEN
        ALTER TABLE email_addresses ADD COLUMN contact_name VARCHAR(255);
    END IF;
END$$;

-- Tabela kalendarza wysyłek
CREATE TABLE
    IF NOT EXISTS email_calendar (
        id SERIAL PRIMARY KEY,
        email_address_id INTEGER REFERENCES email_addresses (id) ON DELETE CASCADE,
        user_id INTEGER REFERENCES users (id) ON DELETE SET NULL,
        send_type VARCHAR(50) NOT NULL, -- np. 'welcome', 'reminder', 'last_offer'
        send_date TIMESTAMP NOT NULL,
        response_received BOOLEAN DEFAULT FALSE,
        response_date TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

-- Szablony wiadomości email
CREATE TABLE IF NOT EXISTS email_templates (
    id SERIAL PRIMARY KEY,
    template_type VARCHAR(50) NOT NULL, -- np. 'welcome', 'reminder', 'last_offer'
    subject VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    days_after_previous INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela kampanii
CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dodanie powiązania szablonu z kampanią i ścieżki do załącznika
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='email_templates' AND column_name='campaign_id') THEN
        ALTER TABLE email_templates ADD COLUMN campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='email_templates' AND column_name='attachment_path') THEN
        ALTER TABLE email_templates ADD COLUMN attachment_path VARCHAR(255);
    END IF;
END$$;

-- Dodanie unikalnego indeksu na (template_type, campaign_id)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes WHERE tablename = 'email_templates' AND indexname = 'email_templates_template_type_campaign_id_key'
    ) THEN
        CREATE UNIQUE INDEX email_templates_template_type_campaign_id_key ON email_templates(template_type, campaign_id);
    END IF;
END$$;

-- Tabela statusów wysyłek dla kontaktów w kampaniach
CREATE TABLE IF NOT EXISTS campaign_progress (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    contact_id INTEGER REFERENCES email_addresses(id) ON DELETE CASCADE,
    current_stage VARCHAR(50) NOT NULL, -- np. 'not_sent', 'welcome_sent', 'reminder_sent', 'last_offer_sent', 'responded'
    last_send_date TIMESTAMP,
    response_date TIMESTAMP,
    UNIQUE (campaign_id, contact_id)
);

-- Tabela kroków (etapów) kampanii
CREATE TABLE IF NOT EXISTS campaign_steps (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    subject TEXT,
    body TEXT,
    days_after_prev INTEGER,
    attachment_path TEXT
);

-- Dodanie indeksu dla szybkiego sortowania kroków
CREATE INDEX IF NOT EXISTS idx_campaign_steps_campaign_id_order ON campaign_steps(campaign_id, step_order);