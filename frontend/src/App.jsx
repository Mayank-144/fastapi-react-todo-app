import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const API_URL = "http://localhost:8000";

function App() {
  // Authentication states
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [user, setUser] = useState(null);
  const [isSignup, setIsSignup] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  // Todos state
  const [todos, setTodos] = useState([]);
  const [newTitle, setNewTitle] = useState("");
  const [naturalPrompt, setNaturalPrompt] = useState("");

  // AI states (LCEL Quick Actions)
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState(null); // { title: "", text: "" }

  // AI Agent Chat states
  const [activeTab, setActiveTab] = useState("agent"); // "agent" | "quick"
  const [chatMessages, setChatMessages] = useState([
    {
      id: "init-1",
      role: "assistant",
      content: "Hello! 👋 I am your LangChain AI Agent. I can check live weather around the world 🌤, manage and add tasks to your list 📝, summarize your progress 📊, or suggest priority recommendations 🎯 in English, Hindi, or Hinglish.\n\nHow can I help you today?",
      tools_used: []
    }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatBottomRef = useRef(null);

  // Admin users state
  const [adminUsers, setAdminUsers] = useState([]);

  // Alert notification state
  const [alert, setAlert] = useState(null);

  const showAlert = (msg, isError = true) => {
    setAlert({ msg, isError });
    setTimeout(() => setAlert(null), 4000);
  };

  // Scroll to bottom of chat
  useEffect(() => {
    if (activeTab === "agent") {
      chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatMessages, chatLoading, activeTab]);

  // Logout & Clear all session state
  const handleLogout = (notify = false) => {
    localStorage.removeItem("token");
    setToken("");
    setUser(null);
    setTodos([]);
    setAdminUsers([]);
    setAiResult(null);
    setChatMessages([
      {
        id: "init-1",
        role: "assistant",
        content: "Hello! 👋 I am your LangChain AI Agent. I can check live weather around the world 🌤, manage and add tasks to your list 📝, summarize your progress 📊, or suggest priority recommendations 🎯 in English, Hindi, or Hinglish.\n\nHow can I help you today?",
        tools_used: []
      }
    ]);
    if (notify) showAlert("Logged out successfully", false);
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

  // Fetch Registered Users for Admin
  const fetchAdminUsers = async (authToken) => {
    try {
      const res = await fetch(`${API_URL}/admin/users`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      if (res.ok) {
        const data = await res.json();
        setAdminUsers(data);
      }
    } catch {
      showAlert("Failed to load admin user list");
    }
  };

  useEffect(() => {
    if (!token) return;

    let isMounted = true;

    const loadInitialData = async () => {
      try {
        const [meRes, todosRes] = await Promise.all([
          fetch(`${API_URL}/me`, { headers: { Authorization: `Bearer ${token}` } }),
          fetch(`${API_URL}/todos`, { headers: { Authorization: `Bearer ${token}` } })
        ]);

        if (!meRes.ok) {
          handleLogout(false);
          return;
        }

        const userData = await meRes.json();
        if (isMounted) setUser(userData);

        if (todosRes.ok) {
          const todosData = await todosRes.json();
          if (isMounted) setTodos(todosData);
        }

        if (userData.role === "admin") {
          const adminRes = await fetch(`${API_URL}/admin/users`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          if (adminRes.ok && isMounted) {
            const adminData = await adminRes.json();
            setAdminUsers(adminData);
          }
        }
      } catch {
        if (isMounted) showAlert("Failed to connect to server");
      }
    };

    loadInitialData();

    return () => {
      isMounted = false;
    };
  }, [token]);

  // Handle Login & Signup
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

  // Standard Task Creation
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
  // AI AGENT CHAT HANDLER
  // ==========================================
  const handleSendChat = async (messageText = null) => {
    const textToSend = messageText || chatInput;
    if (!textToSend.trim() || chatLoading) return;

    const userMsg = {
      id: Date.now().toString(),
      role: "user",
      content: textToSend.trim(),
      tools_used: []
    };

    setChatMessages((prev) => [...prev, userMsg]);
    setChatInput("");
    setChatLoading(true);

    try {
      // Build history for context (last 6 messages)
      const historyPayload = chatMessages.slice(-6).map((m) => ({
        role: m.role,
        content: m.content
      }));

      const res = await fetch(`${API_URL}/ai/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          message: textToSend.trim(),
          history: historyPayload
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Agent chat failed");

      const assistantMsg = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.reply,
        tools_used: data.tools_used || []
      };

      setChatMessages((prev) => [...prev, assistantMsg]);

      // If the agent created new tasks, refresh the task list immediately!
      if (data.created_tasks && data.created_tasks.length > 0) {
        fetchTodos(token);
        showAlert(`✨ Agent added ${data.created_tasks.length} task(s) to your list!`, false);
      }
    } catch (err) {
      const errorMsg = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `⚠️ Error: ${err.message}`,
        tools_used: []
      };
      setChatMessages((prev) => [...prev, errorMsg]);
    } finally {
      setChatLoading(false);
    }
  };

  // ==========================================
  // AI LCEL Feature 1: Multilingual Natural Language Task Add
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
  // AI LCEL Feature 2: Task Summary
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
  // AI LCEL Feature 3: Smart Priority Suggestions
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

  // Toggle Todo Completion
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
            {isSignup ? "Sign up to organize tasks with multilingual AI" : "Enter your credentials to continue"}
          </p>

          <form onSubmit={handleAuth}>
            <div className="form-group">
              <label htmlFor="username">Email / Username</label>
              <input
                id="username"
                type="text"
                placeholder="e.g. user@example.com"
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
            <button className="btn btn-danger" onClick={() => handleLogout(true)}>
              Logout
            </button>
          </div>

          {/* AI AGENT & ACTIONS CONTAINER */}
          <div className="ai-section">
            {/* TAB SELECTOR */}
            <div className="ai-tabs">
              <button
                type="button"
                className={`ai-tab-btn ${activeTab === "agent" ? "active" : ""}`}
                onClick={() => setActiveTab("agent")}
              >
                💬 LangChain Agent (Chat & Weather)
              </button>
              <button
                type="button"
                className={`ai-tab-btn ${activeTab === "quick" ? "active" : ""}`}
                onClick={() => setActiveTab("quick")}
              >
                ⚡ Quick LCEL Tools
              </button>
            </div>

            {/* TAB 1: INTERACTIVE AI AGENT CHAT */}
            {activeTab === "agent" && (
              <div className="agent-chat-container">
                {/* QUICK PROMPT SUGGESTION PILLS */}
                <div className="quick-prompts-bar">
                  <button
                    type="button"
                    className="prompt-pill"
                    onClick={() => handleSendChat("What is the weather in Delhi?")}
                  >
                    🌤 Weather in Delhi
                  </button>
                  <button
                    type="button"
                    className="prompt-pill"
                    onClick={() => handleSendChat("What's the weather in London?")}
                  >
                    🌧 London Weather
                  </button>
                  <button
                    type="button"
                    className="prompt-pill"
                    onClick={() => handleSendChat("Summarize my current tasks and progress")}
                  >
                    📊 Task Summary
                  </button>
                  <button
                    type="button"
                    className="prompt-pill"
                    onClick={() => handleSendChat("Suggest task priorities for my pending items")}
                  >
                    🎯 Priority Advice
                  </button>
                </div>

                {/* CHAT MESSAGES WINDOW */}
                <div className="chat-messages-box">
                  {chatMessages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`chat-message-row ${msg.role === "user" ? "user-row" : "assistant-row"}`}
                    >
                      <div className="chat-avatar">
                        {msg.role === "user" ? "👤" : "🤖"}
                      </div>
                      <div className={`chat-bubble ${msg.role === "user" ? "user-bubble" : "assistant-bubble"}`}>
                        {msg.tools_used && msg.tools_used.length > 0 && (
                          <div className="tools-badge-container">
                            {msg.tools_used.map((tool, idx) => (
                              <span key={idx} className="tool-badge">
                                ⚙️ {tool}
                              </span>
                            ))}
                          </div>
                        )}
                        <div className="chat-content">{msg.content}</div>
                      </div>
                    </div>
                  ))}
                  {chatLoading && (
                    <div className="chat-message-row assistant-row">
                      <div className="chat-avatar">🤖</div>
                      <div className="chat-bubble assistant-bubble thinking-bubble">
                        <span className="dot-pulse"></span>
                        <span style={{ marginLeft: "8px", fontSize: "13px", color: "var(--text-muted)" }}>
                          Agent is thinking & running tools...
                        </span>
                      </div>
                    </div>
                  )}
                  <div ref={chatBottomRef} />
                </div>

                {/* CHAT INPUT BAR */}
                <form
                  className="chat-input-form"
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSendChat();
                  }}
                >
                  <input
                    type="text"
                    placeholder="Ask about weather, add tasks, or request summaries (English, Hindi, Hinglish)..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    disabled={chatLoading}
                  />
                  <button
                    type="submit"
                    className="btn btn-ai-send"
                    disabled={chatLoading || !chatInput.trim()}
                  >
                    {chatLoading ? "⏳" : "Send 🚀"}
                  </button>
                </form>
              </div>
            )}

            {/* TAB 2: QUICK LCEL TOOLS */}
            {activeTab === "quick" && (
              <div className="quick-lcel-container">
                <div className="ai-toolbar">
                  <button className="btn-ai-action" onClick={handleAISummary} disabled={aiLoading}>
                    <span>📊</span> AI Task Summary
                  </button>
                  <button className="btn-ai-action" onClick={handleAIPriorities} disabled={aiLoading}>
                    <span>🎯</span> Priority Suggestions
                  </button>
                </div>

                {/* MULTILINGUAL NATURAL LANGUAGE TASK ADD */}
                <form className="ai-natural-box" onSubmit={handleAINaturalAdd}>
                  <input
                    type="text"
                    placeholder="✨ Add in English, Hindi, or Hinglish (e.g. 'Gym at 6 PM' or 'Kal shaam 6 baje gym jana')"
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
                No tasks yet! Add one above or tell the AI Agent ✨
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
