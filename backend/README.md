## JUST DO IT - To Do List
**Frontend stack**
- HTML
- Javascript
- Tailwind CSS
  
**Backend stack**
- Django
  - Django REST Framework
  - django-softdelete
- SQLite

**Installation and Setup**
1. Clone the repository
```
git clone <your-repo-url>
cd JustDoIt
```
2. Create and activate environment

```
python -m venv venv
#must be activated before server can be ran
source venv/bin/activate # Bash/Linux/Mac
venv\Scripts\activate # Windows
```
3. Install dependencies
```
pip install Django
pip install django-softdelete
pip install djangorestframework
```
4. Apply migrations
```
python manage.py migrate
```
5. Run development server
```
python manage.py runserver
```

**API Endpoints**
| Method   | Endpoint                   | Description                           |
| -------- | -------------------------- | ------------------------------------- |
| `GET`    | `/api/tasks/`              | List all active tasks                 |
| `GET`    | `/api/tasks/?deleted=true` | List all tasks including soft-deleted |
| `POST`   | `/api/tasks/`              | Create a new task                     |
| `GET`    | `/api/tasks/<id>/`         | Retrieve a task by ID                 |
| `PUT`    | `/api/tasks/<id>/`         | Update a task                         |
| `DELETE` | `/api/tasks/<id>/`         | Soft delete a task                    |
| `POST`   | `/api/tasks/<id>/restore/` | Restore a soft-deleted task           |

**Example API Usage**

Create or Update Task Parameters
```
POST/api/tasks/ or PUT/api/tasks/{id}/
{
  "title": "Finish assignment",
  "description": "Complete Django REST Framework tutorial",
  "priority": "High",
  "status": "Not Started"
}
```

Get Tasks
```
GET/api/tasks/
```
Get Tasks with trashed
```
GET/api/tasks/?deleted=true
```
Show Task 
```
GET/api/tasks/{id}/
```
Delete Task
```
DELETE /api/tasks/1/
```
Restore Task
```
POST/api/tasks/<id>/restore/
```


