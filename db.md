# Media Article Management System - Database Schema and Queries

## Overview

This document outlines the database schema for the **Media Article Management System**. The database is designed to support user management, role-based access control (RBAC), article management, and engagement features like comments and likes.

## Database Structure

### Entity-Relationship Diagram (ERD)
The system consists of the following key entities:
- **Users**: Manages user accounts, roles, and permissions.
- **Articles**: Stores article data including content, status, and associated metadata.
- **Comments**: Tracks comments on articles with support for nested replies.
- **Likes**: Records likes for articles and comments.
- **Article Reviews**: Handles the review and approval process for articles.
- **Notifications**: Tracks user notifications for system updates.

---

## Tables and Queries

### 1. **Users (auth_user)**
Manages user accounts, including authentication and roles.

#### Table Definition
```sql
-- Optimized Database Schema for Media Company Article Management System

CREATE TABLE auth_user (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(254) UNIQUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    role ENUM('journalist', 'editor', 'admin', 'user') DEFAULT 'user',
    CONSTRAINT chk_role CHECK (role IN ('journalist', 'editor', 'admin', 'user'))
);

-- Roles/Groups Table
CREATE TABLE auth_group (
    id SERIAL PRIMARY KEY,
    name VARCHAR(80) NOT NULL UNIQUE
);

-- User-Group Relationship
CREATE TABLE auth_user_groups (
    user_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    group_id INTEGER REFERENCES auth_group(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, group_id)
);

-- Permissions Table
CREATE TABLE auth_permission (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    codename VARCHAR(100) NOT NULL UNIQUE
);

-- Group Permissions
CREATE TABLE auth_group_permissions (
    group_id INTEGER REFERENCES auth_group(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES auth_permission(id) ON DELETE CASCADE,
    PRIMARY KEY (group_id, permission_id)
);

-- Articles Table
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    subtitle VARCHAR(200),
    content TEXT NOT NULL,
    author_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    image_url VARCHAR(255),
    publish_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('draft', 'pending', 'approved', 'rejected', 'published') DEFAULT 'draft',
    reviewed_by INTEGER REFERENCES auth_user(id),
    approved_at TIMESTAMP,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    deleted_at TIMESTAMP
);

-- Categories Table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- Tags Table
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- Article-Tag Relationship
CREATE TABLE article_tags (
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (article_id, tag_id)
);

-- Comments Table
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    parent_comment_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Likes for Articles
CREATE TABLE article_likes (
    user_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, article_id)
);

-- Likes for Comments
CREATE TABLE comment_likes (
    user_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    comment_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, comment_id)
);

-- Article Review Table
CREATE TABLE article_reviews (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    reviewer_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    status ENUM('approved', 'rejected', 'pending') DEFAULT 'pending',
    comments TEXT,
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Article History Table
CREATE TABLE article_history (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    changed_by INTEGER REFERENCES auth_user(id),
    change_type ENUM('created', 'edited', 'published', 'deleted'),
    change_details TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Article Image Uploads
CREATE TABLE article_images (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    image_url VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE password_reset_token (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    token UUID DEFAULT uuid_generate_v4() NOT NULL,
    expiration_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Check if a token is expired
SELECT * FROM password_reset_token WHERE token = 'user-provided-token' AND expiration_time > NOW();
