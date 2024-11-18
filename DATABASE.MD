# Media Company Article Management System

## Overview

This project implements an internal article management system using Django. The system allows users to manage articles with role-based access control (RBAC) where different user roles have different permissions.

## User Roles

The system supports three primary user roles:

- **Journalist**: Can create and edit articles.
- **Editor**: Can review and edit articles written by journalists, but cannot create new ones.
- **Admin**: Has full access to all resources, including managing users, articles, and other administrative tasks.

### Database Design

The project uses Django's built-in `auth_user` table to manage user authentication. This table is extended with a custom `role` field and `is_staff` attribute for role-based access. The roles are handled via the `is_staff` field and can be further customized using Django's permissions system.
- **Admin**: Has full access, including managing users, groups, and permissions.
- **Editor**: Assigned can_approve_article, can_edit_article.
- **Journalist**: Assigned can_create_article, can_edit_own_article.
- **User**: Assigned can_read_article, can_comment, can_like.


```sql
-- User table definition (Managed by Django)
CREATE TABLE auth_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,         -- Unique username for the user
    password VARCHAR(128) NOT NULL,                -- Hashed password
    first_name VARCHAR(30),                        -- Optional first name
    last_name VARCHAR(30),                         -- Optional last name
    email VARCHAR(254),                            -- Email address
    is_staff BOOLEAN DEFAULT FALSE,                -- Admins and Editors (elevated access)
    is_active BOOLEAN DEFAULT TRUE,                -- Determines if the user is active
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- User's account creation date
    last_login TIMESTAMP,                          -- Last login timestamp
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('journalist', 'editor', 'admin', 'user')), -- Dynamic role assignment
    group_id INTEGER REFERENCES auth_group(id)     -- FK to auth_group for role-based permissions
);
-- Custom Roles: You can add a `role` field for Journalist, Editor, Admin or use Django's `groups` system.
-- Example: Role can be added in the Django `User` model.
```
### Supporting auth_group Table
To define roles like journalist, editor, and admin, the auth_group table is utilized.

```sql 
CREATE TABLE auth_group (
    id SERIAL PRIMARY KEY,
    name VARCHAR(80) NOT NULL UNIQUE              -- e.g., 'Journalist', 'Editor', 'Admin'
);
```
### Mapping Users to Groups
Each user can belong to one or more groups via a many-to-many relationship:
```sql
CREATE TABLE auth_user_groups (
    user_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    group_id INTEGER REFERENCES auth_group(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, group_id)
);
```
### Custom Permissions via auth_permission
You can define additional permissions for actions like creating, editing, reviewing, approving, and publishing articles.
```sql 
CREATE TABLE auth_permission (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,                -- Human-readable name (e.g., 'Can publish article')
    codename VARCHAR(100) NOT NULL UNIQUE,     -- Permission identifier (e.g., 'can_publish_article')
    content_type_id INTEGER NOT NULL,          -- Links to models (content types)
    group_id INTEGER REFERENCES auth_group(id) -- Permission assigned to groups
);
```

### Articles Table

This table will hold the main data for each article, such as title, content, author, tags, etc.

- status: We define four possible statuses: draft, pending, published, rejected. This can be useful for controlling the flow of articles through different stages (e.g., Journalists create drafts, Editors approve or reject, Admins can publish). 
    - status: The status can be draft, pending, approved, rejected, or published.
        - **Draft**: Only accessible by the author.
        - **Pending**: Submitted for review.
        - **Approved**: Approved by an Editor.
        - **Rejected**: Rejected by an Editor.
        - **Published**: Only Admin can set this status after approval.

```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    subtitle VARCHAR(255),
    content TEXT NOT NULL,
    author_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,  -- FK to User table
    image_url VARCHAR(255),    -- URL or path to the article image
    publish_date TIMESTAMP,    -- Article's publish date
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'pending', 'approved', 'rejected', 'published')),  -- Admins control publishing
    reviewed_by INTEGER REFERENCES auth_user(id),  -- FK to Editor who reviewed (if any)
    approved_at TIMESTAMP -- Time when article was approved or rejected
);
```
### Categories Table

You might want to categorize articles into groups such as "News", "Opinion", "Feature", etc.

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);
```

### Tags Table

You can associate multiple tags with an article, so it's a many-to-many relationship.

```sql 
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- Many-to-many relationship between articles and tags
CREATE TABLE article_tags (
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (article_id, tag_id)
);
```

### Permissions Table 

If you want to extend Django's permissions model, you can create a custom permissions table for specific actions like creating, editing, reviewing, and publishing articles.
```sql 
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT
);
```
### Article Reviews Table (for Editors)

This table stores the feedback or approval status of the articles as they are reviewed by Editors.

```sql 
CREATE TABLE article_reviews (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    reviewer_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,  -- FK to the editor reviewing the article
    status VARCHAR(50) CHECK (status IN ('approved', 'rejected', 'pending')),
    comments TEXT,
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

###  Audit/History Table

If you need to keep track of changes made to articles (for instance, to track edits), you can add an audit table:

```sql 
CREATE TABLE article_history (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    changed_by INTEGER REFERENCES auth_user(id),
    change_type VARCHAR(50) CHECK (change_type IN ('created', 'edited', 'published', 'deleted')),
    change_details TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Article Image Uploads

If you need a more robust way to manage images and files separately:

```sql 
CREATE TABLE article_images (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    image_url VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
### Comments Table:
This table will allow users to comment on articles, and users can also reply to existing comments.
- **parent_comment_id**: This is used to allow nested replies to comments. If parent_comment_id is NULL, it is a top-level comment; otherwise, it's a reply to another comment.
```sql 
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,  -- FK to Articles
    user_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,  -- FK to User (commenter)
    content TEXT NOT NULL,   -- Comment content
    parent_comment_id INTEGER REFERENCES comments(id),  -- FK for replies
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Likes Table (for Articles and Comments):
Users can like articles and comments. This is a simple many-to-many relationship.
- **article_likes**: Users can like articles.
- **comment_likes**: Users can like comments.
```sql 
CREATE TABLE article_likes (
    user_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,  -- FK to User
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,  -- FK to Article
    PRIMARY KEY (user_id, article_id)
);

CREATE TABLE comment_likes (
    user_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,  -- FK to User
    comment_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,  -- FK to Comment
    PRIMARY KEY (user_id, comment_id)
);
```

