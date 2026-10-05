import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = "http://127.0.0.1:8000";

function App() {
  // Auth states
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [user, setUser] = useState(null);
  const [isSignup, setIsSignup] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  // Todos state
  const [todos, setTodos] = useState([]);
  const [newTitle, setNewTitle] = useState("");

  // Admin users state
  const [adminUsers, setAdminUsers] = useState([]);

  // Alert banner state
  const [alert, setAlert] = useState(null);

  // Show Alert
  const showAlert = (msg, isError = true) => {
    setAlert({ msg, isError });
    setTimeout(() => setAlert(null), 4000);
  };

  // Fetch Current Logged-in User
  const fetchMe = async (authToken) => {
    try {
      const res = await fetch(`${API_URL}/me`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      if (!res.ok) throw new Error("Session expired");
      const data = await res.json();
      setUser(data);
      if (data.role === "admin") {
        fetchAdminUsers(authToken);
      }
    } catch {
      handleLogout();
    }
  };

  // Fetch Todos
  const fetchTodos = async (authToken) => {
    try {
      const res = await fetch(`${API_URL}/todos`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      if (res.ok) {
        const data = await res.json();
        setTodos(data);
      }
    } catch {
      showAlert("Failed to load todos");
    }
  };

  // Fetch Admin Users List
  const fetchAdminUsers = async (authToken) => {
    try {
      const res = await fetch(`${API_URL}/admin/users`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      if (res.ok) {
        const data = await res.json();
        setAdminUsers(data);
      }
    } catch {}
  };

  // On component mount or token change
  useEffect(() => {
    if (token) {
      fetchMe(token);
      fetchTodos(token);
    } else {
      setUser(null);
      setTodos([]);
    }
  }, [token]);

  // Auth Handler (Login / Signup)
  const handleAuth = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password) return;

    if (isSignup) {
      // Signup (JSON)
      try {
        const res = await fetch(`${API_URL}/signup`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Signup failed");

        showAlert("Account created successfully! Please login.", false);
        setIsSignup(false);
        setPassword("");
      } catch (err) {
        showAlert(err.message);
      }
    } else {
      // Login (OAuth2 Form Data)
      try {
        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);

        const res = await fetch(`${API_URL}/login`, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: formData
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Login failed");

        localStorage.setItem("token", data.access_token);
        setToken(data.access_token);
        setUsername("");
        setPassword("");
        showAlert("Logged in successfully!", false);
      } catch (err) {
        showAlert(err.message);
      }
    }
  };

  // Add Todo
  const handleAddTodo = async (e) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    try {
      const res = await fetch(`${API_URL}/todos`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ title: newTitle.trim() })
      });
      if (!res.ok) throw new Error("Failed to add todo");
      setNewTitle("");
      fetchTodos(token);
    } catch (err) {
      showAlert(err.message);
    }
  };

  // Toggle Todo Done Status
  const handleToggleTodo = async (id) => {
    try {
      const res = await fetch(`${API_URL}/todos/${id}`, {
        method: "PATCH",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to update status");
      fetchTodos(token);
    } catch (err) {
      showAlert(err.message);
    }
  };

  // Delete Todo
  const handleDeleteTodo = async (id) => {
    try {
      const res = await fetch(`${API_URL}/todos/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to delete todo");
      fetchTodos(token);
    } catch (err) {
      showAlert(err.message);
    }
  };

  // Logout
  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken("");
    setUser(null);
    showAlert("Logged out successfully", false);
  };

  return (
    <div className="container">
      {/* Alert Notification */}
      {alert && (
        <div className={`alert ${alert.isError ? "alert-error" : "alert-success"}`}>
          {alert.msg}
        </div>
      )}

      {/* Auth View (Login / Signup) */}
      {!token ? (
        <div className="card">
          <h1>{isSignup ? "Create Account" : "Welcome Back"}</h1>
          <p className="subtitle">
            {isSignup
              ? "Sign up to start organizing todos"
              : "Enter your credentials to continue"}
          </p>

          <form onSubmit={handleAuth}>
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                placeholder="e.g. rahul123"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="btn">
              {isSignup ? "Sign Up" : "Login"}
            </button>
          </form>

          <div className="switch-link">
            {isSignup ? "Already have an account?" : "Don't have an account?"}
            <button type="button" onClick={() => setIsSignup(!isSignup)}>
              {isSignup ? "Login" : "Sign up"}
            </button>
          </div>
        </div>
      ) : (
        /* Dashboard View */
        <div className="card">
          <div className="app-header">
            <div>
              <div style={{ fontWeight: 700, fontSize: "18px" }}>
                Hi, {user ? user.username : "User"}
              </div>
              <span
                className={`user-badge ${
                  user?.role === "admin" ? "admin-badge" : ""
                }`}
              >
                {user ? user.role.toUpperCase() : "USER"}
              </span>
            </div>
            <button className="btn btn-danger" onClick={handleLogout}>
              Logout
            </button>
          </div>

          {/* Add Todo Form */}
          <form className="todo-input-row" onSubmit={handleAddTodo}>
            <input
              type="text"
              placeholder="What needs to be done?"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              required
            />
            <button type="submit" className="btn">
              Add
            </button>
          </form>

          {/* Todo List */}
          <ul className="todo-list">
            {todos.length === 0 ? (
              <li
                style={{
                  textAlign: "center",
                  color: "var(--text-muted)",
                  fontSize: "14px",
                  padding: "20px 0"
                }}
              >
                No todos yet. Add one above! ✨
              </li>
            ) : (
              todos.map((todo) => (
                <li key={todo.id} className="todo-item">
                  <div className="todo-left">
                    <input
                      type="checkbox"
                      checked={todo.is_done}
                      onChange={() => handleToggleTodo(todo.id)}
                    />
                    <span className={`todo-text ${todo.is_done ? "done" : ""}`}>
                      {todo.title}
                    </span>
                  </div>
                  <button
                    className="btn btn-danger"
                    onClick={() => handleDeleteTodo(todo.id)}
                  >
                    Delete
                  </button>
                </li>
              ))
            )}
          </ul>

          {/* Admin Section */}
          {user?.role === "admin" && (
            <div className="admin-card">
              <div className="admin-card-header">
                <h3 style={{ fontSize: "15px", margin: 0 }}>
                  👑 Admin Panel: All Users
                </h3>
                <button
                  className="btn btn-secondary"
                  onClick={() => fetchAdminUsers(token)}
                >
                  Refresh
                </button>
              </div>
              <ul className="users-list">
                {adminUsers.map((u) => (
                  <li key={u.id}>
                    <span>
                      <strong>#{u.id}</strong> {u.username}
                    </span>
                    <span>
                      Role: <em>{u.role}</em>
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
