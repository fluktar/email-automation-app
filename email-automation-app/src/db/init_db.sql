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