# 🚀 Full-Stack FastAPI + React Todo Application

A modern, production-ready Full-Stack Todo Application built with **FastAPI**, **SQLAlchemy 2.0**, **Argon2 Password Hashing**, **JWT Authentication**, and a reactive **React + Vite** frontend.

---

## ✨ Features

- 🔐 **Secure Authentication:** User signup & login using OAuth2 Password Flow & JWT Tokens.
- 🛡️ **Modern Security:** Argon2 password hashing via `pwdlib` (industry-standard, replacing passlib).
- 🗄️ **SQLAlchemy 2.0 ORM:** Modern type-hinted database models with `Mapped` & `mapped_column`.
- 👥 **Role-Based Access Control (RBAC):**
  - **User Role:** View, add, done/undone toggle, and delete their own private todos.
  - **Admin Role:** View all registered users across the platform & manage todos.
- 🌐 **Interactive API Docs:** Auto-generated Swagger UI (`/docs`) & ReDoc (`/redoc`).
- ⚛️ **Modern React Frontend:** Dark-mode glassmorphism UI with real-time state management.

---

## 🛠️ Tech Stack

### Backend
- **Python 3.10+**
- **FastAPI** (`fastapi[standard]`)
- **SQLAlchemy 2.0+** (SQLite ORM)
- **pwdlib[argon2]** (Password Hashing)
- **PyJWT** (JWT Authentication)
- **Pydantic v2** (Data Validation)

### Frontend
- **React 18 / 19**
- **Vite**
- **Vanilla CSS** (Custom Design System with Glassmorphism)

---

## 📁 Project Structure

```text
todo-fastapi/
│
├── .env                  # Environment Variables (SECRET_KEY, ALGORITHM)
├── .gitignore            # Git Ignore rules
├── requirements.txt      # Backend Python dependencies
│
├── database.py           # Database connection & session factory
├── models.py             # SQLAlchemy 2.0 database tables (User, Todo)
├── schemas.py            # Pydantic validation schemas
├── security.py           # Password hashing (Argon2) & JWT logic
├── main.py               # FastAPI application & API endpoints
├── make_admin.py         # CLI script to promote any user to Admin
│
└── frontend/             # React + Vite Frontend Application
    ├── src/
    │   ├── App.jsx       # Main React Component
    │   ├── App.css       # Glassmorphism & layout styles
    │   └── index.css     # Global theme & typography
    ├── package.json      # React dependencies
    └── vite.config.js    # Vite configuration
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd todo-fastapi
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Mac / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI backend
fastapi dev main.py
```
- Backend will start at: `http://127.0.0.1:8000`
- Swagger Docs: `http://127.0.0.1:8000/docs`

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
- Frontend will start at: `http://localhost:5173`

---

## 👑 Promoting a User to Admin
```bash
python make_admin.py <username>
```

---

## 📜 License
MIT License. Free for learning and building!
