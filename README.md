# Task List API 🚀

A Django REST API for managing tasks, with user authentication and role-based access control.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation & Setup](#installation--setup)
  - [Clone the Repository](#1-clone-the-repository)
  - [Run with Docker](#2-run-with-docker-recommended)
  - [Running Locally](#running-locally-without-docker)
- [API Endpoints](#api-endpoints)
  - [Authentication](#authentication)
  - [Task Management](#task-management)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)
- [Changes & Additions](#changes--additions)

## Features
- User authentication (Signup, Login, Logout)
- JWT-based authentication using `djangorestframework-simplejwt`
- Role-based access control (`Lead` and `Developer`)
- CRUD operations for tasks
- Task assignment to developers
- Automatic timestamp management (created, updated, completed)

## Tech Stack
- **Backend**: Django, Django REST Framework (DRF)
- **Authentication**: JWT (JSON Web Token)
- **Database**: PostgreSQL (via Docker)
- **Containerization**: Docker, Docker Compose
- **Frontend**: Basic HTML templates (for login/signup UI)
- **Testing**: Django `TestCase`, `APIClient`

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/pritom006/TaskListApiDemo.git
cd TaskListApiDemo
```

### 2. Run with Docker (Recommended)
Ensure **Docker** and **Docker Compose** are installed. Then, run:

```bash
docker-compose up --build
```

This will:
- Build the **Django App**
- Start **PostgreSQL** as the database
- Run **Migrations**
- Start the API on `http://127.0.0.1:8000/`

**To stop the container**:
```bash
docker-compose down
```

### Running Locally Without Docker
If you prefer to run it manually:

**1. Create a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # For Mac/Linux
venv\Scripts\activate     # For Windows
```

**2. Install Dependencies**
```bash
pip install -r requirements.txt
```

**3. Apply Migrations**
```bash
python manage.py migrate
```

**4. Create a Superuser (Optional)**
```bash
python manage.py createsuperuser
```

**5. Run the Server**
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/signup/` | Register a new user |
| `POST` | `/login/` | Obtain JWT token |
| `POST` | `/token/refresh/` | Refresh JWT token |
| `POST` | `/logout/` | Logout (Blacklist Token) |

### Task Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/tasks/` | List all tasks (Lead) / Assigned tasks (Developer) |
| `POST` | `/tasks/` | Create a new task (Lead) |
| `GET` | `/tasks/<id>/` | Retrieve task details |
| `PUT` | `/tasks/<id>/` | Update task details |
| `DELETE` | `/tasks/<id>/` | Delete a task |

## Testing
To run unit tests, execute:
```bash
python manage.py test
```

This will run tests for models, serializers, and API views using Django's test framework.

## Project Structure
```
TaskListApiDemo/
│── tasklist/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│── tasks/
│   ├── migrations/
│   ├── templates/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── tests/
│   │   ├── test_models.py
│   │   ├── test_serializers.py
│   │   ├── test_views.py
│── venv/
│── manage.py
│── Dockerfile
│── docker-compose.yml
│── .env
│── README.md
│── requirements.txt
```

## Contributing
Pull requests are welcome! Follow these steps:
1. Fork the repository 🍴
2. Create a new branch `git checkout -b feature-name`
3. Commit your changes `git commit -m "Add feature"`
4. Push the branch `git push origin feature-name`
5. Open a Pull Request ✅

## License
This project is open-source and available under the MIT License.

## Author
Developed by **Pritom**
GitHub: [pritom006](https://github.com/pritom006)

## Changes & Additions
✅ **Docker Support**
- Added docker-compose.yml instructions

✅ **`.env` Configuration**
- Environment variables for database

✅ **Easy Setup**
- Run with just docker-compose up --build

✅ **Project Structure**
- Helps developers navigate the codebase
