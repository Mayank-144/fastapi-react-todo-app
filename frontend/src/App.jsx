import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = "http://localhost:8000";

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
  const [naturalPrompt, setNaturalPrompt] = useState("");

  // AI states
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState(null); // { title: "", text: "" }

  // Admin users state
  const [adminUsers, setAdminUsers] = useState([]);

  // Alert state
  const [alert, setAlert] = useState(null);

  const showAlert = (msg, isError = true) => {
    setAlert({ msg, isError });
    setTimeout(() => setAlert(null), 4000);
  };

  // Fetch Current User
  const fetchMe = async (authToken) => {
    try {
      const res = await fetch(`${API_URL}/me`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      if (!res.ok) throw new Error("Session expired");
      const data = await res.json();
      setUser(data);
      if (data.role === "admin") fetchAdminUsers(authToken);
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

  // Fetch Admin Users
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

  useEffect(() => {
    if (token) {
      fetchMe(token);
      fetchTodos(token);
    } else {
      setUser(null);
      setTodos([]);
    }
  }, [token]);

  // Auth Handler
  const handleAuth = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password) return;

    if (isSignup) {
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

  // Regular Add Todo
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

  // ==========================================
  // AI FEATURE 1: Natural Language Task Add
  // ==========================================
  const handleAINaturalAdd = async (e) => {
    e.preventDefault();
    if (!naturalPrompt.trim()) return;

    setAiLoading(true);
    try {
      const res = await fetch(`${API_URL}/ai/natural-add`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ prompt: naturalPrompt })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "AI parsing failed");
      
      setNaturalPrompt("");
      showAlert(`✨ AI Created Task: "${data.title}"`, false);
      fetchTodos(token);
    } catch (err) {
      showAlert(err.message);
    } finally {
      setAiLoading(false);
    }
  };

  // ==========================================
  // AI FEATURE 2: Summary
  // ==========================================
  const handleAISummary = async () => {
    setAiLoading(true);
    try {
      const res = await fetch(`${API_URL}/ai/summary`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      if (!res.ok) throw new Error("Failed to get AI summary");
      setAiResult({ title: "📊 AI Task Summary", text: data.summary });
    } catch (err) {
      showAlert(err.message);
    } finally {
      setAiLoading(false);
    }
  };

  // ==========================================
  // AI FEATURE 3: Priorities
  // ==========================================
  const handleAIPriorities = async () => {
    setAiLoading(true);
    try {
      const res = await fetch(`${API_URL}/ai/priorities`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      if (!res.ok) throw new Error("Failed to get priorities");
      setAiResult({ title: "🎯 Smart Priority Suggestions", text: data.priorities });
    } catch (err) {
      showAlert(err.message);
    } finally {
      setAiLoading(false);
    }
  };

  // Toggle Todo Done
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
    setAiResult(null);
    showAlert("Logged out successfully", false);
  };

  const pendingCount = todos.filter(t => !t.is_done).length;
  const completedCount = todos.filter(t => t.is_done).length;

  return (
    <div className="container">
      {alert && (
        <div className={`alert ${alert.isError ? "alert-error" : "alert-success"}`}>
          <span>{alert.isError ? "⚠️" : "✅"}</span>
          <span>{alert.msg}</span>
        </div>
      )}

      {!token ? (
        <div className="card auth-box">
          <h1>{isSignup ? "Create Account" : "Welcome Back"}</h1>
          <p className="subtitle">
            {isSignup ? "Sign up to start organizing tasks with AI" : "Enter your credentials to continue"}
          </p>

          <form onSubmit={handleAuth}>
            <div className="form-group">
              <label htmlFor="username">Email / Username</label>
              <input
                id="username"
                type="text"
                placeholder="e.g. rahul@example.com"
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

            <button type="submit" className="btn btn-full">
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
        <div className="card">
          {/* HEADER */}
          <div className="app-header">
            <div className="user-profile">
              <div className="user-avatar">
                {user?.username ? user.username.charAt(0).toUpperCase() : "U"}
              </div>
              <div>
                <div className="user-name">
                  {user ? user.username : "User"}
                  <span className={`user-badge ${user?.role === "admin" ? "admin-badge" : ""}`}>
                    {user ? user.role.toUpperCase() : "USER"}
                  </span>
                </div>
              </div>
            </div>
            <button className="btn btn-danger" onClick={handleLogout}>
              Logout
            </button>
          </div>

          {/* AI SUPERPOWERS SECTION */}
          <div className="ai-section">
            <div className="ai-section-title">
              <span>🤖</span> LangChain AI Assistant
            </div>

            <div className="ai-toolbar">
              <button className="btn-ai-action" onClick={handleAISummary} disabled={aiLoading}>
                <span>📊</span> AI Task Summary
              </button>
              <button className="btn-ai-action" onClick={handleAIPriorities} disabled={aiLoading}>
                <span>🎯</span> Priority Suggestions
              </button>
            </div>

            {/* NATURAL LANGUAGE TASK ADD */}
            <form className="ai-natural-box" onSubmit={handleAINaturalAdd}>
              <input
                type="text"
                placeholder="✨ Add in natural language (e.g. 'Kal shaam 6 baje gym jana hai')"
                value={naturalPrompt}
                onChange={(e) => setNaturalPrompt(e.target.value)}
                disabled={aiLoading}
              />
              <button type="submit" className="btn-ai-gradient" disabled={aiLoading}>
                {aiLoading ? "Thinking..." : "✨ AI Add"}
              </button>
            </form>

            {/* AI RESULT DISPLAY CARD */}
            {aiResult && (
              <div className="ai-result-card">
                <div className="ai-result-header">
                  <div className="ai-result-title">{aiResult.title}</div>
                  <button className="ai-close-btn" onClick={() => setAiResult(null)} title="Close">
                    ✕
                  </button>
                </div>
                <div className="ai-result-body">{aiResult.text}</div>
              </div>
            )}
          </div>

          {/* STANDARD TODO SECTION */}
          <div className="section-divider">
            <span className="section-label">📋 My Tasks</span>
            <span className="todo-counter">
              {pendingCount} Pending • {completedCount} Done
            </span>
          </div>

          <form className="todo-input-row" onSubmit={handleAddTodo}>
            <input
              type="text"
              placeholder="What needs to be done?"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              required
            />
            <button type="submit" className="btn">
              Add Task
            </button>
          </form>

          {/* TODOS LIST */}
          <ul className="todo-list">
            {todos.length === 0 ? (
              <li className="empty-state">
                No tasks yet! Add one above or use the AI Assistant ✨
              </li>
            ) : (
              todos.map((todo) => (
                <li key={todo.id} className="todo-item">
                  <div className="todo-left">
                    <input
                      type="checkbox"
                      className="todo-checkbox"
                      checked={todo.is_done}
                      onChange={() => handleToggleTodo(todo.id)}
                    />
                    <span className={`todo-text ${todo.is_done ? "done" : ""}`}>
                      {todo.title}
                    </span>
                  </div>
                  <button className="btn btn-danger" onClick={() => handleDeleteTodo(todo.id)}>
                    Delete
                  </button>
                </li>
              ))
            )}
          </ul>

          {/* ADMIN ONLY PANEL */}
          {user?.role === "admin" && (
            <div className="admin-card">
              <div className="admin-card-header">
                <h3 style={{ fontSize: "15px", margin: 0 }}>👑 Admin Panel: Registered Users</h3>
                <button className="btn btn-secondary" onClick={() => fetchAdminUsers(token)}>
                  Refresh
                </button>
              </div>
              <ul className="users-list">
                {adminUsers.map((u) => (
                  <li key={u.id}>
                    <span><strong>#{u.id}</strong> {u.username}</span>
                    <span>Role: <em>{u.role}</em></span>
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
