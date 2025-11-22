# JUST DO IT - Task Management Web Application

A collaborative task management system built with Django and vanilla JavaScript that allows users to organize personal and shared tasks with priority levels, due dates, and real-time status tracking.

---

## 📋 Table of Contents
- [Technology Stack](#technology-stack)
- [Backend Architecture](#backend-architecture)
- [Features](#features)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)

---

## 🛠 Technology Stack

### **Backend**
- **Framework:** Django 5.2.6
- **REST API:** Django REST Framework 3.16.1
- **Database:** SQLite (default, easily switchable to PostgreSQL/MySQL)
- **Soft Delete:** django-soft-delete 1.0.21
- **Authentication:** Token-based authentication

### **Frontend**
- **HTML5** - Semantic markup
- **JavaScript (ES6+)** - Vanilla JS with class-based architecture
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client for API requests

---

## 🏗 Backend Architecture

### **Why Django?**

Django was chosen as the backend framework for several compelling reasons:

1. **Batteries-Included Philosophy**
   - ORM (Object-Relational Mapping) for database interactions
   - Security features (CSRF protection, SQL injection prevention)
   - Follows MVC architecture which is a comfortable area for us 

2. **Django REST Framework (DRF)**
   - Built-in viewsets for CRUD operations
   - Token authentication support
   - Good for REST APIs and easy to integrate in frontend

3. **Rapid Development**
   - Minimal boilerplate code
   - Built-in migration system
   - Admin panel for quick data inspection
   - Extensive documentation and community support

4. **Scalability**
   - Can handle both small and large applications
   - Databases are easy to migrate (e.g. sqlite to pgql)
   - Support for async views in Django 5.x

5. **Python Ecosystem**
   - Clean, readable syntax
   - Rich library ecosystem
   - Easy to maintain and test

---

## ✨ Features

-  **Personal Task Management** - Create, read, update, delete tasks
-  **Collaborative Lists** - Share tasks with team members
-  **Priority Levels** - High, Mid, Low priority classification
-  **Due Date Tracking** - Set deadlines with date and time
-  **Search & Filter** - Search by title/description, filter by priority
-  **Soft Delete** - Restore accidentally deleted tasks
-  **User Authentication** - Secure signup/login with security questions
-  **Progress Tracking** - Visual completion statistics
-  **Modern UI** - Responsive design with smooth animations

---

## 📦 Installation & Setup

### **Prerequisites**
- Python 3.8 or higher
- pip (Python package manager)
- Git

### **Step 1: Clone the Repository**
```bash
git clone https://github.com/sizzlingsisig/cmsc128-IndivProject_-Hernia-.git
cd JustDoIt
```

### **Step 2: Create Virtual Environment**
```bash
# Windows
python -m venv env
env\Scripts\activate

# Mac/Linux
python3 -m venv env
source env/Scripts/activate
```

### **Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Core Dependencies:**
```
Django==5.2.6
djangorestframework==3.16.1
django-soft-delete==1.0.21
whitenoise
```

### **Step 4: Database Setup**
```bash
# Create database tables
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

---

## 🚀 Running the Application

### **Development Server**
```bash
python manage.py runserver
```

The application will be available at:
- **Main App:** http://localhost:8000/
- **Admin Panel:** http://localhost:8000/admin/
- **API Root:** http://localhost:8000/api/

### **Access Points**
- `/` - Authentication page (Login/Signup)
- `/tasks/` - Task management dashboard
- `/profile/` - User profile settings
- `/api/` - RESTful API endpoints

---

## 📡 API Documentation

### **Base URL**
```
http://localhost:8000/api/
```

### **Authentication**

All API requests (except login/signup) require token authentication:
```http
Authorization: Token <your-token-here>
```

---

### **User Endpoints**

#### **1. User Registration**
```http
POST /api/users/signup/
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "token": "a1b2c3d4e5f6g7h8i9j0",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### **2. User Login**
```http
POST /api/users/login/
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "token": "a1b2c3d4e5f6g7h8i9j0",
  "username": "johndoe"
}
```

#### **3. Get Current User**
```http
GET /api/users/me/
Authorization: Token <your-token>
```

**Response:**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### **4. Update Security Question**
```http
POST /api/users/update-security-question/
Authorization: Token <your-token>
Content-Type: application/json

{
  "security_question": "What is your pet's name?",
  "security_answer": "Fluffy"
}
```

#### **5. Change Password**
```http
POST /api/users/change-password/
Authorization: Token <your-token>
Content-Type: application/json

{
  "old_password": "oldpass123",
  "new_password": "newpass456"
}
```

#### **6. Logout**
```http
POST /api/users/logout/
Authorization: Token <your-token>
```

---

### **Task Endpoints**

#### **1. List Tasks**
```http
GET /api/tasks/
Authorization: Token <your-token>
```

**Query Parameters:**
- `view` - Filter by view type (`personal` or `collaborative`)
- `list_id` - Filter by collaborative list ID
- `deleted` - Include soft-deleted tasks (`true` or `false`)

**Examples:**
```http
# Get personal tasks
GET /api/tasks/?view=personal

# Get collaborative tasks
GET /api/tasks/?view=collaborative&list_id=5

# Get all tasks including deleted
GET /api/tasks/?deleted=true
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "Complete Django assignment",
    "description": "Implement REST API endpoints",
    "status": "In Progress",
    "priority": "High",
    "due_datetime": "2025-11-25T23:59:00",
    "created_at": "2025-11-22T10:30:00",
    "updated_at": "2025-11-22T15:45:00",
    "created_by_username": "johndoe",
    "collaborative_list": null
  },
  {
    "id": 2,
    "title": "Team meeting preparation",
    "description": "Prepare slides for sprint review",
    "status": "Not Started",
    "priority": "Mid",
    "due_datetime": "2025-11-24T14:00:00",
    "created_at": "2025-11-22T11:00:00",
    "updated_at": "2025-11-22T11:00:00",
    "created_by_username": "johndoe",
    "collaborative_list": 3
  }
]
```

#### **2. Create Task**
```http
POST /api/tasks/
Authorization: Token <your-token>
Content-Type: application/json

{
  "title": "Write unit tests",
  "description": "Add test coverage for API endpoints",
  "priority": "High",
  "status": "Not Started",
  "due_datetime": "2025-11-30T17:00:00",
  "collaborative_list_id": null
}
```

**Response:** `201 Created`
```json
{
  "id": 3,
  "title": "Write unit tests",
  "description": "Add test coverage for API endpoints",
  "status": "Not Started",
  "priority": "High",
  "due_datetime": "2025-11-30T17:00:00",
  "created_at": "2025-11-22T16:20:00",
  "updated_at": "2025-11-22T16:20:00",
  "created_by_username": "johndoe",
  "collaborative_list": null
}
```

#### **3. Get Single Task**
```http
GET /api/tasks/{id}/
Authorization: Token <your-token>
```

**Response:**
```json
{
  "id": 1,
  "title": "Complete Django assignment",
  "description": "Implement REST API endpoints",
  "status": "In Progress",
  "priority": "High",
  "due_datetime": "2025-11-25T23:59:00",
  "created_at": "2025-11-22T10:30:00",
  "updated_at": "2025-11-22T15:45:00",
  "created_by_username": "johndoe",
  "collaborative_list": null
}
```

#### **4. Update Task**
```http
PUT /api/tasks/{id}/
Authorization: Token <your-token>
Content-Type: application/json

{
  "title": "Complete Django assignment",
  "description": "Implement REST API endpoints with documentation",
  "priority": "High",
  "status": "Completed",
  "due_datetime": "2025-11-25T23:59:00"
}
```

**Partial Update:**
```http
PATCH /api/tasks/{id}/
Authorization: Token <your-token>
Content-Type: application/json

{
  "status": "Completed"
}
```

#### **5. Delete Task (Soft Delete)**
```http
DELETE /api/tasks/{id}/
Authorization: Token <your-token>
```

**Response:** `204 No Content`

#### **6. Restore Deleted Task**
```http
POST /api/tasks/{id}/restore/
Authorization: Token <your-token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Complete Django assignment",
  "status": "In Progress",
  "deleted_at": null
}
```

---

### **Collaborative List Endpoints**

#### **1. List Collaborative Lists**
```http
GET /api/collaborative-lists/
Authorization: Token <your-token>
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Team Sprint Tasks",
    "owner": "johndoe",
    "member_usernames": ["janedoe", "bobsmith"],
    "created_at": "2025-11-20T09:00:00",
    "updated_at": "2025-11-22T10:15:00"
  }
]
```

#### **2. Create Collaborative List**
```http
POST /api/collaborative-lists/
Authorization: Token <your-token>
Content-Type: application/json

{
  "name": "Marketing Campaign"
}
```

#### **3. Add Member to List**
```http
POST /api/collaborative-lists/{id}/add_member/
Authorization: Token <your-token>
Content-Type: application/json

{
  "username": "janedoe"
}
```

**Response:**
```json
{
  "message": "Member added successfully",
  "member_usernames": ["janedoe", "bobsmith"]
}
```

#### **4. Remove Member from List**
```http
POST /api/collaborative-lists/{id}/remove_member/
Authorization: Token <your-token>
Content-Type: application/json

{
  "username": "bobsmith"
}
```

---

## 🗄 Database Schema

### **User & Profile**
```python
User (Django built-in)
├── id (PK)
├── username
├── email
├── password (hashed)
├── first_name
└── last_name

Profile
├── id (PK)
├── user_id (FK → User)
├── security_question
├── security_answer
├── created_at
├── updated_at
└── deleted_at (soft delete)
```

### **Tasks**
```python
Task
├── id (PK)
├── title
├── description
├── status (Not Started, In Progress, Completed)
├── priority (High, Mid, Low)
├── due_datetime
├── profile_id (FK → Profile)
├── created_by_id (FK → Profile)
├── collaborative_list_id (FK → CollaborativeList)
├── created_at
├── updated_at
└── deleted_at (soft delete)
```

### **Collaborative Lists**
```python
CollaborativeList
├── id (PK)
├── name
├── owner_id (FK → Profile)
├── members (M2M → Profile)
├── created_at
├── updated_at
└── deleted_at (soft delete)
```
---

## 🔧 Configuration

### **Database Connection**
Located in `JustDoIt/settings.py`:

```python
# SQLite (default)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## 📝 Additional Commands

### **Database Management**
```bash
# Make migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database
python manage.py flush
```

### **Development**
```bash
# Run tests
python manage.py test

# Check for issues
python manage.py check

# Create admin user
python manage.py createsuperuser
```

---

## License

This project is part of CMSC128 coursework.

---

## Authors

**GitHub:** [@sizzlingsisig](https://github.com/sizzlingsisig)
**GitHub:** [@itsShiii16](https://github.com/itsShiii16)


---


