# 🚀 Full-Stack AI Todo Application (FastAPI + LangChain + React + Docker)

A modern, production-grade Full-Stack Todo Application with Role-Based Access Control (RBAC) and **Multilingual AI Superpowers (English, Hindi, Hinglish)**. Built with **FastAPI**, **LangChain**, **Groq LLM**, **SQLAlchemy 2.0**, **Argon2 Password Hashing**, **JWT Authentication**, a sleek **React 19 (Vite)** glassmorphism UI, and containerized with **Docker & Docker Compose**.

---

## 🌟 Key Features

### 🤖 Multilingual AI Superpowers (LangChain + Groq)
- **Natural Language Task Extraction:** Speak or type tasks naturally in English, Hindi (Devanagari), or Hinglish (e.g., *"Kal shaam 6 baje gym jana hai"* or *"Submit project report tomorrow at 5 PM"*) — AI parses the intent and creates a concise, structured task.
- **📊 AI Task Summary:** Instant, structured status updates with progress tracking, emojis, and motivational coaching.
- **🎯 Smart Priority Suggestions:** Categorizes pending tasks into High, Medium, and Low priorities with clear actionable reasoning.

### 🔐 Security & Role-Based Access Control (RBAC)
- **JWT Authentication:** Secure OAuth2 password flow with signed access tokens.
- **Argon2 Password Hashing:** Modern, secure password hashing using `pwdlib[argon2]` (industry best practice).
- **User Role:** Create, view, complete, and delete personal private todos.
- **Admin Role:** View all registered platform users and manage system tasks.

### 🗄️ Robust Backend & Database
- **SQLAlchemy 2.0 ORM:** Modern type-safe models using `Mapped` & `mapped_column`.
- **SQLite Database:** Local relational persistence with foreign keys and cascade deletions.
- **Interactive API Docs:** Auto-generated Swagger UI (`/docs`) & ReDoc (`/redoc`).

### 🎨 Modern React Frontend
- **Dark Glassmorphism UI:** Tailored color palette, frosted glass styling, and smooth micro-animations.
- **Real-Time State:** Instant optimistic updates for task toggling, adding, and deletion.
- **Responsive Layout:** Optimized for mobile, tablet, and desktop viewports.

### 🐳 DevOps & Containerization
- **Docker & Docker Compose:** One-command startup for both backend and frontend.
- **Hot Reloading:** Live volume mounting for frictionless development.

---

## 🛠️ Tech Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Uvicorn |
| **AI / LLM** | LangChain, LangChain-Groq (`qwen/qwen3.8-27b`) |
| **Security** | `pwdlib[argon2]` (Password Hashing), `PyJWT` (Access Tokens), `python-dotenv` |
| **Database** | SQLite (Relational ORM) |
| **Frontend** | React 19, Vite, Vanilla CSS (Glassmorphism & Responsive Design) |
| **DevOps** | Docker, Docker Compose, Git & GitHub |

---

## 📁 Project Structure

```text
todo-fastapi/
│
├── .dockerignore           # Root Docker ignore rules
├── .env                    # Environment variables (SECRET_KEY, GROQ_API_KEY)
├── .gitignore              # Git ignore rules (secrets, venv, node_modules, db)
├── Dockerfile              # Backend Docker container definition
├── docker-compose.yml      # Multi-container orchestration (Backend + Frontend)
├── requirements.txt        # Python backend dependencies
│
├── ai_service.py           # LangChain + Groq AI logic (Summary, Priorities, Natural Add)
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
        ├── App.jsx         # Main React application component (Auth, Todos, AI, Admin)
        ├── App.css         # Glassmorphism & responsive UI styling
        ├── index.css       # Core design tokens & gradient background
        └── main.jsx        # React root mounting
```

---

## 🚀 Running the Project

### Option A: Using Docker (Recommended 🐳)

Make sure [Docker Desktop](https://www.docker.com/products/docker-desktop/) is installed and running, then:

1. **Configure Environment Variables:**
   Create a `.env` file in the root folder (or ensure existing values):
   ```env
   SECRET_KEY=your_super_secret_jwt_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   GROQ_API_KEY=your_groq_api_key_here
   ```

2. **Start Containers:**
   ```bash
   docker compose up --build
   ```

3. **Access Services:**
   - 🌐 **React Frontend:** [http://localhost:5173](http://localhost:5173)
   - ⚙️ **FastAPI Backend:** [http://localhost:8000](http://localhost:8000)
   - 📖 **Interactive API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

4. **Stop Containers:**
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
| `POST` | `/ai/summary` | AI-generated status summary of user tasks | Yes (Bearer) |
| `POST` | `/ai/priorities` | AI prioritized task recommendations | Yes (Bearer) |
| `POST` | `/ai/natural-add` | Extract task title from natural language prompt | Yes (Bearer) |
| `GET` | `/admin/users` | List all registered users | Yes (Admin only) |

---

## 📄 License
MIT License. Built for building production-ready FastAPI + React + AI applications!
