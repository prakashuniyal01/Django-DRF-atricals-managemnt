# Media Article Management System

## Overview
The **Media Article Management System** is a Django-based web application designed to streamline the management of articles within a media company. The system includes role-based access for **Journalists**, **Editors**, and **Admins**, as well as public API access for retrieving published articles.

## Features

### Core Features
1. **User Roles and Permissions**
   - **Journalist**: Submit and edit their own articles.
   - **Editor**: Review, approve, reject, and edit articles.
   - **Admin**: Full control over articles, users, and system settings.

2. **Article Workflow**
   - Draft → Pending Review → Approved → Published/Rejected
   - Multi-page form for article submission.

3. **API Integration**
   - CRUD operations for articles.
   - Public API endpoint for published articles.
   - Token-based authentication.

4. **Engagement**
   - Commenting and liking on articles.
   - Notifications for status changes (submitted, approved, rejected, published).

5. **Metrics**
   - Track article views, likes, and engagement metrics.

- Password reset via email.
- Email notifications for article status updates.
- Search and filter functionality for articles.

---

## Installation

### Prerequisites
- Python 
- SQL
- Django 
- Django REST Framework (DRF)
- Cloudinary for img upload


## overall 

- **Scenario**: You have been hired by a media company to develop an internal article management system. Journalists, editors, and administrators will use the system to create, edit, review, and publish articles. The system also includes an API to allow integration with third-party platforms.
- 
- You need to build the following features in the system:
- Part 1: Article Submission Form
- The first task is to create a two-page form that allows journalists to submit articles for review.
- 
- Form Fields:
- Page 1:
- Title (Text Field)
- Subtitle (Text Field)
- Article Content (Text Area)
- Author Name (Text Field)
- Email Address (Email Field)

- Page 2:
- Article Image (File Upload)
- Tags (Checkboxes for predefined tags like Politics, Sports, Tech, etc.)
- Category (Dropdown with categories like News, Opinion, Feature)
- Publish Date (Date Field, must be a future date)
- Agree to Terms (Checkbox)
- Custom Validation:
- Ensure the title is at least 10 characters long.
- Validate that the publish date is in the future.
- Email field must have a valid format.
- Ensure that the terms checkbox is checked.
- Pagination:
- Implement pagination to split the form across two pages, with the ability to navigate between pages without losing form data.
- Error Handling:
- Display validation errors with user-friendly messages.
- Part 2: Article Management System (Backend & API)
- The second part involves building the backend for managing articles and users, including authentication, CRUD operations, and API integration.

- Authentication:
- Implement user registration, login, and logout functionality.
- Use Django's built-in authentication system.
- Allow users to reset passwords via email.
- Authorization:
- Three user roles:
- Journalist: Can submit and edit their own articles but cannot publish them.
- Editor: Can review, approve, and publish articles.
- Admin: Has full access to create, edit, delete, and manage users.
- Use Django’s permission system to restrict actions based on roles.
- CRUD Operations:
- Create a model called Article with fields such as title, content, author, image, tags, category, and publish_date.
- Journalists can create and edit their own articles.
- Editors can approve, reject, or publish articles.
- Admins can manage articles and users.
- Django Rest Framework (DRF) API:
- Create an API for the Article model using DRF.
- Implement CRUD operations via the API.
- Use Token Authentication for the API.
- Restrict API access based on user roles (e.g., only Editors and Admins can approve or publish articles).
- Implement pagination, search, and filtering in the API (e.g., filter articles by category or search by title).
- Implement email notifications when an article is submitted for review and when it is approved or rejected.
- Create an endpoint for retrieving a list of published articles, accessible to the public.