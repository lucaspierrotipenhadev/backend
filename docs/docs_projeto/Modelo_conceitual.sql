-- Tabela de usuários
CREATE TABLE USER (
    id BIGINT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Perfil do usuário
CREATE TABLE PROFILE (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    bio TEXT,
    avatar VARCHAR(255),
    birth_date DATE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    CONSTRAINT fk_profile_user FOREIGN KEY (user_id) REFERENCES USER(id) ON DELETE CASCADE
);

-- Publicações
CREATE TABLE POST (
    id BIGINT PRIMARY KEY,
    author_id BIGINT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    edited BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_post_author FOREIGN KEY (author_id) REFERENCES USER(id) ON DELETE CASCADE
);

-- Mídias de publicações
CREATE TABLE POSTMEDIA (
    id BIGINT PRIMARY KEY,
    post_id BIGINT NOT NULL,
    file VARCHAR(255) NOT NULL,
    media_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_postmedia_post FOREIGN KEY (post_id) REFERENCES POST(id) ON DELETE CASCADE
);

-- Comentários (com auto-referência)
CREATE TABLE COMMENT (
    id BIGINT PRIMARY KEY,
    author_id BIGINT NOT NULL,
    post_id BIGINT NOT NULL,
    parent_id BIGINT,
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    CONSTRAINT fk_comment_author FOREIGN KEY (author_id) REFERENCES USER(id) ON DELETE CASCADE,
    CONSTRAINT fk_comment_post FOREIGN KEY (post_id) REFERENCES POST(id) ON DELETE CASCADE,
    CONSTRAINT fk_comment_parent FOREIGN KEY (parent_id) REFERENCES COMMENT(id) ON DELETE CASCADE
);

-- Curtidas em posts
CREATE TABLE POSTLIKE (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    post_id BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT uq_postlike UNIQUE (user_id, post_id),
    CONSTRAINT fk_postlike_user FOREIGN KEY (user_id) REFERENCES USER(id) ON DELETE CASCADE,
    CONSTRAINT fk_postlike_post FOREIGN KEY (post_id) REFERENCES POST(id) ON DELETE CASCADE
);

-- Curtidas em comentários
CREATE TABLE COMMENTLIKE (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    comment_id BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT uq_commentlike UNIQUE (user_id, comment_id),
    CONSTRAINT fk_commentlike_user FOREIGN KEY (user_id) REFERENCES USER(id) ON DELETE CASCADE,
    CONSTRAINT fk_commentlike_comment FOREIGN KEY (comment_id) REFERENCES COMMENT(id) ON DELETE CASCADE
);

-- Seguidores entre usuários
CREATE TABLE FOLLOWUSER (
    id BIGINT PRIMARY KEY,
    follower_id BIGINT NOT NULL,
    following_id BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT uq_follow UNIQUE (follower_id, following_id),
    CONSTRAINT fk_follow_follower FOREIGN KEY (follower_id) REFERENCES USER(id) ON DELETE CASCADE,
    CONSTRAINT fk_follow_following FOREIGN KEY (following_id) REFERENCES USER(id) ON DELETE CASCADE
);