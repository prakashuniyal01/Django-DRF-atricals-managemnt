# API Endpoints Overview

## Public Endpoints (Accessible to All Users)

### List Published Articles
**GET** `/api/public/articles/`  
- List all published articles.  
- Supports filters (`?category=`, `?tag=`, `?search=`, `?author=`) and pagination.  

### Retrieve a Published Article
**GET** `/api/public/articles/{id}/`  
- View details of a published article.  

## Authenticated User Endpoints

### Comments and Likes (All Authenticated Users)

#### List Comments on an Article
**GET** `/api/articles/{id}/comments/`  
- Fetch all comments on a specific article.  

#### Add a Comment to an Article
**POST** `/api/articles/{id}/comments/`  
- Add a new comment.  

#### Like/Unlike an Article
**POST** `/api/articles/{id}/like/`  
- Like or unlike a specific article.  

#### Like/Unlike a Comment
**POST** `/api/comments/{id}/like/`  
- Like or unlike a specific comment.  

#### Delete a Comment
**DELETE** `/api/comments/{id}/`  
- Only Admin or comment owner can delete.  

## Journalist-Specific Endpoints

### List Own Articles
**GET** `/api/articles/`  
- Journalists can view only their own articles.  

### Create an Article
**POST** `/api/articles/`  
- Journalists can submit a new article for review.  

### Update Own Article
**PUT** `/api/articles/{id}/`  
- Journalists can edit their own articles in draft or pending status.  

### Delete Own Article
**DELETE** `/api/articles/{id}/`  
- Journalists can delete their own articles in draft status.  

## Editor-Specific Endpoints

### List All Articles for Review
**GET** `/api/articles/`  
- Editors can view all articles, except deleted ones.  

### Review an Article
**POST** `/api/articles/{id}/review/`  
- Editors can approve or reject articles with comments.  

### Edit an Article
**PUT** `/api/articles/{id}/`  
- Editors can edit articles submitted by journalists before approval or publishing.  

### Publish an Article
**POST** `/api/articles/{id}/publish/`  
- Editors can publish approved articles.  

## Admin-Specific Endpoints

### Full CRUD Access to Articles
#### List All Articles
**GET** `/api/articles/`  
- List all articles, including drafts, pending, rejected, and published.  

#### Create an Article
**POST** `/api/articles/`  
- Admins can create articles.  

#### Edit Any Article
**PUT** `/api/articles/{id}/`  
- Admins can edit any article.  

#### Delete Any Article
**DELETE** `/api/articles/{id}/`  
- Admins can delete (soft delete) any article.  

### Manage Users, Tags, and Categories
#### Categories
**GET** `/api/categories/`  
**POST** `/api/categories/`  
**PUT** `/api/categories/{id}/`  
**DELETE** `/api/categories/{id}/`  

#### Tags and Users
- Similar endpoints for managing tags and users.  

## Notifications Workflow

### Journalist Posts an Article
- Notify all editors and admins about a new submission.  

### Article Approved or Rejected
- Notify the journalist who submitted the article.  

### User Comments or Likes an Article
- Notify the journalist who owns the article.  

## Summary of Role Responsibilities

| Role        | Responsibilities                                                                                  |
|-------------|--------------------------------------------------------------------------------------------------|
| **Admin**   | Full access: Manage users, articles, tags, categories, and publish articles.                     |
| **Editor**  | Review, edit, approve, and publish articles submitted by journalists.                            |
| **Journalist** | Create and manage their own articles (CRUD) but cannot publish directly.                       |
| **User**    | Read articles, comment, and like articles or comments.                                           |
