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