CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS docs (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    uuid VARCHAR(200) NOT NULL,
    PRIMARY KEY (user_id, uuid)
);

INSERT INTO users (email, password_hash, username)
VALUES 
    ('1', '$2b$12$geI3.Ne2XuTf7I1ajxuHrud7QM8gMwDMaUd50I/8htSdThSHWey8e', 'Iaroslav'),
    ('2', '$2b$12$2dy2ahciSCTyrkBv1WbvUuI.4BuYoAGLCHEY7rgGUyt5u7IOw7pH6', 'Zik');
