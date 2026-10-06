# 🚀 Full-Stack FastAPI + React Todo Application (Dockerized)

A modern, production-grade Full-Stack Todo Application with Role-Based Access Control (RBAC), built with **FastAPI**, **SQLAlchemy 2.0**, **Argon2 Password Hashing**, **JWT Authentication**, a responsive **React (Vite)** frontend, and containerized with **Docker & Docker Compose**.

---

## 🌟 Key Features

- 🔐 **Secure JWT Authentication:** OAuth2 password flow with secure Bearer tokens.
- 🛡️ **Modern Security:** Argon2 password hashing using `pwdlib[argon2]` (industry best practice).
- 🗄️ **SQLAlchemy 2.0 ORM:** Type-safe database models using `Mapped` & `mapped_column` with SQLite.
- 👥 **Role-Based Access Control (RBAC):**
  - **User Role:** Create, view, toggle status, and delete their own private todos.
  - **Admin Role:** View all registered users across the platform & manage todos.
- 🌐 **Auto-Generated API Docs:** Interactive Swagger UI (`/docs`) & ReDoc (`/redoc`).
- ⚛️ **Modern React Frontend:** Dark-mode glassmorphism UI with real-time state management.
- 🐳 **Dockerized Setup:** Single-command startup (`docker compose up --build`) for both backend & frontend.

---

## 🛠️ Tech Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Uvicorn |
| **Security** | `pwdlib[argon2]` (Password Hashing), `PyJWT` (Access Tokens), `python-dotenv` |
| **Database** | SQLite (Relational ORM) |
| **Frontend** | React 19, Vite, Vanilla CSS (Glassmorphism & Responsive Design) |
| **DevOps** | Docker, Docker Compose, Git & GitHub |

---

## 📁 Project Structure

```text
todo-fastapi/
│
├── .dockerignore           # Docker build ignore rules
├── .env                    # Environment variables (SECRET_KEY, ALGORITHM)
├── .gitignore              # Git ignore rules (secrets, venv, node_modules)
├── Dockerfile              # Backend Docker container definition
├── docker-compose.yml      # Multi-container orchestration (Backend + Frontend)
├── requirements.txt        # Python backend dependencies
│
├── database.py             # Database engine, session factory & dependency (get_db)
├── models.py               # SQLAlchemy 2.0 tables (User & Todo models)
├── schemas.py              # Pydantic v2 schemas for request validation & response filtering
├── security.py             # Argon2 password hashing, JWT token generation & auth dependency
├── main.py                 # FastAPI application routes, CORS, CRUD operations & Admin APIs
├── make_admin.py           # Helper CLI script to promote any user to Admin
│
└── frontend/               # React + Vite Frontend Application
    ├── Dockerfile          # Frontend Docker container definition
    ├── .dockerignore       # Frontend Docker ignore rules
    ├── index.html          # HTML entry point (Google Fonts integration)
    ├── package.json        # Frontend dependencies
    ├── vite.config.js      # Vite configuration
    └── src/
        ├── App.jsx         # Main React application component (Auth, Todos, Admin)
        ├── App.css         # Glassmorphism & responsive UI styling
        ├── index.css       # Core design tokens & gradient background
        └── main.jsx        # React root mounting
```

---

## 🚀 Running the Project

### Option A: Using Docker (Recommended 🐳)

Make sure [Docker Desktop](https://www.docker.com/products/docker-desktop/) is installed and running, then run:

```bash
docker compose up --build
```

- **React Frontend:** 👉 [http://localhost:5173](http://localhost:5173)
- **FastAPI Backend:** 👉 [http://localhost:8000](http://localhost:8000)
- **Swagger Interactive API Docs:** 👉 [http://localhost:8000/docs](http://localhost:8000/docs)

To stop containers:
```bash
docker compose down
```

---

### Option B: Running Locally (Without Docker)

#### 1. Backend Setup:
```bash
# Navigate to project folder
cd todo-fastapi

# Create and activate virtual environment
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Mac / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend server
fastapi dev main.py
```

#### 2. Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```

---

## 👑 Promoting a User to Admin

By default, all signups are assigned the `user` role for security. To promote any user to `admin`:

```bash
# Local:
python make_admin.py <username>

# Inside Docker:
docker exec -it fastapi_backend python make_admin.py <username>
```

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/signup` | Register a new user account | No |
| `POST` | `/login` | Authenticate and get JWT Bearer token | No |
| `GET` | `/me` | Get profile of currently logged-in user | Yes (Bearer) |
| `GET` | `/todos` | Get all todos for current user | Yes (Bearer) |
| `POST` | `/todos` | Create a new todo item | Yes (Bearer) |
| `PATCH` | `/todos/{id}` | Toggle todo status (Done / Undone) | Yes (Owner only) |
| `DELETE` | `/todos/{id}` | Delete a todo item | Yes (Owner / Admin) |
| `GET` | `/admin/users` | List all registered users | Yes (Admin only) |

---

## 📄 License
MIT License. Built for learning and building production-ready FastAPI applications!
